#!/usr/bin/env python3
# Copyright (c) DarkCode LLC. All rights reserved.
# SPDX-License-Identifier: BSD-2-Clause
# Contact: cory@darkcode.ai
"""
Dump all valid triple tags from VantaCode taxonomies.

Usage:
  python machinetag.py --namespace vantacode-mbt
  python machinetag.py --all
  python machinetag.py --all --count
  python machinetag.py --namespace vantacode-domain --json
"""

import argparse
import json
import sys
from pathlib import Path


def find_repo_root():
    """Walk up from this script's location to find the repo root."""
    here = Path(__file__).resolve().parent
    for candidate in [here.parent, here.parent.parent, here]:
        if (candidate / "MANIFEST.json").exists():
            return candidate
    return here.parent


def load_taxonomy(path):
    """Load a machinetag.json and return parsed data."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def extract_tags(data):
    """Extract all valid triple tags from a taxonomy data structure.

    Returns list of tag strings in format: namespace:predicate="value"
    """
    namespace = data.get("namespace", "")
    tags = []

    for group in data.get("values", []):
        predicate = group.get("predicate", "")
        for entry in group.get("entry", []):
            value = entry.get("value", "")
            tags.append(f'{namespace}:{predicate}="{value}"')

    # If no values section, emit predicate-only tags
    if not data.get("values"):
        for pred in data.get("predicates", []):
            tags.append(f'{namespace}:{pred["value"]}')

    return tags


def get_taxonomy_dirs(repo_root):
    """Find all taxonomy directories (vantacode-* with machinetag.json)."""
    dirs = {}
    for d in sorted(repo_root.iterdir()):
        if d.is_dir() and d.name.startswith("vantacode-"):
            mt = d / "machinetag.json"
            if mt.exists():
                dirs[d.name] = mt
    return dirs


def main():
    parser = argparse.ArgumentParser(
        description="Dump all valid triple tags from VantaCode taxonomies."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--namespace",
        type=str,
        help="Single taxonomy namespace to dump (e.g., vantacode-mbt)",
    )
    group.add_argument(
        "--all",
        action="store_true",
        help="Dump tags from all taxonomies",
    )
    parser.add_argument(
        "--count",
        action="store_true",
        help="Show count per namespace instead of listing tags",
    )
    parser.add_argument(
        "--json",
        dest="output_json",
        action="store_true",
        help="Output as JSON array",
    )

    args = parser.parse_args()
    repo_root = find_repo_root()
    taxonomy_dirs = get_taxonomy_dirs(repo_root)

    if not taxonomy_dirs:
        print("No taxonomies found.", file=sys.stderr)
        sys.exit(1)

    # Determine which namespaces to process
    if args.namespace:
        ns = args.namespace
        if ns not in taxonomy_dirs:
            print(f"Namespace '{ns}' not found.", file=sys.stderr)
            print(f"Available: {', '.join(taxonomy_dirs.keys())}", file=sys.stderr)
            sys.exit(1)
        namespaces = {ns: taxonomy_dirs[ns]}
    else:
        namespaces = taxonomy_dirs

    all_tags = []
    counts = {}

    for ns_name, mt_path in sorted(namespaces.items()):
        data = load_taxonomy(mt_path)
        tags = extract_tags(data)
        all_tags.extend(tags)
        counts[ns_name] = len(tags)

    if args.count:
        if args.output_json:
            print(json.dumps(counts, indent=2))
        else:
            for ns_name, count in sorted(counts.items()):
                print(f"{ns_name}: {count} tags")
            print(f"\nTotal: {sum(counts.values())} tags")
    elif args.output_json:
        print(json.dumps(all_tags, indent=2))
    else:
        for tag in all_tags:
            print(tag)


if __name__ == "__main__":
    main()
