#!/usr/bin/env python3
# Copyright (c) DarkCode LLC. All rights reserved.
# SPDX-License-Identifier: BSD-2-Clause
# Contact: cory@darkcode.ai
"""
Generate a unified tag list across all taxonomies and galaxy clusters.

Taxonomy tags:  vantacode:{namespace}:{predicate}="{value}"
Galaxy cluster: vantacode:galaxy:{type}="{value}"

Usage:
  python generate_tags.py
  python generate_tags.py --format json
  python generate_tags.py --format csv
  python generate_tags.py --filter vantacode-mbt
"""

import argparse
import csv
import io
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


def collect_taxonomy_tags(repo_root, ns_filter=None):
    """Collect all taxonomy tags in unified format.

    Returns list of dicts with: tag, source, namespace, predicate, value
    """
    tags = []
    for d in sorted(repo_root.iterdir()):
        if not d.is_dir() or not d.name.startswith("vantacode-"):
            continue
        mt = d / "machinetag.json"
        if not mt.exists():
            continue

        data = load_json(mt)
        namespace = data.get("namespace", d.name)

        if ns_filter and namespace != ns_filter:
            continue

        for group in data.get("values", []):
            predicate = group.get("predicate", "")
            for entry in group.get("entry", []):
                value = entry.get("value", "")
                tag = f'vantacode:{namespace}:{predicate}="{value}"'
                tags.append(
                    {
                        "tag": tag,
                        "source": "taxonomy",
                        "namespace": namespace,
                        "predicate": predicate,
                        "value": value,
                    }
                )

    return tags


def collect_galaxy_tags(repo_root, ns_filter=None):
    """Collect all galaxy cluster tags in unified format.

    Returns list of dicts with: tag, source, namespace, type, value
    """
    tags = []
    clusters_dir = repo_root / "clusters"
    if not clusters_dir.exists():
        return tags

    for cf in sorted(clusters_dir.glob("*.json")):
        data = load_json(cf)
        cluster_type = data.get("type", "")

        if ns_filter and ns_filter not in cluster_type:
            continue

        for entry in data.get("values", []):
            value = entry.get("value", "")
            tag = f'vantacode:galaxy:{cluster_type}="{value}"'
            tags.append(
                {
                    "tag": tag,
                    "source": "galaxy",
                    "namespace": "galaxy",
                    "predicate": cluster_type,
                    "value": value,
                }
            )

    return tags


def output_text(tags):
    """Print tags as plain text, one per line."""
    for t in tags:
        print(t["tag"])


def output_json(tags):
    """Print tags as JSON array."""
    print(json.dumps([t["tag"] for t in tags], indent=2))


def output_csv(tags):
    """Print tags as CSV."""
    buf = io.StringIO()
    writer = csv.DictWriter(
        buf, fieldnames=["tag", "source", "namespace", "predicate", "value"]
    )
    writer.writeheader()
    for t in tags:
        writer.writerow(t)
    print(buf.getvalue(), end="")


def main():
    parser = argparse.ArgumentParser(
        description="Generate unified tag list across all taxonomies and galaxy clusters."
    )
    parser.add_argument(
        "--format",
        choices=["text", "json", "csv"],
        default="text",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--filter",
        type=str,
        default=None,
        help="Filter by namespace (e.g., vantacode-mbt)",
    )

    args = parser.parse_args()
    repo_root = find_repo_root()

    taxonomy_tags = collect_taxonomy_tags(repo_root, args.filter)
    galaxy_tags = collect_galaxy_tags(repo_root, args.filter)
    all_tags = taxonomy_tags + galaxy_tags

    if not all_tags:
        print("No tags found.", file=sys.stderr)
        sys.exit(1)

    if args.format == "json":
        output_json(all_tags)
    elif args.format == "csv":
        output_csv(all_tags)
    else:
        output_text(all_tags)

    # Summary to stderr so it doesn't pollute piped output
    print(
        f"\n# {len(taxonomy_tags)} taxonomy tags + {len(galaxy_tags)} galaxy tags = {len(all_tags)} total",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
