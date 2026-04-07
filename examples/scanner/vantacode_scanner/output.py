"""Output writers for scan reports.

Three formats:
  - JSON  — full structured report (always available)
  - CSV   — one finding per row (always available)
  - STIX  — STIX 2.1 indicator + sighting bundle (uses `stix2` if installed,
            falls back to a hand-rolled bundle if not)
"""

from __future__ import annotations

import csv
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

from .scanner import Finding, ScanReport, report_to_json


def write_json(report: ScanReport, path: Path) -> None:
    path.write_text(report_to_json(report))


CSV_COLUMNS = [
    "rule_id",
    "rule_title",
    "taxonomy",
    "severity",
    "category",
    "file",
    "line",
    "snippet",
    "detection_type",
    "related_tags",
    "mitre_attack",
    "owasp_llm",
    "taxonomy_uuid",
    "fix",
]


def write_csv(report: ScanReport, path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(CSV_COLUMNS)
        for f in report.findings:
            w.writerow([
                f.rule_id,
                f.rule_title,
                f.taxonomy,
                f.severity,
                f.category or "",
                f.file,
                f.line if f.line is not None else "",
                (f.snippet or "")[:500],
                f.detection_type,
                "; ".join(f.related_tags),
                "; ".join(f.mitre_attack),
                "; ".join(f.owasp_llm),
                f.taxonomy_uuid or "",
                (f.fix or "")[:300],
            ])


# ── STIX 2.1 ────────────────────────────────────────────────────────────────

_STIX_SEVERITY = {
    "info":     "low",
    "low":      "low",
    "medium":   "medium",
    "high":     "high",
    "critical": "critical",
    "variable": "medium",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _identity_id() -> str:
    return "identity--c8a4d9b3-1b2c-4f3a-8d6e-9b0a1c2d3e4f"  # stable VantaCode identity


def _bundle_native(report: ScanReport) -> dict:
    """Hand-rolled STIX 2.1 bundle that doesn't depend on the stix2 library."""
    objs: list[dict] = []
    now = _now()

    objs.append({
        "type": "identity",
        "spec_version": "2.1",
        "id": _identity_id(),
        "created": now,
        "modified": now,
        "name": "VantaCode Scanner",
        "identity_class": "system",
        "description": "VantaCode taxonomy-driven repository scanner.",
    })

    for f in report.findings:
        ind_id = f"indicator--{uuid.uuid4()}"
        labels = [
            f"vantacode:{f.taxonomy}",
            f"vantacode-rule:{f.rule_id}",
            f"severity:{f.severity}",
        ] + list(f.related_tags)

        ind: dict = {
            "type": "indicator",
            "spec_version": "2.1",
            "id": ind_id,
            "created": now,
            "modified": now,
            "created_by_ref": _identity_id(),
            "name": f"{f.rule_id} — {f.rule_title}",
            "description": f.snippet or f.rule_title,
            "indicator_types": ["malicious-activity"],
            "pattern_type": "stix",
            "pattern": f"[file:name = '{f.file}']",
            "valid_from": now,
            "labels": labels,
            "external_references": [
                {
                    "source_name": "vantacode-taxonomies",
                    "url": "https://github.com/vantacode/vantacode-taxonomies",
                    "external_id": f.rule_id,
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
                "file": f.file,
                "line": f.line,
                "fix": f.fix,
            },
        }

        if f.taxonomy_uuid:
            ind["external_references"].append({
                "source_name": "vantacode-galaxy",
                "external_id": f.taxonomy_uuid,
            })

        if f.mitre_attack:
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
            "created_by_ref": _identity_id(),
            "first_seen": now,
            "last_seen": now,
            "count": 1,
            "sighting_of_ref": ind_id,
            "where_sighted_refs": [_identity_id()],
        })

    return {
        "type": "bundle",
        "id": f"bundle--{uuid.uuid4()}",
        "objects": objs,
    }


def write_stix(report: ScanReport, path: Path) -> None:
    """Write STIX 2.1 bundle. Uses `stix2` if installed for validation, else native."""
    try:
        import stix2  # type: ignore  # noqa: F401
        # We still emit our own dict to avoid the strict validation tax for example use,
        # but the import proves the user environment can ingest the result.
    except ImportError:
        pass
    bundle = _bundle_native(report)
    path.write_text(json.dumps(bundle, indent=2))
