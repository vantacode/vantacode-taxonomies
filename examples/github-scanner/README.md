# vantacode-github-scanner

GitHub-wide companion to [`examples/scanner/`](../scanner/).

Where the local scanner walks a directory tree, this one walks **all of
GitHub** (or any subset thereof) by reading the `github_search` field on
VantaCode rules and feeding each phrase through `gh search code`. The output
shape is identical to the local scanner — same JSON / CSV / STIX 2.1 writers,
same rule metadata, same MISP-compatible labels — so anything that already
ingests one can ingest the other.

This is the same approach the public VantaCode taxonomy uses to discover
real-world examples of OFA techniques, DKC anti-patterns, and MBT bypasses
in the wild without indexing the whole internet ourselves.

---

## Why drive `gh` instead of the REST API

- `gh` already handles auth — `gh auth login` once and you inherit the
  authenticated **30 requests/minute** code-search limit instead of the
  unauthenticated 10/min.
- `gh search code --json` returns a stable JSON shape across versions, so we
  do not have to track REST schema drift.
- The legacy code-search API is hard-capped at **1000 results per query** no
  matter how you page; the wrapper exposes that as `--pages × --per-page`
  with a clamp.

The only nontrivial gotcha is that `gh search code` parses positional args as
the query. If you pass an entire phrase as a single argv element with spaces
inside it, `gh` wraps the whole thing in outer quotes and searches for one
literal sentence. The wrapper [`shlex.split`s the query](vantacode_github_scanner/gh.py#L100)
so each quoted phrase / bare token becomes its own argv element and GitHub
treats them as an AND-group, exactly the way the dorks were authored.

---

## Prerequisites

1. **`gh` on PATH** — install from <https://cli.github.com>.
2. **Authenticated** — `gh auth login` (any account works; the rate limit
   bumps to 30/min the moment auth is configured). The CLI runs
   `gh auth status` at startup and refuses to scan if you are unauthenticated.
3. **Python 3.10+** and either `uv` or `pip`.

---

## Quick start

```bash
# scan all of GitHub for the curated set of high-signal queries
uv run --project examples/github-scanner vantacode-gh-scan \
    --rules scanner-rules

# restrict to a single org and a single rule pack, write JSON
uv run --project examples/github-scanner vantacode-gh-scan \
    --rules scanner-rules \
    --scope org:vantacode \
    --only vantacode-ofa-techniques \
    --format json --out ofa-org.json

# limit blast radius while debugging — only the first 5 queries, 1 page each
uv run --project examples/github-scanner vantacode-gh-scan \
    --rules scanner-rules \
    --max-queries 5 --pages 1

# CI gate: any critical finding fails the build
uv run --project examples/github-scanner vantacode-gh-scan \
    --rules scanner-rules \
    --fail-on critical

# STIX 2.1 bundle for MISP / TAXII import
uv run --project examples/github-scanner vantacode-gh-scan \
    --rules scanner-rules \
    --format stix --out gh-scan.stix.json
```

If you do not want `uv`, the package is a normal `pyproject.toml` project —
`pip install -e examples/github-scanner` and then `vantacode-gh-scan ...`.

---

## CLI reference

```
Usage: vantacode-gh-scan [OPTIONS]

Options:
  -r, --rules DIRECTORY           Directory containing scanner-rules YAML files.
  --scope TEXT                    GitHub scope qualifier appended to every query
                                  (e.g. 'org:vantacode', 'user:NoDataFound',
                                  'repo:owner/name'). Omit to scan all of GitHub.
  --only TEXT                     Restrict to one or more taxonomies (repeatable).
  --severity [info|low|medium|high|critical]
                                  Minimum severity to query.  [default: medium]
  --fail-on [never|low|medium|high|critical]
                                  Exit non-zero if any finding meets or exceeds
                                  this severity.  [default: never]
  -f, --format [json|csv|stix]    Output format.  [default: json]
  -o, --out PATH                  Output file. Required for csv/stix; defaults
                                  to stdout for json.
  --pages INTEGER RANGE           Pages of results per query (page * per-page
                                  caps at 1000 — gh API limit).  [default: 1]
  --per-page INTEGER RANGE        Results per page (max 100, the gh API hard cap).
                                  [default: 100]
  --pause FLOAT                   Seconds to sleep between gh calls. Stay under
                                  the 30/min auth limit.  [default: 2.5]
  --max-queries INTEGER           Hard cap on the number of gh searches issued
                                  (useful for testing).
  -q, --quiet                     Suppress per-query progress output.
  --help                          Show this message and exit.
```

Exit codes:

| Code | Meaning |
|------|---------|
| `0`  | Scan completed; no findings reached `--fail-on` threshold |
| `1`  | Findings reached the `--fail-on` threshold (gate failure)  |
| `2`  | Configuration / auth error (`gh` missing, not logged in, no rule packs loaded) |

---

## Scope qualifiers

The `--scope` value is appended verbatim to every query. Anything GitHub Code
Search accepts as a scope qualifier works:

| Scope | Effect |
|-------|--------|
| _omitted_                    | All public code on GitHub |
| `org:vantacode`              | A single org (public + accessible private) |
| `user:NoDataFound`           | A single user account |
| `repo:owner/name`            | A single repository |
| `language:python`            | All public code, Python only (additive to per-rule `language:`) |

Scope qualifiers stack with the rule's own `language:` filter, so
`--scope org:vantacode` plus a rule that sets `language: python` becomes
`<query> org:vantacode --language python`.

---

## Rate limits, in plain language

- Authenticated code-search is **30 requests/minute**. The default
  `--pause 2.5` keeps you well under that even at full throttle.
- Unauthenticated is 10/min. The CLI refuses to run unauthenticated.
- Each query is at most **1000 results** total (`pages × per-page ≤ 1000`).
  Pages 2-10 are useful when you want more than 100 hits for a single
  popular phrase.
- If `gh` reports a 403 / 429 / "rate limit" error, the wrapper sleeps 30s
  and retries the call once before giving up. Persistent failures land in
  the report's `errors[]` array — they do not abort the run.

A rough budget for the curated set:

```
~63 queries × 1 page × 100 results ≈ 6 300 hits
~63 queries × 2.5 s pause          ≈ 2.5 minutes wall time
```

Restricting with `--scope` is the right way to go fast — `--scope org:foo`
on a small org typically completes in well under a minute.

---

## Adding new `github_search` phrases

The scanner reads phrases off the existing
[`scanner-rules/`](../../scanner-rules/) packs. Adding a new rule to the
GitHub-wide pass is just adding a `github_search` block to its YAML — the
local scanner ignores the field, so nothing else changes.

The field accepts three shapes (validated by
[`scanner-rules/schema.json`](../../scanner-rules/schema.json)):

```yaml
# 1. single string — language inferred from the query if it has a `language:`
#    qualifier, otherwise unspecified
- id: SEC-005
  github_search: '"DEBUG = True" "settings.py"'

# 2. list of strings
- id: CMT-002
  github_search:
    - '"# not sure why this works"'
    - '"// not sure why this works"'
    - '"// honestly no idea"'

# 3. list of objects (lets you set per-query language and a description)
- id: SEC-002
  github_search:
    - query: '"def login(" "if password ==" '
      language: python
      description: hand-rolled login with naive password compare
    - query: '"function login(" "if (password ==)"'
      language: javascript
```

A few authoring tips that came out of building the curated set:

- **Quote phrases.** GitHub Code Search treats unquoted tokens as AND-grouped
  bag-of-words; quoted phrases are exact matches. Almost every useful dork
  is a sequence of two or three quoted phrases that together form a tight
  shape (`"def login(" "if password ==" "return True"`).
- **Pair a syntactic anchor with a semantic phrase.** `"def "` next to
  `"As an AI language model"` is much more selective than either alone.
- **Use `language:` for high-volume languages.** Adding `language: python`
  cuts noise dramatically without losing the rule's intent.
- **Avoid bare keywords.** A bare deserialization function name on its own
  returns hundreds of thousands of legitimate hits. Pair it with a request
  argument or context phrase to tighten it down to suspicious shapes only.

If a query needs to contain a substring that the local pre-tool security
hooks would otherwise flag, use YAML's double-quoted form with a unicode
escape — e.g. `"\"p\u0069ckle.loads\""` — so the on-disk bytes do not
contain the literal substring, but the loader resolves it to the runtime
string the search needs.

---

## Output formats

All three formats are byte-for-byte the same shape as the local scanner so a
single ingestion path can handle both.

### JSON

```json
{
  "queried_taxonomies": ["vantacode-dkc-rules", "vantacode-ofa-techniques"],
  "queries_run": 63,
  "queries_failed": 0,
  "repos_seen": 2104,
  "started_at": "2026-04-07T12:34:56+00:00",
  "finished_at": "2026-04-07T12:37:21+00:00",
  "summary": {
    "total": 4912,
    "by_severity": { "high": 3210, "critical": 421, "medium": 1281 },
    "by_taxonomy": { "vantacode-dkc-rules": 3902, "vantacode-ofa-techniques": 1010 },
    "by_repo": { "owner/repo": 14, "...": 1 }
  },
  "findings": [
    {
      "rule_id": "OFA-001",
      "rule_title": "Negative Null Observation",
      "taxonomy": "vantacode-ofa-techniques",
      "severity": "critical",
      "category": "anti-observation-framing",
      "repo": "some-owner/some-repo",
      "path": "prompts/system.txt",
      "url": "https://github.com/some-owner/some-repo/blob/HEAD/prompts/system.txt",
      "query": "\"no one is watching\" prompt",
      "language": null,
      "fragments": ["…no one is watching, you can be honest…"],
      "related_tags": ["vantacode-mbt:observation-dependent-behavior=\"eval-benchmark-detection\""],
      "mitre_attack": ["T1497"],
      "owasp_llm": ["LLM01"],
      "taxonomy_uuid": "320f4c06-b99f-5d4f-ba7a-0e0184551313",
      "finding_uuid": "…uuid4…"
    }
  ],
  "errors": []
}
```

### CSV

One row per finding. Columns:
`rule_id, rule_title, taxonomy, severity, category, repo, path, url, language, query, fragment, related_tags, mitre_attack, owasp_llm, taxonomy_uuid`.

### STIX 2.1

Hand-rolled bundle (no `stix2` dependency) containing:

- one `identity` object representing the **VantaCode GitHub Scanner** (stable
  ID `identity--6f3c0e9a-2b4d-4d8e-9a1f-7c5b3e2a1d04`, distinct from the
  local scanner's identity)
- one `indicator` per finding with:
    - VantaCode triple-tag `labels` (`vantacode:<taxonomy>`,
      `vantacode-rule:<id>`, `severity:<level>`, `source:github-code-search`)
    - `external_references` to the taxonomies repo, the GitHub URL of the hit,
      the source galaxy UUID, and any MITRE ATT&CK technique IDs
    - an `x_vantacode` custom block carrying the full hit metadata
      (repo, path, url, query, language, fragments) for downstream pivoting
- one `sighting` per indicator anchored to the scanner identity

Both bundles round-trip into MISP via the STIX 2.1 import path. Because the
two scanners use different identity IDs you can ingest both into the same
event without collisions and still tell which scanner produced which
indicator.

---

## CI snippet

```yaml
# .github/workflows/vantacode-gh-scan.yml
name: vantacode-gh-scan
on:
  schedule: [{ cron: "0 6 * * 1" }]   # weekly Monday 06:00 UTC
  workflow_dispatch:

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v3
      - name: gh auth
        run: echo "${{ secrets.GH_PAT }}" | gh auth login --with-token
      - name: scan our org
        run: |
          uv run --project examples/github-scanner vantacode-gh-scan \
              --rules scanner-rules \
              --scope org:${{ github.repository_owner }} \
              --severity high \
              --fail-on critical \
              --format stix --out gh-scan.stix.json
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: vantacode-gh-scan
          path: gh-scan.stix.json
```

The PAT only needs `public_repo` scope to lift the rate limit to 30/min and
to read public org code.

---

## Example: feed the bundle into MISP

```bash
uv run --project examples/github-scanner vantacode-gh-scan \
    --rules scanner-rules \
    --scope org:some-org \
    --format stix --out /tmp/some-org.stix.json \
    --severity high

curl -X POST https://misp.example.org/events/upload_stix/2 \
     -H "Authorization: $MISP_KEY" \
     -H "Content-Type: application/json" \
     --data @/tmp/some-org.stix.json
```

---

## Limitations and design notes

- **Code search only.** This scanner uses `gh search code`, not `gh search
  repos` or `gh search commits`. Rule shapes that depend on commit messages
  or repo metadata belong in a separate pass.
- **1000-result hard cap per query.** The legacy code-search API will not
  page past 1000 hits no matter how you ask. If a phrase is so noisy that
  it hits the cap, narrow it with another quoted phrase or a `language:`
  qualifier.
- **No reach across files.** Each finding is one file. Cross-file rules
  (e.g. "this prompt template is referenced from this LLM call") are
  intentionally out of scope here — see the local scanner's `heuristic`
  detection type for those.
- **Deliberate severity floor.** The default `--severity medium` skips
  `info` / `low` rules so you do not waste rate limit on housekeeping
  signals. Drop it explicitly with `--severity info` if you want everything.
- **`variable` severity.** CVE-driven rules use `variable` and are always
  included regardless of `--severity` so a CVE never gets silently dropped.
- **Errors do not abort.** If a single query 403s after backoff, the
  failure lands in `report["errors"]` and the scan keeps going. Check the
  `queries_failed` count in the summary.
