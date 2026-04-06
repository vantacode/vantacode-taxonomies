#!/usr/bin/env python3
# Copyright (c) DarkCode LLC. All rights reserved.
# SPDX-License-Identifier: BSD-2-Clause
# Contact: cory@darkcode.ai
"""
Generate README.md documentation for each taxonomy from its machinetag.json.

Creates a markdown README in each taxonomy directory with:
  - Title and description
  - Table of predicates
  - Table of values per predicate (value, expanded, description, colour)
  - Tag format examples

Also prints a summary listing all taxonomies with tag counts.
"""

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


def load_json(path):
    """Load and return parsed JSON."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def escape_md(text):
    """Escape pipe characters for markdown table cells."""
    if not text:
        return ""
    return text.replace("|", "\\|")


def generate_taxonomy_readme(data, output_path):
    """Generate a README.md for a single taxonomy."""
    namespace = data.get("namespace", "unknown")
    description = data.get("description", "")
    version = data.get("version", 1)
    exclusive = data.get("exclusive", False)
    refs = data.get("refs", [])
    predicates = data.get("predicates", [])
    values = data.get("values", [])

    lines = []
    lines.append(f"# {namespace}")
    lines.append("")
    lines.append(f"> {description}")
    lines.append("")
    lines.append(f"**Version:** {version}  ")
    lines.append(f"**Exclusive:** {'Yes' if exclusive else 'No'}  ")
    if refs:
        lines.append(f"**References:** {', '.join(refs)}  ")
    lines.append("")

    # Predicates table
    lines.append("## Predicates")
    lines.append("")
    lines.append("| Predicate | Expanded | Description | Exclusive |")
    lines.append("|-----------|----------|-------------|-----------|")
    for pred in predicates:
        pval = pred.get("value", "")
        pexp = escape_md(pred.get("expanded", ""))
        pdesc = escape_md(pred.get("description", ""))
        pexcl = "Yes" if pred.get("exclusive", False) else "No"
        lines.append(f"| `{pval}` | {pexp} | {pdesc} | {pexcl} |")
    lines.append("")

    # Values tables per predicate
    # Build a lookup from predicate name to value entries
    values_by_pred = {}
    for group in values:
        pred_name = group.get("predicate", "")
        values_by_pred[pred_name] = group.get("entry", [])

    tag_examples = []

    for pred in predicates:
        pval = pred.get("value", "")
        entries = values_by_pred.get(pval, [])
        if not entries:
            continue

        lines.append(f"## Values: `{pval}`")
        lines.append("")
        lines.append("| Value | Expanded | Description | Colour |")
        lines.append("|-------|----------|-------------|--------|")

        for entry in entries:
            ev = entry.get("value", "")
            eexp = escape_md(entry.get("expanded", ""))
            edesc = escape_md(entry.get("description", ""))
            ecol = entry.get("colour", "")
            col_cell = f"`{ecol}`" if ecol else ""
            lines.append(f"| `{ev}` | {eexp} | {edesc} | {col_cell} |")

            # Collect first example per predicate
            if len(tag_examples) < len(predicates) and not any(
                pval in t for t in tag_examples
            ):
                tag_examples.append(f'{namespace}:{pval}="{ev}"')

        lines.append("")

    # Tag format examples
    if tag_examples:
        lines.append("## Tag Format Examples")
        lines.append("")
        lines.append("```")
        for example in tag_examples[:5]:
            lines.append(example)
        lines.append("```")
        lines.append("")

    # Count total tags
    total_tags = sum(len(values_by_pred.get(p["value"], [])) for p in predicates)
    lines.append("---")
    lines.append("")
    lines.append(f"*{total_tags} tags across {len(predicates)} predicates.*")
    lines.append("")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return namespace, total_tags, len(predicates)


def main():
    repo_root = find_repo_root()
    print(f"Repository: {repo_root}")
    print()

    taxonomy_dirs = sorted(
        d
        for d in repo_root.iterdir()
        if d.is_dir() and d.name.startswith("vantacode-")
    )

    summary = []

    for tdir in taxonomy_dirs:
        mt = tdir / "machinetag.json"
        if not mt.exists():
            print(f"  SKIP {tdir.name}/ (no machinetag.json)")
            continue

        data = load_json(mt)
        readme_path = tdir / "README.md"
        namespace, total_tags, num_preds = generate_taxonomy_readme(data, readme_path)
        summary.append((namespace, total_tags, num_preds))
        print(f"  Generated {tdir.name}/README.md ({total_tags} tags)")

    # Print summary
    print()
    print("=== Summary ===")
    print(f"{'Namespace':<30} {'Tags':>6} {'Predicates':>12}")
    print("-" * 52)
    total = 0
    for ns, tags, preds in summary:
        print(f"{ns:<30} {tags:>6} {preds:>12}")
        total += tags
    print("-" * 52)
    print(f"{'TOTAL':<30} {total:>6}")
    print()


if __name__ == "__main__":
    main()
