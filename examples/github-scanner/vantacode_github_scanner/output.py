"""Output writers for GithubScanReport.

JSON, CSV, and STIX 2.1 — same shape as the local scanner so consumers
that already handle one can handle both.
"""

from __future__ import annotations

import csv
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

from .scanner import GithubFinding, GithubScanReport


# ── JSON ────────────────────────────────────────────────────────────────────

def write_json(report: GithubScanReport, path: Path) -> None:
    path.write_text(json.dumps(report.to_dict(), indent=2))


# ── CSV ─────────────────────────────────────────────────────────────────────

CSV_COLUMNS = [
    "rule_id",
    "rule_title",
    "taxonomy",
    "severity",
    "category",
    "repo",
    "path",
    "url",
    "language",
    "query",
    "fragment",
    "related_tags",
    "mitre_attack",
    "owasp_llm",
    "taxonomy_uuid",
]


def write_csv(report: GithubScanReport, path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(CSV_COLUMNS)
        for f in report.findings:
            fragment = (f.fragments[0] if f.fragments else "")[:500]
            w.writerow([
                f.rule_id,
                f.rule_title,
                f.taxonomy,
                f.severity,
                f.category or "",
                f.repo,
                f.path,
                f.url,
                f.language or "",
                f.query,
                fragment,
                "; ".join(f.related_tags),
                "; ".join(f.mitre_attack),
                "; ".join(f.owasp_llm),
                f.taxonomy_uuid or "",
            ])


# ── STIX 2.1 ────────────────────────────────────────────────────────────────

_VANTACODE_GH_IDENTITY_ID = "identity--6f3c0e9a-2b4d-4d8e-9a1f-7c5b3e2a1d04"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _bundle_native(report: GithubScanReport) -> dict:
    """Hand-rolled STIX 2.1 bundle. No `stix2` dep required."""
    objs: list[dict] = []
    now = _now()

    objs.append({
        "type": "identity",
        "spec_version": "2.1",
        "id": _VANTACODE_GH_IDENTITY_ID,
        "created": now,
        "modified": now,
        "name": "VantaCode GitHub Scanner",
        "identity_class": "system",
        "description": "VantaCode taxonomy-driven GitHub-wide code search scanner.",
    })

    for f in report.findings:
        ind_id = f"indicator--{uuid.uuid4()}"
        labels = [
            f"vantacode:{f.taxonomy}",
            f"vantacode-rule:{f.rule_id}",
            f"severity:{f.severity}",
            "source:github-code-search",
        ] + list(f.related_tags)

        # STIX file pattern with the GitHub URL preserved as the location
        stix_pattern = f"[file:name = '{f.path}']"

        ind: dict = {
            "type": "indicator",
            "spec_version": "2.1",
            "id": ind_id,
            "created": now,
            "modified": now,
            "created_by_ref": _VANTACODE_GH_IDENTITY_ID,
            "name": f"{f.rule_id} — {f.rule_title}",
            "description": (f.fragments[0] if f.fragments else f.rule_title),
            "indicator_types": ["malicious-activity"],
            "pattern_type": "stix",
            "pattern": stix_pattern,
            "valid_from": now,
            "labels": labels,
            "external_references": [
                {
                    "source_name": "vantacode-taxonomies",
                    "url": "https://github.com/vantacode/vantacode-taxonomies",
                    "external_id": f.rule_id,
                },
                {
                    "source_name": "github",
                    "url": f.url or f"https://github.com/{f.repo}",
                    "description": f"Hit in {f.repo}/{f.path}",
                },
            ],
            "x_vantacode": {
                "rule_id": f.rule_id,
                "taxonomy": f.taxonomy,
                "category": f.category,
                "severity": f.severity,
                "mitre_attack": f.mitre_attack,
                "owasp_llm": f.owasp_llm,
                "taxonomy_uuid": f.taxonomy_uuid,
                "repo": f.repo,
                "path": f.path,
                "url": f.url,
                "query": f.query,
                "language": f.language,
                "fragments": f.fragments,
            },
        }

        if f.taxonomy_uuid:
            ind["external_references"].append({
                "source_name": "vantacode-galaxy",
                "external_id": f.taxonomy_uuid,
            })

        for attack_id in f.mitre_attack:
            ind["external_references"].append({
                "source_name": "mitre-attack",
                "external_id": attack_id,
                "url": f"https://attack.mitre.org/techniques/{attack_id.replace('.', '/')}/",
            })

        objs.append(ind)

        sighting_id = f"sighting--{uuid.uuid4()}"
        objs.append({
            "type": "sighting",
            "spec_version": "2.1",
            "id": sighting_id,
            "created": now,
            "modified": now,
            "created_by_ref": _VANTACODE_GH_IDENTITY_ID,
            "first_seen": now,
            "last_seen": now,
            "count": 1,
            "sighting_of_ref": ind_id,
            "where_sighted_refs": [_VANTACODE_GH_IDENTITY_ID],
        })

    return {
        "type": "bundle",
        "id": f"bundle--{uuid.uuid4()}",
        "objects": objs,
    }


def write_stix(report: GithubScanReport, path: Path) -> None:
    try:
        import stix2  # type: ignore  # noqa: F401
    except ImportError:
        pass
    path.write_text(json.dumps(_bundle_native(report), indent=2))
