"""click-based CLI for the GitHub-wide VantaCode scanner.

Usage examples
--------------

    # Scan all of GitHub for the 63 high-signal queries (uses gh code search)
    vantacode-gh-scan --rules ../../scanner-rules

    # Restrict to a single org and a single rule pack, write JSON
    vantacode-gh-scan -r ../../scanner-rules --scope org:vantacode \\
        --only vantacode-ofa-techniques -f json -o ofa-org.json

    # Limit blast radius while debugging
    vantacode-gh-scan -r ../../scanner-rules --max-queries 5 --pages 1

    # CI gate: any critical hit is a build failure
    vantacode-gh-scan -r ../../scanner-rules --fail-on critical

    # STIX bundle to push into MISP
    vantacode-gh-scan -r ../../scanner-rules -f stix -o gh-scan.stix.json
"""

from __future__ import annotations

import sys
from pathlib import Path

import click

from .gh import gh_authenticated, gh_available
from .output import write_csv, write_json, write_stix
from .scanner import GithubScanReport, run_scan, severity_rank


_DEFAULT_RULES_DIR = Path(__file__).resolve().parents[3] / "scanner-rules"

_FORMATS = ("json", "csv", "stix")
_SEVERITIES = ("info", "low", "medium", "high", "critical")
_FAIL_ON = ("never", "low", "medium", "high", "critical")


@click.command(
    name="vantacode-gh-scan",
    help="Run a VantaCode taxonomy-driven scan against GitHub Code Search.",
)
@click.option(
    "-r", "--rules",
    type=click.Path(file_okay=False, exists=True, path_type=Path),
    default=_DEFAULT_RULES_DIR,
    show_default=True,
    help="Directory containing scanner-rules YAML files.",
)
@click.option(
    "--scope",
    type=str,
    default=None,
    help="GitHub scope qualifier appended to every query "
         "(e.g. 'org:vantacode', 'user:NoDataFound', 'repo:owner/name'). "
         "Omit to scan all of GitHub.",
)
@click.option(
    "--only",
    "only_taxonomies",
    multiple=True,
    help="Restrict to one or more taxonomies (repeatable). "
         "Example: --only vantacode-dkc-rules --only vantacode-ofa-techniques",
)
@click.option(
    "--severity",
    type=click.Choice(_SEVERITIES),
    default="medium",
    show_default=True,
    help="Minimum severity to query. Rules below this floor are skipped.",
)
@click.option(
    "--fail-on",
    "fail_on",
    type=click.Choice(_FAIL_ON),
    default="never",
    show_default=True,
    help="Exit non-zero if any finding meets or exceeds this severity.",
)
@click.option(
    "-f", "--format",
    "fmt",
    type=click.Choice(_FORMATS),
    default="json",
    show_default=True,
    help="Output format.",
)
@click.option(
    "-o", "--out",
    type=click.Path(dir_okay=False, path_type=Path),
    default=None,
    help="Output file. Required for csv/stix; defaults to stdout for json.",
)
@click.option(
    "--pages",
    type=click.IntRange(1, 10),
    default=1,
    show_default=True,
    help="Pages of results per query (page * per-page caps at 1000 — gh API limit).",
)
@click.option(
    "--per-page",
    type=click.IntRange(1, 100),
    default=100,
    show_default=True,
    help="Results per page (max 100, the gh API hard cap).",
)
@click.option(
    "--pause",
    "pause_seconds",
    type=float,
    default=2.5,
    show_default=True,
    help="Seconds to sleep between gh calls. Stay under the 30/min auth limit.",
)
@click.option(
    "--max-queries",
    type=int,
    default=None,
    help="Hard cap on the number of gh searches issued (useful for testing).",
)
@click.option(
    "-q", "--quiet",
    is_flag=True,
    help="Suppress per-query progress output.",
)
def main(
    rules: Path,
    scope: str | None,
    only_taxonomies: tuple[str, ...],
    severity: str,
    fail_on: str,
    fmt: str,
    out: Path | None,
    pages: int,
    per_page: int,
    pause_seconds: float,
    max_queries: int | None,
    quiet: bool,
) -> None:
    if not gh_available():
        click.echo(
            "vantacode-gh-scan: gh CLI not found on PATH.\n"
            "Install: https://cli.github.com",
            err=True,
        )
        raise SystemExit(2)

    authed, status = gh_authenticated()
    if not authed:
        click.echo(
            "vantacode-gh-scan: gh CLI is installed but not authenticated.\n"
            "Run `gh auth login` first — unauthenticated code search is "
            "rate-limited to 10 requests/minute.\n\n"
            f"gh auth status: {status}",
            err=True,
        )
        raise SystemExit(2)

    # severity floor → set of allowed severities
    floor = severity_rank(severity)
    severities_allowed = {s for s in _SEVERITIES if severity_rank(s) >= floor}
    # Always include "variable" — those are CVE-driven and shouldn't be silently dropped
    severities_allowed.add("variable")

    only_set = set(only_taxonomies) if only_taxonomies else None

    def _log(msg: str) -> None:
        if not quiet:
            click.echo(msg, err=True)

    if not quiet:
        click.echo(
            f"vantacode-gh-scan: scope={scope or 'all of GitHub'}  "
            f"severity≥{severity}  pages={pages}  per_page={per_page}  pause={pause_seconds}s",
            err=True,
        )

    try:
        report = run_scan(
            rules,
            scope=scope,
            only_taxonomies=only_set,
            only_severities=severities_allowed,
            pages=pages,
            per_page=per_page,
            pause_seconds=pause_seconds,
            max_queries=max_queries,
            log=_log,
        )
    except RuntimeError as e:
        click.echo(f"vantacode-gh-scan: {e}", err=True)
        raise SystemExit(2)

    # ── output ────────────────────────────────────────────────────────────
    if fmt == "json":
        if out:
            write_json(report, out)
            if not quiet:
                click.echo(f"vantacode-gh-scan: wrote {out}", err=True)
        else:
            import json
            click.echo(json.dumps(report.to_dict(), indent=2))
    elif fmt == "csv":
        if not out:
            click.echo("vantacode-gh-scan: --out is required for csv", err=True)
            raise SystemExit(2)
        write_csv(report, out)
        if not quiet:
            click.echo(f"vantacode-gh-scan: wrote {out}", err=True)
    elif fmt == "stix":
        if not out:
            click.echo("vantacode-gh-scan: --out is required for stix", err=True)
            raise SystemExit(2)
        write_stix(report, out)
        if not quiet:
            click.echo(f"vantacode-gh-scan: wrote {out}", err=True)

    # ── human summary ─────────────────────────────────────────────────────
    if not quiet:
        click.echo("", err=True)
        click.echo(
            f"vantacode-gh-scan: {report.queries_run} queries, "
            f"{report.queries_failed} failed, "
            f"{report.repos_seen} unique repos, "
            f"{len(report.findings)} findings.",
            err=True,
        )
        sev_summary = report.summary_by_severity()
        if sev_summary:
            click.echo(
                "  by severity: "
                + ", ".join(f"{k}={v}" for k, v in sorted(
                    sev_summary.items(),
                    key=lambda kv: severity_rank(kv[0]),
                    reverse=True,
                )),
                err=True,
            )
        tax_summary = report.summary_by_taxonomy()
        if tax_summary:
            click.echo(
                "  by taxonomy: "
                + ", ".join(f"{k}={v}" for k, v in sorted(tax_summary.items())),
                err=True,
            )

    # ── fail-on gate ──────────────────────────────────────────────────────
    if fail_on != "never":
        gate = severity_rank(fail_on)
        triggered = [f for f in report.findings if severity_rank(f.severity) >= gate]
        if triggered:
            if not quiet:
                click.echo(
                    f"vantacode-gh-scan: {len(triggered)} finding(s) at or above "
                    f"--fail-on={fail_on}",
                    err=True,
                )
            raise SystemExit(1)


if __name__ == "__main__":
    main()
