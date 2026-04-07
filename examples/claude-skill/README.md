# vantacode-scan — Claude Code skill & pre-commit hook

This directory packages the [`examples/scanner/`](../scanner/) reference
implementation as a [Claude Code skill](https://docs.claude.com/en/docs/claude-code/skills),
so Claude can run a VantaCode scan on demand while you develop, and as a
**git pre-commit hook** so the same scan blocks commits with critical or
high-severity findings.

The skill loads the rule packs from
[`scanner-rules/`](../../scanner-rules/) — 114+ rules across DKC, OFA, MBT,
governance, sensitivity, domain, and status — and emits findings as JSON,
CSV, or STIX 2.1.

---

## Contents

```
examples/claude-skill/
├── README.md                       # this file
└── vantacode-scan/
    ├── SKILL.md                    # skill manifest (frontmatter + guidance for Claude)
    └── scripts/
        ├── run-scan.sh             # entry point used by both the skill and the hook
        └── pre-commit              # git pre-commit hook (standalone, no framework needed)
```

The skill is intentionally just a manifest plus a thin wrapper script. It
defers to the scanner package in [`examples/scanner/`](../scanner/) so that
the rules and detection logic stay in one place.

---

## Prerequisites

- **`uv`** — the recommended Python tool runner
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```
  If you don't have (or want) `uv`, the wrapper falls back to
  `python3 -m vantacode_scanner` via `PYTHONPATH`.
- **`git`** — required if the wrapper needs to auto-clone the scanner into
  `~/.cache/vantacode/`.
- **`jq`** *(optional)* — the pre-commit hook uses `jq` to surface critical
  and high-severity findings inline. Without it, the hook still blocks
  the commit and prints the path to the JSON report.

---

## Install the Claude Code skill

Pick **one** of the install paths below. The skill is identical in all
three; the difference is just where the directory lives.

### Per-project install

Use this if you want the skill scoped to a single project (recommended for
projects on shared machines, or if you want the skill to auto-version with
the repo):

```bash
mkdir -p .claude/skills
cp -R path/to/vantacode-taxonomies/examples/claude-skill/vantacode-scan \
      .claude/skills/vantacode-scan
chmod +x .claude/skills/vantacode-scan/scripts/run-scan.sh
```

Claude Code auto-discovers any skill under `.claude/skills/` in the
current working directory.

### Global install (all projects on this machine)

```bash
mkdir -p ~/.claude/skills
cp -R path/to/vantacode-taxonomies/examples/claude-skill/vantacode-scan \
      ~/.claude/skills/vantacode-scan
chmod +x ~/.claude/skills/vantacode-scan/scripts/run-scan.sh
```

### Symlink install (live updates from a checkout)

If you keep a working checkout of `vantacode-taxonomies` on disk and want
the skill to track it:

```bash
mkdir -p ~/.claude/skills
ln -s "$(pwd)/examples/claude-skill/vantacode-scan" \
      ~/.claude/skills/vantacode-scan
```

Now `git pull` in the taxonomies repo updates your skill in place.

### Verify the install

In a Claude Code session, ask:

> Run a vantacode-scan on this directory at severity high.

Claude should pick up the skill and run
`~/.claude/skills/vantacode-scan/scripts/run-scan.sh --source . --severity high`.
The skill description in `SKILL.md` lists the trigger phrases that route
the request here.

---

## Install the pre-commit hook

The hook is a **standalone** bash script — it does not require the
[`pre-commit`](https://pre-commit.com) framework. It only needs `bash`,
`git`, and either `uv` or `python3`.

### Standalone install (single repo)

From inside the repo you want to scan:

```bash
cp path/to/vantacode-taxonomies/examples/claude-skill/vantacode-scan/scripts/pre-commit \
   .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

That's it. On the next `git commit`, the hook will:

1. Resolve the scanner location (env var → submodule → cached clone).
2. Run the scanner against the staged files at the configured severity.
3. Block the commit if any finding meets or exceeds `VANTACODE_FAIL_ON`
   (default: `high`), and print the offending findings inline.

### Configuration (env vars)

| Variable | Default | What it does |
|----------|---------|--------------|
| `VANTACODE_FAIL_ON` | `high` | Severity threshold that blocks the commit. One of `critical`, `high`, `medium`, `low`, `never`. |
| `VANTACODE_SEVERITY` | `medium` | Minimum severity reported by the scanner. Findings below this never appear. |
| `VANTACODE_SKILL_DIR` | `$HOME/.claude/skills/vantacode-scan/scripts` | Where to find `run-scan.sh`. The hook also tries the in-tree path automatically. |
| `VANTACODE_RULES_DIR` | *(scanner default)* | Override the rule pack directory. |
| `VANTACODE_SCANNER_DIR` | *(auto)* | Path to a `vantacode-taxonomies` checkout that contains `examples/scanner/`. |

#### Bypass the hook for a single commit

```bash
VANTACODE_FAIL_ON=never git commit -m "WIP"
```

#### Skip the hook entirely (not recommended)

```bash
git commit --no-verify -m "..."
```

### Pre-commit framework integration

If your project already uses [`pre-commit`](https://pre-commit.com), add a
local hook entry to `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: local
    hooks:
      - id: vantacode-scan
        name: vantacode-scan
        entry: examples/claude-skill/vantacode-scan/scripts/pre-commit
        language: system
        pass_filenames: false
        stages: [commit]
```

Adjust the `entry` path to wherever you copied the hook (e.g.
`.git/hooks/vantacode-scan` or `~/.claude/skills/vantacode-scan/scripts/pre-commit`).

### Install across many repos

To roll the hook out to every git repo on a machine, install it as a
**git template hook**:

```bash
mkdir -p ~/.git-templates/hooks
cp path/to/vantacode-taxonomies/examples/claude-skill/vantacode-scan/scripts/pre-commit \
   ~/.git-templates/hooks/pre-commit
chmod +x ~/.git-templates/hooks/pre-commit
git config --global init.templateDir ~/.git-templates
```

New repos created or cloned after this point will automatically receive
the hook. To install it into existing repos, re-run `git init` inside
each one.

---

## CI install (GitHub Actions)

Drop the scanner straight into a workflow with `uv`. This snippet runs the
DKC + OFA packs and fails the build on any high-or-critical finding,
uploading the JSON report as an artifact.

```yaml
# .github/workflows/vantacode-scan.yml
name: vantacode-scan

on:
  push:
    branches: [main]
  pull_request:

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v3

      - name: Clone vantacode-taxonomies
        run: |
          git clone --depth 1 https://github.com/vantacode/vantacode-taxonomies.git \
            "$RUNNER_TEMP/vantacode-taxonomies"

      - name: Run vantacode-scan
        run: |
          uv run --project "$RUNNER_TEMP/vantacode-taxonomies/examples/scanner" \
            vantacode-scan \
              --source . \
              --rules "$RUNNER_TEMP/vantacode-taxonomies/scanner-rules" \
              --only vantacode-dkc-rules \
              --only vantacode-ofa-techniques \
              --severity medium \
              --fail-on high \
              --format json \
              --out vantacode-scan.json

      - name: Upload report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: vantacode-scan-report
          path: vantacode-scan.json
```

For STIX output (e.g. to push into MISP), add a second `vantacode-scan`
invocation with `--format stix --out vantacode-scan.stix.json`.

---

## How the wrapper resolves the scanner

`scripts/run-scan.sh` looks for the scanner package in this order:

1. `$VANTACODE_SCANNER_DIR` if set.
2. `./vantacode-taxonomies/examples/scanner/` (sibling checkout or
   submodule of the project being scanned).
3. `~/.cache/vantacode/vantacode-taxonomies/` (auto-cloned shallowly on
   first run).

This means the skill works whether the user has the taxonomies repo
vendored, sitting next to their project, or nowhere on disk yet.

It then prefers `uv run --project <scanner>` and falls back to
`PYTHONPATH=<scanner> python3 -m vantacode_scanner` if `uv` is not on
`PATH`.

---

## What Claude does with the skill

When the skill activates, Claude reads
[`vantacode-scan/SKILL.md`](vantacode-scan/SKILL.md) for guidance on:

- when to invoke the scanner (and when not to),
- which CLI flags to use for which task (CI gate vs spreadsheet review vs
  STIX bundle for MISP),
- how to summarize findings — group by taxonomy, lead with criticals,
  surface OFA categories, treat governance gaps as easy wins,
- how to handle false positives — `regex` and `heuristic` rules are not
  ground truth.

If you want to customize the prompt-side behavior, edit `SKILL.md`. The
frontmatter `description` field is what Claude matches against to decide
whether to invoke the skill, so keep the trigger keywords there.

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Hook prints `run-scan.sh not found ... skipping` and exits 0 | Either install the skill (so `~/.claude/skills/vantacode-scan/` exists) or set `VANTACODE_SKILL_DIR` to wherever you copied it. |
| `vantacode-scan: scanner not found at ...` | Set `VANTACODE_SCANNER_DIR=/path/to/vantacode-taxonomies`, or let the wrapper auto-clone (`rm -rf ~/.cache/vantacode && commit again`). |
| `vantacode-scan: neither uv nor python3 is on PATH` | Install one of them. `uv` is preferred. |
| Hook is too noisy / blocks too aggressively | Lower the gate: `VANTACODE_FAIL_ON=critical git commit ...`. Or raise the report floor: `VANTACODE_SEVERITY=high`. |
| You want findings inline but `jq` isn't installed | `brew install jq` (macOS) or `apt-get install jq` (Debian/Ubuntu). The hook auto-detects it. |

---

## Related

- [`examples/scanner/`](../scanner/) — the scanner package itself, plus
  CLI reference and output formats.
- [`scanner-rules/`](../../scanner-rules/) — the rule packs the scanner
  loads (DKC, OFA, MBT, governance, sensitivity, domain, status).
- Top-level [`README.md`](../../README.md) — taxonomy overview.
