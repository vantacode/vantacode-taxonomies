# VantaCode Scanner Rules

This directory contains **machine-readable scanner rules** that bind VantaCode taxonomies and galaxies to concrete detections (regex, manifest checks, file presence/absence, glob counts, heuristic markers). The example scanner under [`examples/scanner/`](../examples/scanner/) consumes these YAML files to scan local directories or cloned GitHub repositories and emit findings as **JSON, CSV, or STIX 2.1**.

The rules are intentionally **separate from the taxonomies themselves**:

- The taxonomies (e.g. [`vantacode-dkc/`](../vantacode-dkc/), [`vantacode-ofa/`](../vantacode-ofa/)) and galaxies (e.g. [`clusters/vantacode-dkc-rules.json`](../clusters/vantacode-dkc-rules.json)) are the canonical, MISP-compatible knowledge layer. They describe **what** a finding means.
- The scanner rules in this directory describe **how** to find one. Each rule file declares a `taxonomy` and binds rule IDs (e.g. `CMT-001`, `OFA-003`, `GOV-SEC-001`) to detections that operate on file content.

This split lets the taxonomy data stay tool-neutral (CC0) while the scanner rules and the example scanner can evolve independently under the BSD-2-Clause portion of the repo.

---

## Rule Packs

| File | Taxonomy / Galaxy | Rules |
|------|-------------------|-------|
| [`dkc.yaml`](dkc.yaml) | `vantacode-dkc-rules` | All 56 DKC detection rules across 7 weighted categories (comment forensics, LLM fingerprints, security anti-patterns, outdated versions, developer signals, infrastructure red flags, social signals). |
| [`ofa.yaml`](ofa.yaml) | `vantacode-ofa-techniques` | All 20 Observation Framing Attack techniques as prompt-text patterns. |
| [`mbt.yaml`](mbt.yaml) | `vantacode-mbt-techniques` | Selected MBT techniques with reliable static signals (eval-aware code, exposed control panels, default creds, exposed model weights, ML supply-chain typosquats). |
| [`governance.yaml`](governance.yaml) | `vantacode-governance` | Binary file-presence checks for documentation, branch protection, CI/CD, security, and code-quality predicates. |
| [`domain.yaml`](domain.yaml) | `vantacode-domain` | Heuristic classification rules that suggest domain category tags from imports and dependency manifests. |
| [`sensitivity.yaml`](sensitivity.yaml) | `vantacode-sensitivity` | PII / PHI / financial / credential indicator patterns. |
| [`status.yaml`](status.yaml) | `vantacode-status` | Lifecycle inference (scaffold / deprecated / active). |
| [`schema.json`](schema.json) | — | JSON Schema describing the rule file format. |

---

## Rule File Format

Every rule file is a YAML document with this top-level shape:

```yaml
taxonomy: vantacode-dkc-rules            # required — namespace this pack binds to
version: 1                               # required
description: "..."                       # optional
source_galaxy: clusters/...json          # optional — provenance pointer

default_target:                          # optional — globs/excludes inherited by all rules
  globs: ["**/*.py", "**/*.js"]
  exclude_globs: ["**/.git/**", "**/node_modules/**"]

rules:
  - id: CMT-001                          # required — stable rule id
    title: "LLM Chat Response Left as Comments"
    severity: medium                     # info|low|medium|high|critical|variable
    category: comment-forensics
    category_weight: 0.10
    taxonomy_uuid: e149b57b-...          # optional — UUID of source cluster value
    related_tags:                        # optional — triple-tag references
      - 'vantacode-mbt:adversarial-input-vulnerabilities="prompt-injection"'
    mitre_attack: ["T1497"]              # optional
    owasp_llm: ["LLM01"]                 # optional
    references: ["https://..."]          # optional
    fix: "Rewrite or remove the comment..."
    target:                              # optional — overrides default_target
      globs: ["**/*.py"]
    detection:                           # required
      type: regex                        # see "Detection types" below
      flags: [ignorecase, multiline]
      patterns:
        - "^\\s*(?:#|//).*here is the code"
      min_matches: 1
```

### Detection types

| `type` | Inputs | Trigger condition |
|--------|--------|-------------------|
| `regex` | `patterns`, `flags`, `min_matches` | One or more patterns match against file content. |
| `file_exists` | `missing_paths` (interpreted as "expected to exist") | At least one matching path exists. |
| `file_missing` | `missing_paths` | None of the listed paths exist (governance gaps). |
| `glob_count` | `patterns`, `min_count` / `max_count` | Files matching the patterns exceed `min_count` or fall below `max_count`. |
| `manifest` | `manifest_files`, `manifest_check` | Built-in named check parses the manifest (e.g. `eol_runtime`, `unpinned_deps`, `typosquat`). |
| `secret_scan` | — | Built-in scanner runs the high-precision secret pattern set. |
| `json_path` | `manifest_files`, `json_path` | A JSON path expression matches inside the listed files. |
| `heuristic` | `notes` | Marker for follow-up logic. The example scanner reports these as advisory unless a built-in heuristic exists. |

The full schema lives in [`schema.json`](schema.json).

---

## How the Scanner Uses These Rules

The example scanner in [`examples/scanner/`](../examples/scanner/) loads every YAML file in this directory at startup, compiles the regex patterns, and runs them against the target tree. Findings are mapped back to:

- **VantaCode taxonomy tags** — e.g. a `CMT-001` hit emits `vantacode-dkc:comment-forensics="CMT-001"` and any `related_tags` from the rule.
- **MISP triple-tag form** — for direct ingest into MISP events.
- **STIX 2.1 indicator + sighting bundles** — using the `taxonomy_uuid` as the indicator's `external_references` source.
- **CSV rows** — one per finding for spreadsheet review.

See the scanner README for invocation, output schemas, and integration recipes.

---

## Adding or Modifying Rules

1. Pick the right pack (or create a new one — name it `<taxonomy>.yaml`).
2. Add a rule with a stable `id` and a clear `severity`.
3. Reference the source taxonomy or galaxy entry via `taxonomy_uuid` and `related_tags` so findings round-trip back to the canonical knowledge layer.
4. Validate against [`schema.json`](schema.json):
   ```bash
   uv run --with jsonschema --with pyyaml python -c "import json,yaml,jsonschema,sys; jsonschema.validate(yaml.safe_load(open(sys.argv[1])), json.load(open('scanner-rules/schema.json')))" scanner-rules/dkc.yaml
   ```
5. Smoke-test with the example scanner against this repository:
   ```bash
   uv run examples/scanner/vantacode_scanner --source . --format json --out /tmp/scan.json
   ```

Rules are intentionally conservative — false positives are the failure mode that destroys trust in scanners. When in doubt, mark the rule `severity: info` and tighten the regex.
