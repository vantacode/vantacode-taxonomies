#!/usr/bin/env python3
# Copyright (c) DarkCode LLC. All rights reserved.
# SPDX-License-Identifier: BSD-2-Clause
# Contact: cory@darkcode.ai
"""
Validate all taxonomy, galaxy, and cluster JSON files against their schemas.

Checks:
  - Schema compliance (jsonschema)
  - Duplicate values within predicates/entries
  - Missing required fields
  - Orphaned predicates (values reference a predicate not in predicates[])
  - Valid UUID format
  - Cluster type matches galaxy type

Exits non-zero on any failure (CI compatible).
"""

import json
import os
import re
import sys
from pathlib import Path

try:
    import jsonschema
except ImportError:
    print("\033[91mERROR: jsonschema not installed. Run: pip install jsonschema\033[0m")
    sys.exit(1)


# ANSI color codes
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RESET = "\033[0m"
BOLD = "\033[1m"

UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.IGNORECASE
)


def find_repo_root():
    """Walk up from this script's location to find the repo root (contains MANIFEST.json)."""
    here = Path(__file__).resolve().parent
    for candidate in [here.parent, here.parent.parent, here]:
        if (candidate / "MANIFEST.json").exists():
            return candidate
    # Fallback: assume script is in tools/ under repo root
    return here.parent


def load_json(path):
    """Load and return parsed JSON from a file path."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def validate_uuids(data, path, errors):
    """Recursively find any 'uuid' fields and validate format."""
    if isinstance(data, dict):
        for key, value in data.items():
            if key == "uuid" and isinstance(value, str):
                if not UUID_RE.match(value):
                    errors.append(f"  Invalid UUID '{value}' in {path}")
            else:
                validate_uuids(value, path, errors)
    elif isinstance(data, list):
        for item in data:
            validate_uuids(item, path, errors)


def check_duplicate_values(values_list, path):
    """Check for duplicate value strings within the same predicate group."""
    errors = []
    for group in values_list:
        predicate = group.get("predicate", "<unknown>")
        seen = set()
        for entry in group.get("entry", []):
            val = entry.get("value", "")
            if val in seen:
                errors.append(
                    f"  Duplicate value '{val}' under predicate '{predicate}' in {path}"
                )
            seen.add(val)
    return errors


def check_orphaned_predicates(data, path):
    """Check that every predicate referenced in values[] exists in predicates[]."""
    errors = []
    predicate_names = {p["value"] for p in data.get("predicates", [])}
    for group in data.get("values", []):
        pred = group.get("predicate", "")
        if pred not in predicate_names:
            errors.append(
                f"  Orphaned predicate '{pred}' in values[] not found in predicates[] in {path}"
            )
    return errors


def check_duplicate_cluster_values(data, path):
    """Check for duplicate value strings in cluster values[]."""
    errors = []
    seen = set()
    for entry in data.get("values", []):
        val = entry.get("value", "")
        if val in seen:
            errors.append(f"  Duplicate cluster value '{val}' in {path}")
        seen.add(val)
    return errors


# Matches the source_tag pattern enforced by mapping.schema.json:
#   vantacode-<taxonomy>:<predicate>="<value>"
SOURCE_TAG_RE = re.compile(
    r'^(vantacode-[a-z0-9-]+):([a-z0-9-]+)="([^"]+)"$'
)


def build_taxonomy_index(taxonomy_dirs):
    """Build a lookup of namespace -> {predicate -> set(values)} from every loaded
    machinetag.json. Used to cross-check that mapping source_tag references actually
    resolve to a real taxonomy entry, not just a syntactically valid string."""
    index = {}
    for tdir in taxonomy_dirs:
        mt = tdir / "machinetag.json"
        if not mt.exists():
            continue
        try:
            data = load_json(mt)
        except json.JSONDecodeError:
            continue
        ns = data.get("namespace", "")
        if not ns:
            continue
        predicates = {}
        for group in data.get("values", []):
            pred = group.get("predicate", "")
            values = {e.get("value", "") for e in group.get("entry", [])}
            predicates[pred] = values
        # Predicates may exist with no values block — still register them so
        # the validator can distinguish "unknown predicate" from "unknown value".
        for p in data.get("predicates", []):
            pname = p.get("value", "")
            if pname and pname not in predicates:
                predicates[pname] = set()
        index[ns] = predicates
    return index


def validate_mapping(filepath, schema, taxonomy_index):
    """Validate a single cross-reference mapping JSON file."""
    errors = []
    warnings = []
    filename = str(filepath)

    try:
        data = load_json(filepath)
    except json.JSONDecodeError as e:
        return [f"  JSON parse error: {e}"], []

    # Schema validation (catches the namespace prefix bug at the source_tag pattern).
    try:
        jsonschema.validate(instance=data, schema=schema)
    except jsonschema.ValidationError as e:
        errors.append(f"  Schema validation failed: {e.message}")
        if e.absolute_path:
            errors.append(f"    at: {'/'.join(str(p) for p in e.absolute_path)}")

    # Cross-check that the declared `source` namespace exists.
    src_ns = data.get("source", "")
    if src_ns and src_ns not in taxonomy_index:
        errors.append(
            f"  Unknown source namespace '{src_ns}' — no matching taxonomy directory"
        )

    # Walk every mapping entry and verify the source_tag actually resolves to a
    # real predicate+value in the source taxonomy. This is the catch for the
    # "syntactically valid but pointing at nothing" failure mode.
    for idx, entry in enumerate(data.get("mappings", [])):
        tag = entry.get("source_tag", "")
        m = SOURCE_TAG_RE.match(tag)
        if not m:
            # Schema layer already caught this; skip the resolve step.
            continue
        ns, pred, val = m.group(1), m.group(2), m.group(3)
        if ns not in taxonomy_index:
            errors.append(
                f"  mapping[{idx}] source_tag '{tag}' references unknown namespace '{ns}'"
            )
            continue
        preds = taxonomy_index[ns]
        if pred not in preds:
            errors.append(
                f"  mapping[{idx}] source_tag '{tag}' references unknown predicate "
                f"'{ns}:{pred}'"
            )
            continue
        if preds[pred] and val not in preds[pred]:
            errors.append(
                f"  mapping[{idx}] source_tag '{tag}' references unknown value "
                f"'{val}' under predicate '{ns}:{pred}'"
            )

    # If a target_namespace is declared (i.e. the target is another VantaCode
    # taxonomy), make sure it's a real one. We don't try to resolve the
    # target_id values themselves because the cross-walk to external frameworks
    # is intentionally free-form.
    target_ns = data.get("target_namespace")
    if target_ns and target_ns not in taxonomy_index:
        warnings.append(
            f"  Declared target_namespace '{target_ns}' has no matching taxonomy"
        )

    validate_uuids(data, filename, errors)
    return errors, warnings


def validate_taxonomy(filepath, schema):
    """Validate a single taxonomy machinetag.json file."""
    errors = []
    warnings = []
    filename = str(filepath)

    try:
        data = load_json(filepath)
    except json.JSONDecodeError as e:
        return [f"  JSON parse error: {e}"], []

    # Schema validation
    try:
        jsonschema.validate(instance=data, schema=schema)
    except jsonschema.ValidationError as e:
        errors.append(f"  Schema validation failed: {e.message}")
        # Path in schema where error occurred
        if e.absolute_path:
            errors.append(f"    at: {'/'.join(str(p) for p in e.absolute_path)}")

    # Check namespace matches directory name
    parent_dir = filepath.parent.name
    ns = data.get("namespace", "")
    if ns and ns != parent_dir:
        warnings.append(
            f"  Namespace '{ns}' does not match directory name '{parent_dir}'"
        )

    # Check for duplicate values
    if "values" in data:
        errors.extend(check_duplicate_values(data["values"], filename))

    # Check for orphaned predicates
    errors.extend(check_orphaned_predicates(data, filename))

    # Validate UUIDs
    validate_uuids(data, filename, errors)

    return errors, warnings


def validate_galaxy(filepath, schema):
    """Validate a single galaxy definition JSON file."""
    errors = []
    filename = str(filepath)

    try:
        data = load_json(filepath)
    except json.JSONDecodeError as e:
        return [f"  JSON parse error: {e}"], []

    try:
        jsonschema.validate(instance=data, schema=schema)
    except jsonschema.ValidationError as e:
        errors.append(f"  Schema validation failed: {e.message}")
        if e.absolute_path:
            errors.append(f"    at: {'/'.join(str(p) for p in e.absolute_path)}")

    validate_uuids(data, filename, errors)
    return errors, []


def validate_cluster(filepath, schema, galaxy_types):
    """Validate a single cluster JSON file."""
    errors = []
    warnings = []
    filename = str(filepath)

    try:
        data = load_json(filepath)
    except json.JSONDecodeError as e:
        return [f"  JSON parse error: {e}"], []

    try:
        jsonschema.validate(instance=data, schema=schema)
    except jsonschema.ValidationError as e:
        errors.append(f"  Schema validation failed: {e.message}")
        if e.absolute_path:
            errors.append(f"    at: {'/'.join(str(p) for p in e.absolute_path)}")

    # Check type matches a known galaxy type
    cluster_type = data.get("type", "")
    if galaxy_types and cluster_type not in galaxy_types:
        warnings.append(
            f"  Cluster type '{cluster_type}' has no matching galaxy definition"
        )

    # Check for duplicate cluster values
    if "values" in data:
        errors.extend(check_duplicate_cluster_values(data, filename))

    validate_uuids(data, filename, errors)
    return errors, warnings


def main():
    repo_root = find_repo_root()
    schema_dir = repo_root / "schema"

    print(f"{BOLD}{CYAN}VantaCode Taxonomy Validator{RESET}")
    print(f"{CYAN}Repository: {repo_root}{RESET}")
    print()

    # Load schemas
    taxonomy_schema_path = schema_dir / "taxonomy.schema.json"
    galaxy_schema_path = schema_dir / "galaxy.schema.json"
    cluster_schema_path = schema_dir / "cluster.schema.json"
    mapping_schema_path = schema_dir / "mapping.schema.json"

    schemas_ok = True
    for sp in [
        taxonomy_schema_path,
        galaxy_schema_path,
        cluster_schema_path,
        mapping_schema_path,
    ]:
        if not sp.exists():
            print(f"{RED}MISSING schema: {sp}{RESET}")
            schemas_ok = False

    if not schemas_ok:
        print(f"\n{RED}Cannot proceed without all schema files.{RESET}")
        sys.exit(1)

    taxonomy_schema = load_json(taxonomy_schema_path)
    galaxy_schema = load_json(galaxy_schema_path)
    cluster_schema = load_json(cluster_schema_path)
    mapping_schema = load_json(mapping_schema_path)

    total_errors = 0
    total_warnings = 0
    total_pass = 0

    # --- Validate Taxonomies ---
    print(f"{BOLD}--- Taxonomies ---{RESET}")
    taxonomy_dirs = sorted(
        d
        for d in repo_root.iterdir()
        if d.is_dir() and d.name.startswith("vantacode-")
    )

    # Build the namespace -> predicates -> values index up front so the
    # mappings pass below can resolve every source_tag.
    taxonomy_index = build_taxonomy_index(taxonomy_dirs)

    for tdir in taxonomy_dirs:
        mt = tdir / "machinetag.json"
        if not mt.exists():
            print(f"  {YELLOW}SKIP{RESET} {tdir.name}/ (no machinetag.json)")
            continue

        errors, warnings = validate_taxonomy(mt, taxonomy_schema)
        if errors:
            print(f"  {RED}FAIL{RESET} {tdir.name}/machinetag.json")
            for e in errors:
                print(f"    {RED}{e}{RESET}")
            total_errors += len(errors)
        else:
            print(f"  {GREEN}PASS{RESET} {tdir.name}/machinetag.json")
            total_pass += 1

        for w in warnings:
            print(f"    {YELLOW}WARN{RESET} {w}")
            total_warnings += 1

    # --- Validate Galaxies ---
    print(f"\n{BOLD}--- Galaxies ---{RESET}")
    galaxies_dir = repo_root / "galaxies"
    galaxy_types = set()

    if galaxies_dir.exists():
        for gf in sorted(galaxies_dir.glob("*.json")):
            errors, warnings = validate_galaxy(gf, galaxy_schema)
            if errors:
                print(f"  {RED}FAIL{RESET} galaxies/{gf.name}")
                for e in errors:
                    print(f"    {RED}{e}{RESET}")
                total_errors += len(errors)
            else:
                print(f"  {GREEN}PASS{RESET} galaxies/{gf.name}")
                total_pass += 1
                # Track galaxy types for cluster cross-reference
                try:
                    gdata = load_json(gf)
                    galaxy_types.add(gdata.get("type", ""))
                except Exception:
                    pass

            for w in warnings:
                print(f"    {YELLOW}WARN{RESET} {w}")
                total_warnings += 1
    else:
        print(f"  {YELLOW}SKIP{RESET} (no galaxies/ directory)")

    # --- Validate Clusters ---
    print(f"\n{BOLD}--- Clusters ---{RESET}")
    clusters_dir = repo_root / "clusters"

    if clusters_dir.exists():
        for cf in sorted(clusters_dir.glob("*.json")):
            errors, warnings = validate_cluster(cf, cluster_schema, galaxy_types)
            if errors:
                print(f"  {RED}FAIL{RESET} clusters/{cf.name}")
                for e in errors:
                    print(f"    {RED}{e}{RESET}")
                total_errors += len(errors)
            else:
                print(f"  {GREEN}PASS{RESET} clusters/{cf.name}")
                total_pass += 1

            for w in warnings:
                print(f"    {YELLOW}WARN{RESET} {w}")
                total_warnings += 1
    else:
        print(f"  {YELLOW}SKIP{RESET} (no clusters/ directory)")

    # --- Validate Mappings ---
    print(f"\n{BOLD}--- Mappings ---{RESET}")
    mappings_dir = repo_root / "mappings"

    if mappings_dir.exists():
        for mf in sorted(mappings_dir.glob("*.json")):
            errors, warnings = validate_mapping(mf, mapping_schema, taxonomy_index)
            if errors:
                print(f"  {RED}FAIL{RESET} mappings/{mf.name}")
                for e in errors:
                    print(f"    {RED}{e}{RESET}")
                total_errors += len(errors)
            else:
                print(f"  {GREEN}PASS{RESET} mappings/{mf.name}")
                total_pass += 1

            for w in warnings:
                print(f"    {YELLOW}WARN{RESET} {w}")
                total_warnings += 1
    else:
        print(f"  {YELLOW}SKIP{RESET} (no mappings/ directory)")

    # --- Summary ---
    print(f"\n{BOLD}--- Summary ---{RESET}")
    print(f"  {GREEN}Passed: {total_pass}{RESET}")
    if total_warnings:
        print(f"  {YELLOW}Warnings: {total_warnings}{RESET}")
    if total_errors:
        print(f"  {RED}Errors: {total_errors}{RESET}")
        print(f"\n{RED}Validation FAILED.{RESET}")
        sys.exit(1)
    else:
        print(f"\n{GREEN}All validations passed.{RESET}")
        sys.exit(0)


if __name__ == "__main__":
    main()
