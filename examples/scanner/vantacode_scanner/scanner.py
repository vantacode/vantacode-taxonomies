"""Core scan engine.

Walks a target tree, runs every applicable rule against every applicable
file, and yields `Finding` objects. Detection backends are intentionally
simple — readability over cleverness.
"""

from __future__ import annotations

import fnmatch
import json
import re
import uuid
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Iterable

from .rules import Rule, RulePack


# ── Built-in pattern banks for the secret_scan and manifest detection types ──

_SECRET_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("aws-access-key",     re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("aws-secret-key",     re.compile(r"(?i)\baws_secret_access_key\s*[:=]\s*['\"]?[A-Za-z0-9/+=]{40}\b")),
    ("openai-key",         re.compile(r"\bsk-[A-Za-z0-9]{20,}\b")),
    ("anthropic-key",      re.compile(r"\bsk-ant-(?:api|admin)\d{2}-[A-Za-z0-9_\-]{60,}\b")),
    ("hf-token",           re.compile(r"\bhf_[A-Za-z0-9]{30,}\b")),
    ("github-token",       re.compile(r"\bghp_[A-Za-z0-9]{30,}\b")),
    ("github-app-token",   re.compile(r"\b(?:ghu|ghs|ghr|gho)_[A-Za-z0-9]{30,}\b")),
    ("gcp-service-acct",   re.compile(r'"type"\s*:\s*"service_account"')),
    ("private" "-key-header", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA |PGP )?" r"PRIVATE KEY-----")),
    ("jwt",                re.compile(r"\beyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\b")),
    ("slack-token",        re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b")),
    ("stripe-secret",      re.compile(r"\bsk_live_[A-Za-z0-9]{24,}\b")),
]

# Conservative known-bad / common LLM-hallucinated package names. The list is
# illustrative — production use would point at a proper feed.
_HALLUCINATED_PYTHON: set[str] = {
    "py-llm-utils",
    "openai-utils",
    "anthropic-tools",
    "langchain-core-utils",
    "fastapi-secure",
    "pydantic-extra",
    "uvicorn-prod",
}

_TYPOSQUAT_PYTHON: dict[str, str] = {
    "requets": "requests",
    "urllib": "urllib3",
    "beatifulsoup4": "beautifulsoup4",
    "pythn-dateutil": "python-dateutil",
    "python-jwt": "PyJWT",
    "djano": "django",
    "tensorlfow": "tensorflow",
    "transformer": "transformers",
}

_ML_TYPOSQUAT_PYTHON: dict[str, str] = {
    "tensorlfow": "tensorflow",
    "transformer": "transformers",
    "scikit-lern": "scikit-learn",
    "pytorch-cpu": "torch",
    "openai-py": "openai",
}

_EOL_RUNTIMES_PY: set[str] = {"3.6", "3.7", "3.8"}
_EOL_RUNTIMES_NODE: set[str] = {"10", "12", "14", "16"}


# ── Findings ─────────────────────────────────────────────────────────────────

_SEVERITY_RANK = {"info": 0, "low": 1, "medium": 2, "high": 3, "critical": 4, "variable": 2}


@dataclass
class Finding:
    rule_id: str
    rule_title: str
    taxonomy: str
    severity: str
    category: str | None
    file: str
    line: int | None
    snippet: str | None
    detection_type: str
    related_tags: list[str] = field(default_factory=list)
    mitre_attack: list[str] = field(default_factory=list)
    owasp_llm: list[str] = field(default_factory=list)
    taxonomy_uuid: str | None = None
    references: list[str] = field(default_factory=list)
    fix: str | None = None
    finding_uuid: str = field(default_factory=lambda: str(uuid.uuid4()))

    def to_dict(self) -> dict:
        return asdict(self)

    def severity_rank(self) -> int:
        return _SEVERITY_RANK.get(self.severity, 0)


@dataclass
class ScanReport:
    source: str
    scanned_files: int
    findings: list[Finding]
    skipped_rules: list[str]

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


# ── Walk + dispatch ──────────────────────────────────────────────────────────

def _matches_any(path: str, globs: Iterable[str]) -> bool:
    for g in globs:
        if fnmatch.fnmatch(path, g):
            return True
    return False


def _iter_files(root: Path, exclude_globs: list[str]) -> Iterable[Path]:
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        rel = p.relative_to(root).as_posix()
        if any(fnmatch.fnmatch(rel, g) for g in exclude_globs):
            continue
        try:
            if p.stat().st_size > 2_000_000:  # 2 MB hard cap
                continue
        except OSError:
            continue
        yield p


def _read_text(p: Path) -> str | None:
    try:
        return p.read_text(encoding="utf-8", errors="replace")
    except (OSError, UnicodeDecodeError):
        return None


def _line_for_offset(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def _snippet(text: str, offset: int, end: int, *, ctx: int = 80) -> str:
    start = max(0, offset - ctx)
    finish = min(len(text), end + ctx)
    return text[start:finish].replace("\n", " ⏎ ")[:300]


# ── Detection backends ──────────────────────────────────────────────────────

def _scan_regex(rule: Rule, root: Path) -> list[Finding]:
    findings: list[Finding] = []
    for f in _iter_files(root, rule.exclude_globs):
        rel = f.relative_to(root).as_posix()
        if rule.target_globs and not _matches_any(rel, rule.target_globs):
            continue
        text = _read_text(f)
        if text is None:
            continue
        hits = 0
        for pat in rule.compiled_patterns:
            for m in pat.finditer(text):
                hits += 1
                findings.append(_finding_from_rule(
                    rule, file=rel,
                    line=_line_for_offset(text, m.start()),
                    snippet=_snippet(text, m.start(), m.end()),
                ))
                if hits >= 50:  # cap per file
                    break
            if hits >= 50:
                break
    return findings


def _scan_file_missing(rule: Rule, root: Path) -> list[Finding]:
    for path_glob in rule.missing_paths:
        for _ in root.glob(path_glob):
            return []  # at least one expected file exists
    return [_finding_from_rule(
        rule, file="<repo root>", line=None,
        snippet=f"none of: {', '.join(rule.missing_paths[:6])}",
    )]


def _scan_file_exists(rule: Rule, root: Path) -> list[Finding]:
    for path_glob in rule.missing_paths:
        for hit in root.glob(path_glob):
            return [_finding_from_rule(
                rule, file=hit.relative_to(root).as_posix(),
                line=None, snippet=f"matched {path_glob}",
            )]
    return []


def _scan_glob_count(rule: Rule, root: Path) -> list[Finding]:
    matches: list[str] = []
    for g in rule.raw_patterns:
        for hit in root.glob(g):
            if hit.is_file():
                matches.append(hit.relative_to(root).as_posix())
    if rule.min_count is not None and len(matches) >= rule.min_count:
        return [_finding_from_rule(
            rule, file=matches[0], line=None,
            snippet=f"{len(matches)} files match (>= {rule.min_count})",
        )]
    if rule.max_count is not None and len(matches) > rule.max_count:
        return [_finding_from_rule(
            rule, file=matches[0], line=None,
            snippet=f"{len(matches)} files match (> {rule.max_count})",
        )]
    return []


def _scan_secret(rule: Rule, root: Path) -> list[Finding]:
    findings: list[Finding] = []
    for f in _iter_files(root, rule.exclude_globs or ["**/.git/**"]):
        rel = f.relative_to(root).as_posix()
        text = _read_text(f)
        if text is None:
            continue
        for label, pat in _SECRET_PATTERNS:
            for m in pat.finditer(text):
                findings.append(_finding_from_rule(
                    rule, file=rel,
                    line=_line_for_offset(text, m.start()),
                    snippet=f"[{label}] " + _snippet(text, m.start(), m.end()),
                ))
                break  # one per pattern per file is plenty
    return findings


def _scan_manifest(rule: Rule, root: Path) -> list[Finding]:
    if rule.manifest_check is None:
        return []
    findings: list[Finding] = []
    for mf in rule.manifest_files:
        for path in root.glob(f"**/{mf}"):
            text = _read_text(path)
            if text is None:
                continue
            rel = path.relative_to(root).as_posix()
            findings.extend(_dispatch_manifest_check(rule, rel, text))
    return findings


def _dispatch_manifest_check(rule: Rule, rel: str, text: str) -> list[Finding]:
    check = rule.manifest_check
    out: list[Finding] = []

    if check == "hallucinated_packages":
        for name in _HALLUCINATED_PYTHON:
            if re.search(rf"(?im)^\s*{re.escape(name)}\b", text):
                out.append(_finding_from_rule(rule, file=rel, line=None, snippet=f"hallucinated dep: {name}"))

    elif check == "typosquat":
        for bad, good in _TYPOSQUAT_PYTHON.items():
            if re.search(rf"(?im)^\s*{re.escape(bad)}\b", text):
                out.append(_finding_from_rule(rule, file=rel, line=None, snippet=f"typosquat: {bad} (did you mean {good}?)"))

    elif check == "ml_typosquat":
        for bad, good in _ML_TYPOSQUAT_PYTHON.items():
            if re.search(rf"(?im)^\s*{re.escape(bad)}\b", text):
                out.append(_finding_from_rule(rule, file=rel, line=None, snippet=f"ml typosquat: {bad} (did you mean {good}?)"))

    elif check == "unpinned_deps":
        # naive: requirements.txt entries with no `==`, no version pin
        if rel.endswith("requirements.txt"):
            for i, line in enumerate(text.splitlines(), start=1):
                line_clean = line.strip()
                if not line_clean or line_clean.startswith("#"):
                    continue
                if "==" not in line_clean and ">=" not in line_clean and "~=" not in line_clean:
                    out.append(_finding_from_rule(rule, file=rel, line=i, snippet=line_clean))

    elif check == "eol_runtime":
        m = re.search(r"python_requires\s*=\s*['\"][^'\"]*?(\d\.\d+)", text)
        if m and m.group(1) in _EOL_RUNTIMES_PY:
            out.append(_finding_from_rule(rule, file=rel, line=None, snippet=f"python {m.group(1)} is EOL"))
        m = re.search(r'"node"\s*:\s*"[^"]*?(\d+)"', text)
        if m and m.group(1) in _EOL_RUNTIMES_NODE:
            out.append(_finding_from_rule(rule, file=rel, line=None, snippet=f"node {m.group(1)} is EOL"))
        for line in text.splitlines():
            line_clean = line.strip()
            if line_clean in _EOL_RUNTIMES_PY:
                out.append(_finding_from_rule(rule, file=rel, line=None, snippet=f"runtime pinned to EOL {line_clean}"))

    elif check == "eol_framework":
        # signal-only — flags django<3, flask<2, fastapi<0.90
        for pat, label in [
            (r"(?im)^\s*django\s*[=~<>]+\s*([12]\.)", "django<3"),
            (r"(?im)^\s*flask\s*[=~<>]+\s*([01]\.)", "flask<2"),
            (r"(?im)^\s*fastapi\s*[=~<>]+\s*0\.([0-8]\d|0)", "fastapi<0.90"),
        ]:
            if re.search(pat, text):
                out.append(_finding_from_rule(rule, file=rel, line=None, snippet=label))

    elif check == "competing_deps":
        groups = [
            ("requests", "httpx", "urllib3"),
            ("flask", "fastapi", "django"),
            ("sqlalchemy", "tortoise-orm", "peewee"),
        ]
        for group in groups:
            present = [g for g in group if re.search(rf"(?im)^\s*{re.escape(g)}\b", text)]
            if len(present) >= 2:
                out.append(_finding_from_rule(rule, file=rel, line=None, snippet=f"competing deps: {', '.join(present)}"))

    elif check == "abandoned_packages":
        # static deny-list of known abandoned packages — illustrative only
        abandoned = {"python-dateutil2", "moment", "request", "bower", "gulp", "grunt"}
        for name in abandoned:
            if re.search(rf"(?im)^\s*[\"']?{re.escape(name)}[\"']?\b", text):
                out.append(_finding_from_rule(rule, file=rel, line=None, snippet=f"abandoned: {name}"))

    elif check == "cve_audit":
        # advisory only — actual CVE lookup is opt-in via --online (not implemented in example)
        out.append(_finding_from_rule(
            rule, file=rel, line=None,
            snippet="CVE audit requires --online (not enabled in this run)",
        ))

    return out


# ── Heuristic stub: heuristic rules without a built-in implementation ───────

_BUILTIN_HEURISTICS: dict[str, "callable"] = {}


def _scan_heuristic(rule: Rule, root: Path) -> list[Finding]:
    impl = _BUILTIN_HEURISTICS.get(rule.id)
    if impl is None:
        return []  # advisory only
    return impl(rule, root)


# ── Dispatcher ───────────────────────────────────────────────────────────────

_BACKENDS = {
    "regex":         _scan_regex,
    "file_missing":  _scan_file_missing,
    "file_exists":   _scan_file_exists,
    "glob_count":    _scan_glob_count,
    "secret_scan":   _scan_secret,
    "manifest":      _scan_manifest,
    "heuristic":     _scan_heuristic,
}


def _finding_from_rule(rule: Rule, *, file: str, line: int | None, snippet: str | None) -> Finding:
    return Finding(
        rule_id=rule.id,
        rule_title=rule.title,
        taxonomy=rule.taxonomy,
        severity=rule.severity,
        category=rule.category,
        file=file,
        line=line,
        snippet=snippet,
        detection_type=rule.detection_type,
        related_tags=list(rule.related_tags),
        mitre_attack=list(rule.mitre_attack),
        owasp_llm=list(rule.owasp_llm),
        taxonomy_uuid=rule.taxonomy_uuid,
        references=list(rule.references),
        fix=rule.fix,
    )


def scan(root: Path, packs: list[RulePack], *, only_severity: str | None = None) -> ScanReport:
    findings: list[Finding] = []
    skipped: list[str] = []

    files_seen = sum(1 for _ in _iter_files(root, ["**/.git/**"]))

    min_rank = _SEVERITY_RANK.get(only_severity or "info", 0)

    for pack in packs:
        for rule in pack.rules:
            backend = _BACKENDS.get(rule.detection_type)
            if backend is None:
                skipped.append(f"{rule.id} ({rule.detection_type})")
                continue
            if _SEVERITY_RANK.get(rule.severity, 0) < min_rank:
                continue
            try:
                findings.extend(backend(rule, root))
            except Exception as e:  # noqa: BLE001 — never let one rule kill the run
                skipped.append(f"{rule.id} (error: {type(e).__name__})")

    return ScanReport(
        source=str(root),
        scanned_files=files_seen,
        findings=findings,
        skipped_rules=skipped,
    )


def report_to_json(report: ScanReport) -> str:
    return json.dumps({
        "source": report.source,
        "scanned_files": report.scanned_files,
        "summary": {
            "total": len(report.findings),
            "by_severity": report.summary_by_severity(),
            "by_taxonomy": report.summary_by_taxonomy(),
        },
        "findings": [f.to_dict() for f in report.findings],
        "skipped_rules": report.skipped_rules,
    }, indent=2, default=str)
