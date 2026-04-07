"""Orchestrator for GitHub-wide VantaCode scans.

Loads rule packs from `scanner-rules/` (via the local `vantacode_scanner`
package), iterates rules that have a `github_search` field, runs each
query through `gh search code`, and assembles a `GithubScanReport`.

The structure mirrors the local scanner so that downstream consumers (the
JSON / CSV / STIX writers, MISP import, dashboards) can treat both
reports the same way.
"""

from __future__ import annotations

import datetime as dt
import sys
import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Iterable

from vantacode_scanner.rules import GithubQuery, Rule, RulePack, load_all_rule_packs

from .gh import GhHit, search_code


_SEVERITY_RANK = {"info": 0, "low": 1, "medium": 2, "high": 3, "critical": 4, "variable": 2}


def severity_rank(s: str) -> int:
    return _SEVERITY_RANK.get(s, 0)


@dataclass
class GithubFinding:
    rule_id: str
    rule_title: str
    taxonomy: str
    severity: str
    category: str | None
    repo: str
    path: str
    url: str
    query: str
    language: str | None
    fragments: list[str]
    related_tags: list[str] = field(default_factory=list)
    mitre_attack: list[str] = field(default_factory=list)
    owasp_llm: list[str] = field(default_factory=list)
    taxonomy_uuid: str | None = None
    references: list[str] = field(default_factory=list)
    description: str | None = None
    finding_uuid: str = field(default_factory=lambda: str(uuid.uuid4()))

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class GithubScanReport:
    queried_taxonomies: list[str]
    queries_run: int
    queries_failed: int
    repos_seen: int
    findings: list[GithubFinding]
    started_at: str
    finished_at: str
    errors: list[dict] = field(default_factory=list)

    def summary_by_severity(self) -> dict[str, int]:
        out: dict[str, int] = {}
        for f in self.findings:
            out[f.severity] = out.get(f.severity, 0) + 1
        return out

    def summary_by_taxonomy(self) -> dict[str, int]:
        out: dict[str, int] = {}
        for f in self.findings:
            out[f.taxonomy] = out.get(f.taxonomy, 0) + 1
        return out

    def summary_by_repo(self) -> dict[str, int]:
        out: dict[str, int] = {}
        for f in self.findings:
            out[f.repo] = out.get(f.repo, 0) + 1
        return out

    def to_dict(self) -> dict:
        return {
            "queried_taxonomies": self.queried_taxonomies,
            "queries_run": self.queries_run,
            "queries_failed": self.queries_failed,
            "repos_seen": self.repos_seen,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "summary": {
                "total": len(self.findings),
                "by_severity": self.summary_by_severity(),
                "by_taxonomy": self.summary_by_taxonomy(),
                "by_repo": self.summary_by_repo(),
            },
            "findings": [f.to_dict() for f in self.findings],
            "errors": self.errors,
        }


def _scope_query(query: str, scope: str | None) -> str:
    """Append a `org:foo` / `user:foo` / `repo:foo/bar` qualifier."""
    if not scope:
        return query
    return f"{query} {scope}"


def _iter_searchable_rules(
    packs: Iterable[RulePack],
    *,
    only_taxonomies: set[str] | None,
    only_severities: set[str] | None,
) -> Iterable[tuple[Rule, RulePack]]:
    for pack in packs:
        if only_taxonomies and pack.taxonomy not in only_taxonomies:
            continue
        for rule in pack.rules:
            if not rule.github_search:
                continue
            if only_severities and rule.severity not in only_severities:
                continue
            yield rule, pack


def run_scan(
    rules_dir: Path,
    *,
    scope: str | None = None,
    only_taxonomies: set[str] | None = None,
    only_severities: set[str] | None = None,
    pages: int = 1,
    per_page: int = 100,
    pause_seconds: float = 2.5,
    max_queries: int | None = None,
    log: callable = lambda msg: None,
) -> GithubScanReport:
    """Run the GitHub-wide scan.

    `scope`            — None for all-of-GitHub, or `org:foo`/`user:foo`/`repo:owner/name`
    `only_taxonomies`  — restrict to rule packs in this set
    `only_severities`  — restrict to rules at these severity levels
    `pages` * `per_page` — total result cap per query (legacy API max 1000)
    `max_queries`      — hard cap on the number of gh searches issued (debug aid)
    `log`              — callable for human-readable progress
    """
    packs = load_all_rule_packs(rules_dir)
    if not packs:
        raise RuntimeError(f"No rule packs found under {rules_dir}")

    started_at = dt.datetime.now(dt.timezone.utc).isoformat()
    findings: list[GithubFinding] = []
    errors: list[dict] = []
    queried_taxonomies: set[str] = set()
    repos: set[str] = set()
    queries_run = 0
    queries_failed = 0

    for rule, pack in _iter_searchable_rules(
        packs,
        only_taxonomies=only_taxonomies,
        only_severities=only_severities,
    ):
        queried_taxonomies.add(pack.taxonomy)
        for q in rule.github_search:
            if max_queries is not None and queries_run >= max_queries:
                break
            scoped = _scope_query(q.query, scope)
            log(f"  [{rule.id}] {scoped}"
                + (f" --language {q.language}" if q.language else ""))
            hits, err = search_code(
                scoped,
                language=q.language,
                pages=pages,
                per_page=per_page,
                pause_seconds=pause_seconds,
            )
            queries_run += 1
            if err:
                queries_failed += 1
                errors.append({
                    "rule_id": rule.id,
                    "query": scoped,
                    "language": q.language,
                    "error": err,
                })
                continue
            for h in hits:
                if h.repo:
                    repos.add(h.repo)
                findings.append(_finding_from_hit(rule, pack, q, scoped, h))

    finished_at = dt.datetime.now(dt.timezone.utc).isoformat()

    return GithubScanReport(
        queried_taxonomies=sorted(queried_taxonomies),
        queries_run=queries_run,
        queries_failed=queries_failed,
        repos_seen=len(repos),
        findings=findings,
        started_at=started_at,
        finished_at=finished_at,
        errors=errors,
    )


def _finding_from_hit(rule: Rule, pack: RulePack, q: GithubQuery, scoped_query: str, h: GhHit) -> GithubFinding:
    return GithubFinding(
        rule_id=rule.id,
        rule_title=rule.title,
        taxonomy=pack.taxonomy,
        severity=rule.severity,
        category=rule.category,
        repo=h.repo,
        path=h.path,
        url=h.url,
        query=scoped_query,
        language=q.language,
        fragments=h.fragments,
        related_tags=list(rule.related_tags),
        mitre_attack=list(rule.mitre_attack),
        owasp_llm=list(rule.owasp_llm),
        taxonomy_uuid=rule.taxonomy_uuid,
        references=list(rule.references),
        description=rule.description,
    )
