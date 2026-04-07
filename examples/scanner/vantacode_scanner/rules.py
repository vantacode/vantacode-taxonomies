"""Rule loading and compilation.

Reads every YAML file under a scanner-rules directory, validates the basic
shape, compiles regex patterns, and exposes a flat list of `Rule` objects
keyed by taxonomy.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


_FLAG_MAP = {
    "ignorecase": re.IGNORECASE,
    "multiline":  re.MULTILINE,
    "dotall":     re.DOTALL,
    "verbose":    re.VERBOSE,
}


@dataclass
class GithubQuery:
    """A single GitHub Code Search phrase derived from a rule.

    `query` is fed verbatim as the positional arg to `gh search code`. Quoted
    phrases inside the query are honored as AND-grouped tokens by GitHub.
    `language` (optional) maps to the `--language` flag and bypasses the
    legacy gh wrapping bug for multi-token queries.
    """
    query: str
    language: str | None = None
    description: str | None = None


@dataclass
class Rule:
    id: str
    title: str
    severity: str
    taxonomy: str
    category: str | None = None
    category_weight: float | None = None
    taxonomy_uuid: str | None = None
    related_tags: list[str] = field(default_factory=list)
    mitre_attack: list[str] = field(default_factory=list)
    owasp_llm: list[str] = field(default_factory=list)
    references: list[str] = field(default_factory=list)
    fix: str | None = None
    description: str | None = None

    detection_type: str = "regex"
    target_globs: list[str] = field(default_factory=list)
    exclude_globs: list[str] = field(default_factory=list)

    compiled_patterns: list[re.Pattern[str]] = field(default_factory=list)
    raw_patterns: list[str] = field(default_factory=list)
    min_matches: int = 1

    manifest_files: list[str] = field(default_factory=list)
    manifest_check: str | None = None
    missing_paths: list[str] = field(default_factory=list)
    min_count: int | None = None
    max_count: int | None = None
    notes: str | None = None

    github_search: list[GithubQuery] = field(default_factory=list)


@dataclass
class RulePack:
    taxonomy: str
    version: int
    description: str
    source_galaxy: str | None
    rules: list[Rule]


def _compile_flags(flag_names: list[str]) -> int:
    f = 0
    for name in flag_names:
        if name in _FLAG_MAP:
            f |= _FLAG_MAP[name]
    return f


def _coerce_list(v: Any) -> list:
    if v is None:
        return []
    if isinstance(v, list):
        return v
    return [v]


def _parse_github_search(raw: Any) -> list[GithubQuery]:
    """Normalize the `github_search` field into a list of GithubQuery objects.

    Accepts:
        - None / missing             → []
        - "phrase"                   → [GithubQuery(query="phrase")]
        - ["a", "b"]                 → [GithubQuery("a"), GithubQuery("b")]
        - [{"query": "...", "language": "python"}, ...]
        - mixed list of strings and dicts
    """
    if raw is None:
        return []
    if isinstance(raw, str):
        return [GithubQuery(query=raw)]
    if not isinstance(raw, list):
        raise ValueError(f"github_search must be a string or list, got {type(raw).__name__}")

    out: list[GithubQuery] = []
    for item in raw:
        if isinstance(item, str):
            out.append(GithubQuery(query=item))
        elif isinstance(item, dict):
            q = item.get("query")
            if not q or not isinstance(q, str):
                raise ValueError(f"github_search item missing string 'query': {item!r}")
            out.append(GithubQuery(
                query=q,
                language=item.get("language"),
                description=item.get("description"),
            ))
        else:
            raise ValueError(f"github_search item must be string or mapping, got {type(item).__name__}")
    return out


def load_rule_pack(path: Path) -> RulePack:
    data = yaml.safe_load(path.read_text())
    if not isinstance(data, dict):
        raise ValueError(f"{path}: rule pack must be a mapping")

    taxonomy = data.get("taxonomy")
    if not taxonomy:
        raise ValueError(f"{path}: missing 'taxonomy'")

    default_target = data.get("default_target") or {}
    default_globs = default_target.get("globs") or []
    default_excludes = default_target.get("exclude_globs") or []

    rules: list[Rule] = []
    for raw in data.get("rules") or []:
        det = raw.get("detection") or {}
        flags = _compile_flags(det.get("flags") or [])

        compiled: list[re.Pattern[str]] = []
        raw_patterns = _coerce_list(det.get("patterns"))
        if det.get("type") == "regex":
            for p in raw_patterns:
                try:
                    compiled.append(re.compile(p, flags))
                except re.error as e:
                    raise ValueError(f"{path}: rule {raw.get('id')}: invalid regex {p!r}: {e}") from e

        target = raw.get("target") or {}
        rule = Rule(
            id=raw["id"],
            title=raw["title"],
            severity=raw.get("severity", "info"),
            taxonomy=taxonomy,
            category=raw.get("category"),
            category_weight=raw.get("category_weight"),
            taxonomy_uuid=raw.get("taxonomy_uuid"),
            related_tags=_coerce_list(raw.get("related_tags")),
            mitre_attack=_coerce_list(raw.get("mitre_attack")),
            owasp_llm=_coerce_list(raw.get("owasp_llm")),
            references=_coerce_list(raw.get("references")),
            fix=raw.get("fix"),
            description=raw.get("description"),
            detection_type=det.get("type", "regex"),
            target_globs=target.get("globs") or default_globs,
            exclude_globs=target.get("exclude_globs") or default_excludes,
            compiled_patterns=compiled,
            raw_patterns=raw_patterns,
            min_matches=int(det.get("min_matches", 1)),
            manifest_files=_coerce_list(det.get("manifest_files")),
            manifest_check=det.get("manifest_check"),
            missing_paths=_coerce_list(det.get("missing_paths")),
            min_count=det.get("min_count"),
            max_count=det.get("max_count"),
            notes=det.get("notes"),
            github_search=_parse_github_search(raw.get("github_search")),
        )
        rules.append(rule)

    return RulePack(
        taxonomy=taxonomy,
        version=int(data.get("version", 1)),
        description=data.get("description", ""),
        source_galaxy=data.get("source_galaxy"),
        rules=rules,
    )


def load_all_rule_packs(rules_dir: Path) -> list[RulePack]:
    packs: list[RulePack] = []
    for path in sorted(rules_dir.glob("*.yaml")):
        if path.name.startswith("_"):
            continue
        packs.append(load_rule_pack(path))
    for path in sorted(rules_dir.glob("*.yml")):
        if path.name.startswith("_"):
            continue
        packs.append(load_rule_pack(path))
    return packs
