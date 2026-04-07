#!/usr/bin/env bash
# vantacode-scan: thin wrapper that runs the VantaCode reference scanner
# against the current directory (or whatever --source you pass).
#
# This script is what the Claude Code skill invokes. It is also what the
# pre-commit hook invokes. Keeping a single entry point keeps behavior
# consistent across "claude is running this for me" and "git is running
# this for me" modes.

set -euo pipefail

# ── Resolve the scanner location ────────────────────────────────────────────
#
# Order of resolution:
#   1. $VANTACODE_SCANNER_DIR if set (full path to a checkout that contains
#      examples/scanner/)
#   2. ./vantacode-taxonomies (submodule or sibling checkout)
#   3. ~/.cache/vantacode/vantacode-taxonomies (auto-cloned by this script)
#
SCANNER_REPO="${VANTACODE_SCANNER_DIR:-}"

if [[ -z "$SCANNER_REPO" && -d "vantacode-taxonomies/examples/scanner" ]]; then
    SCANNER_REPO="$(pwd)/vantacode-taxonomies"
fi

if [[ -z "$SCANNER_REPO" ]]; then
    SCANNER_REPO="${HOME}/.cache/vantacode/vantacode-taxonomies"
    if [[ ! -d "$SCANNER_REPO" ]]; then
        echo "vantacode-scan: cloning scanner into $SCANNER_REPO ..." >&2
        mkdir -p "$(dirname "$SCANNER_REPO")"
        git clone --depth 1 --quiet \
            https://github.com/vantacode/vantacode-taxonomies.git \
            "$SCANNER_REPO"
    fi
fi

if [[ ! -d "$SCANNER_REPO/examples/scanner" ]]; then
    echo "vantacode-scan: scanner not found at $SCANNER_REPO/examples/scanner" >&2
    exit 2
fi

# ── Run via uv (preferred) or fall back to PYTHONPATH ──────────────────────

if command -v uv >/dev/null 2>&1; then
    exec uv run --project "$SCANNER_REPO/examples/scanner" \
                vantacode-scan "$@"
fi

if command -v python3 >/dev/null 2>&1; then
    echo "vantacode-scan: uv not found, falling back to PYTHONPATH mode" >&2
    PYTHONPATH="$SCANNER_REPO/examples/scanner" \
        exec python3 -m vantacode_scanner "$@"
fi

echo "vantacode-scan: neither uv nor python3 is on PATH; install one and retry" >&2
exit 2
