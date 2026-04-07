# vantacode-scanner

Reference implementation of a scanner that loads VantaCode taxonomy rules from
[`scanner-rules/`](../../scanner-rules/) and runs them against a local
directory or cloned GitHub repository, emitting findings as **JSON, CSV, or
STIX 2.1**.

The scanner is intentionally a small, readable example. It is not meant to
replace dedicated SAST or SCA tools — it is meant to demonstrate how to
operationalize VantaCode taxonomies (DKC, OFA, MBT, governance, sensitivity,
domain, status) as concrete repository-level checks that round-trip back to
MISP-compatible tags and STIX 2.1 indicators.

---

## Quick start

The scanner is packaged as a regular Python project. The easiest way to run it
is with [uv](https://docs.astral.sh/uv/):

```bash
# scan a local directory, default JSON output to stdout
uv run --project examples/scanner vantacode-scan --source .

# scan a GitHub repository (clone is shallow + ephemeral)
uv run --project examples/scanner vantacode-scan \
    --source https://github.com/vantacode/vantacode-taxonomies \
    --format json --out scan.json

# owner/repo shorthand also works
uv run --project examples/scanner vantacode-scan -s vantacode/vantacode-taxonomies

# CSV output
uv run --project examples/scanner vantacode-scan -s . -f csv -o scan.csv

# STIX 2.1 bundle (no extra deps required; if `stix2` is installed it is used
# for ingest validation)
uv run --project examples/scanner vantacode-scan -s . -f stix -o scan.stix.json
```

If you prefer not to use `uv`, the package is a normal `pyproject.toml`
project — `pip install -e examples/scanner` and then `vantacode-scan ...`.

You can also run it without installing anything by exporting `PYTHONPATH`:

```bash
PYTHONPATH=examples/scanner python -m vantacode_scanner --source . --format json
```

---

## What it does

1. Loads every `*.yaml` rule pack under `--rules` (defaults to the repo's
   `scanner-rules/` directory).
2. Resolves the source — local directory, full GitHub URL, or `owner/repo`
   shorthand. Remote sources are cloned shallowly into a temp directory and
   removed after the scan.
3. Walks the source tree, applies each rule's target globs/excludes, and
   dispatches the rule to its detection backend:
    - `regex` — content regex against text files (skips files > 2 MB)
    - `file_missing` — flags governance gaps when no expected file exists
    - `file_exists` — emits info findings when a file is present
    - `glob_count` — flags when matching files exceed `min_count`
    - `secret_scan` — built-in high-precision secret pattern set
    - `manifest` — built-in named checks (`hallucinated_packages`,
      `typosquat`, `eol_runtime`, `eol_framework`, `unpinned_deps`,
      `competing_deps`, `abandoned_packages`, `cve_audit`, `ml_typosquat`)
    - `heuristic` — advisory; reports the rule and its `notes` so a downstream
      tool can act on it
4. Aggregates findings into a `ScanReport` and serializes to the requested
   format.

---

## CLI reference

```
Usage: vantacode-scan [OPTIONS]

Options:
  -s, --source TEXT               Local directory, GitHub URL, or owner/repo shorthand.  [required]
  -r, --rules PATH                Directory containing scanner-rules YAML files.
                                  [default: ../../scanner-rules]
  -f, --format [csv|json|stix]    Output format.  [default: json]
  -o, --out PATH                  Output file (required for csv/stix; stdout for json by default).
  --severity [info|low|medium|high|critical]
                                  Minimum severity to report.  [default: info]
  --only TEXT                     Restrict to one or more taxonomies (repeatable).
  --fail-on [never|low|medium|high|critical]
                                  Exit non-zero if any finding meets or exceeds this severity.
                                  [default: never]
  -q, --quiet                     Suppress the human summary.
  --help                          Show this message and exit.
```

### Pre-commit / CI usage

The `--fail-on` flag turns the scanner into a CI gate. A typical pre-commit or
CI invocation:

```bash
vantacode-scan --source . --severity high --fail-on critical --quiet \
               --only vantacode-dkc-rules \
               --only vantacode-ofa-techniques \
               --format json --out .vantacode-scan.json
```

Exit codes:

| Code | Meaning |
|------|---------|
| `0`  | Scan completed; no findings reached `--fail-on` threshold |
| `1`  | Findings reached the `--fail-on` threshold (gate failure) |
| `2`  | Configuration error (missing rules dir, no rule packs loaded) |

---

## Output formats

### JSON

```json
{
  "source": "/path/to/repo",
  "scanned_files": 95,
  "summary": {
    "total": 411,
    "by_severity": { "critical": 48, "high": 42, "medium": 17, "info": 301, "low": 3 },
    "by_taxonomy": { "vantacode-dkc-rules": 12, "vantacode-ofa-techniques": 55, "..." : 0 }
  },
  "findings": [
    {
      "rule_id": "OFA-001",
      "rule_title": "Negative Null Observation Framing",
      "taxonomy": "vantacode-ofa-techniques",
      "severity": "critical",
      "category": "anti-observation-framing",
      "file": "prompts/system.txt",
      "line": 14,
      "snippet": "...nothing is being logged...",
      "detection_type": "regex",
      "related_tags": ["vantacode-mbt:observation-dependent-behavior=\"eval-benchmark-detection\""],
      "mitre_attack": ["T1497"],
      "owasp_llm": ["LLM01"],
      "taxonomy_uuid": "320f4c06-b99f-5d4f-ba7a-0e0184551313",
      "fix": null,
      "finding_uuid": "...uuid4..."
    }
  ],
  "skipped_rules": []
}
```

### CSV

One row per finding with the columns:
`rule_id, rule_title, taxonomy, severity, category, file, line, snippet, detection_type, related_tags, mitre_attack, owasp_llm, taxonomy_uuid, fix`.

### STIX 2.1

The bundle contains:

- one `identity` object representing the VantaCode Scanner
- one `indicator` per finding, carrying the rule ID + VantaCode triple-tag
  labels and an `external_reference` to the source galaxy UUID and any MITRE
  ATT&CK technique IDs
- one `sighting` per indicator, anchored to the scanner identity

The bundle round-trips into MISP via the STIX 2.1 import path and works in any
TAXII-aware tool. The scanner emits the bundle as plain JSON to avoid making
`stix2` a hard dependency, but if `stix2` is installed in the environment the
import succeeds and tools that load the bundle through `stix2.parse(...)` will
validate it.

---

## Rule packs

The scanner doesn't ship rules of its own — it loads them from
[`scanner-rules/`](../../scanner-rules/). The current packs are:

- `dkc.yaml` — 56 DKC rules (comment forensics, LLM fingerprints, security
  anti-patterns, outdated versions, developer signals, infrastructure red
  flags, social signals)
- `ofa.yaml` — 20 OFA techniques (observation framing attack patterns)
- `mbt.yaml` — selected MBT techniques with reliable static signals
- `governance.yaml` — file-presence governance baseline
- `domain.yaml` — domain category classification heuristics
- `sensitivity.yaml` — PII / PHI / financial / credential indicators
- `status.yaml` — lifecycle inference

See [`scanner-rules/README.md`](../../scanner-rules/README.md) for the rule
file format and the schema.

---

## Limitations and design notes

- **No auth, no API.** GitHub clones use the `git` binary on PATH and only
  shallow-clone (`--depth 1`). Private repos work if the local git already
  has credentials.
- **Single-file regex scope.** Rules don't reach across files. Cross-file
  resolution (LLM-001, LLM-003) is intentionally left as `heuristic` so a
  follow-up implementation can add AST-based passes.
- **No network calls by default.** Manifest checks that need a registry or
  CVE database (`cve_audit`) emit advisory findings unless extended.
- **2 MB file cap.** The walker skips files larger than 2 MB to keep scans
  fast. Most binary blobs are excluded by glob anyway.
- **Severity mapping.** STIX bundle severities use the indicator labels
  (`severity:critical`, `severity:high`, …) so consumers can re-map to their
  own scoring without losing the original VantaCode value.

---

## Example: scan a remote repo and feed STIX into MISP

```bash
uv run --project examples/scanner vantacode-scan \
    --source https://github.com/some-owner/some-repo \
    --format stix --out /tmp/some-repo.stix.json \
    --severity high

# import the bundle into MISP
curl -X POST https://misp.example.org/events/upload_stix/2 \
     -H "Authorization: $MISP_KEY" \
     -H "Content-Type: application/json" \
     --data @/tmp/some-repo.stix.json
```
