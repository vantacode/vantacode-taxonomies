---
name: vantacode-scan
description: Scan the current project (or a remote GitHub repo) against the VantaCode DKC, OFA, MBT, governance, and sensitivity taxonomies. Use whenever the user asks to "scan", "audit", "check the repo", "look for DKC issues", "look for OFA framings", "find LLM fingerprints", "review for shipped-without-understanding code", "produce a STIX bundle of findings", or before any commit / PR that touches application code.
---

# vantacode-scan

This skill runs the **VantaCode reference scanner** (`examples/scanner/` in
[vantacode/vantacode-taxonomies](https://github.com/vantacode/vantacode-taxonomies))
against the user's project. It loads the taxonomy-bound rule packs from
`scanner-rules/` and emits findings as JSON, CSV, or STIX 2.1.

The scanner covers **114+ rules** across:

- `vantacode-dkc-rules` — 56 Dunning-Kruger Coding rules (comment forensics, LLM fingerprints, security anti-patterns, outdated versions, developer signals, infrastructure red flags, social signals)
- `vantacode-ofa-techniques` — 20 Observation Framing Attack patterns
- `vantacode-mbt-techniques` — selected Malicious Behaviors Taxonomy detections
- `vantacode-governance` — file-presence governance baseline
- `vantacode-domain` — domain category classification heuristics
- `vantacode-sensitivity` — PII / PHI / financial / credential indicators
- `vantacode-status` — lifecycle inference

## When to use this skill

Invoke this skill when the user:

- asks to scan / audit / review their code
- asks about DKC, OFA, MBT, prompt-injection sinks, hand-rolled auth, or "what is this code doing"
- is about to commit, push, or open a PR that touches application code
- asks for a STIX bundle, MISP-importable output, or a governance report
- mentions any of: `dkc`, `ofa`, `vantacode`, `taxonomy scan`, `LLM fingerprints`, `observation framing`

This skill is also installable as a **pre-commit hook** so it runs automatically on every commit. See the Installation section.

## How to run the scanner

The scanner ships as a regular Python package powered by [uv](https://docs.astral.sh/uv/). The skill assumes `uv` is on the user's `$PATH`. If it isn't, install it first:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Running against the current project

If the user's project already has the scanner cloned (e.g. as a submodule, or via the install script in `examples/claude-skill/`), use the wrapper:

```bash
~/.claude/skills/vantacode-scan/scripts/run-scan.sh \
    --source . \
    --severity high \
    --format json \
    --out .vantacode-scan.json
```

If the scanner is **not** yet on disk, clone it once into a cache directory and run:

```bash
mkdir -p ~/.cache/vantacode
test -d ~/.cache/vantacode/vantacode-taxonomies || \
    git clone --depth 1 https://github.com/vantacode/vantacode-taxonomies.git ~/.cache/vantacode/vantacode-taxonomies

uv run --project ~/.cache/vantacode/vantacode-taxonomies/examples/scanner \
       vantacode-scan --source "$(pwd)" --severity high --format json
```

### Common invocations

```bash
# Quick local scan, JSON to stdout
vantacode-scan -s .

# Only DKC + OFA, fail the run on any high or critical finding (good for CI)
vantacode-scan -s . \
  --only vantacode-dkc-rules \
  --only vantacode-ofa-techniques \
  --severity high --fail-on high \
  -f json -o .vantacode-scan.json

# CSV report for spreadsheet review
vantacode-scan -s . -f csv -o vantacode-scan.csv

# STIX 2.1 bundle for MISP import
vantacode-scan -s . -f stix -o vantacode-scan.stix.json --severity medium

# Scan a remote repo without cloning manually
vantacode-scan -s vantacode/vantacode-taxonomies -f json -o /tmp/scan.json
```

## How to interpret the output

For each finding, the scanner emits:

- `rule_id` — stable identifier (e.g. `CMT-007`, `OFA-003`, `GOV-SEC-001`)
- `taxonomy` — the VantaCode namespace (`vantacode-dkc-rules`, `vantacode-ofa-techniques`, …)
- `severity` — `info | low | medium | high | critical`
- `file`, `line`, `snippet` — where the rule matched
- `related_tags` — MISP triple-tag references
- `mitre_attack`, `owasp_llm` — cross-framework references
- `taxonomy_uuid` — UUID into the source galaxy cluster (so the finding round-trips back to the canonical knowledge layer)
- `fix` — suggested remediation, when available

When summarizing for the user:

1. Group by `taxonomy` first, then by `severity` (critical → high → medium).
2. Lead with the most actionable critical findings — credential leaks (`SEC-001`, `CMT-007`), unsafe deserialization (`SEC-010`), exposed admin panels (`INF-004`), default credentials (`MBT-3.2`).
3. For OFA findings, surface the `category` and the matched line so the user can decide whether the framing is intentional (their own red-team test fixtures) or accidental.
4. For governance gaps (`GOV-*`), suggest the missing file (`SECURITY.md`, `CODEOWNERS`, etc.) — these are easy wins.
5. For `heuristic` rules with no built-in implementation, present them as "review yourself" items, not as confirmed findings.

## How NOT to use this skill

- Do not invoke this skill on unrelated questions (general programming help, library docs, refactoring requests).
- Do not run the scanner against the user's `$HOME` or other system directories.
- Do not interpret raw scanner output as ground truth — false positives are real, especially for `regex` rules. Always cross-check the matched snippet before recommending a code change.
- Do not run the scanner with `--online` or upload reports to third-party services without explicit user consent.

## Installation

See the README in [`examples/claude-skill/`](../README.md) for full install instructions, including:

- Per-project install (`.claude/skills/vantacode-scan/`)
- Global install (`~/.claude/skills/vantacode-scan/`)
- Pre-commit hook install (standalone or via the `pre-commit` framework)
- CI install (GitHub Actions snippet)
