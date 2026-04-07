"""Click-based CLI for the VantaCode reference scanner."""

from __future__ import annotations

import sys
from pathlib import Path

import click

from .output import write_csv, write_json, write_stix
from .rules import load_all_rule_packs
from .scanner import scan
from .sources import display_source, resolve_source


_DEFAULT_RULES_DIR = Path(__file__).resolve().parent.parent.parent.parent / "scanner-rules"


_FORMAT_WRITERS = {
    "json": write_json,
    "csv":  write_csv,
    "stix": write_stix,
}


@click.command(name="vantacode-scan")
@click.option(
    "--source", "-s", required=True,
    help="Local directory, GitHub URL (https://github.com/owner/repo[.git]), or owner/repo shorthand.",
)
@click.option(
    "--rules", "-r", "rules_dir",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=_DEFAULT_RULES_DIR,
    show_default=True,
    help="Directory containing scanner-rules YAML files.",
)
@click.option(
    "--format", "-f", "fmt",
    type=click.Choice(sorted(_FORMAT_WRITERS.keys())),
    default="json",
    show_default=True,
    help="Output format.",
)
@click.option(
    "--out", "-o", "out_path",
    type=click.Path(path_type=Path),
    default=None,
    help="Write output to this file instead of stdout (required for csv/stix).",
)
@click.option(
    "--severity",
    type=click.Choice(["info", "low", "medium", "high", "critical"]),
    default="info",
    show_default=True,
    help="Minimum severity to report.",
)
@click.option(
    "--only", "only_taxonomies", multiple=True,
    help="Restrict scan to one or more taxonomies (e.g. --only vantacode-dkc-rules --only vantacode-ofa-techniques).",
)
@click.option(
    "--fail-on",
    type=click.Choice(["never", "low", "medium", "high", "critical"]),
    default="never",
    show_default=True,
    help="Exit non-zero if any finding meets or exceeds this severity (useful for CI / pre-commit).",
)
@click.option("--quiet", "-q", is_flag=True, help="Suppress the human summary.")
def main(
    source: str,
    rules_dir: Path,
    fmt: str,
    out_path: Path | None,
    severity: str,
    only_taxonomies: tuple[str, ...],
    fail_on: str,
    quiet: bool,
) -> None:
    """Scan a directory or GitHub repo against VantaCode taxonomy rules."""
    if not rules_dir.exists():
        click.echo(f"error: rules directory not found: {rules_dir}", err=True)
        sys.exit(2)

    packs = load_all_rule_packs(rules_dir)
    if only_taxonomies:
        packs = [p for p in packs if p.taxonomy in only_taxonomies]
    if not packs:
        click.echo("error: no rule packs loaded", err=True)
        sys.exit(2)

    if not quiet:
        rule_count = sum(len(p.rules) for p in packs)
        click.echo(f"loaded {len(packs)} rule packs ({rule_count} rules) from {rules_dir}", err=True)
        click.echo(f"resolving source: {display_source(source)}", err=True)

    root, cleanup = resolve_source(source)
    try:
        report = scan(root, packs, only_severity=severity)
    finally:
        cleanup()

    if fmt == "json" and out_path is None:
        from .scanner import report_to_json
        click.echo(report_to_json(report))
    else:
        if out_path is None:
            out_path = Path(f"vantacode-scan.{fmt}")
        _FORMAT_WRITERS[fmt](report, out_path)
        if not quiet:
            click.echo(f"wrote {len(report.findings)} findings to {out_path}", err=True)

    if not quiet:
        click.echo("", err=True)
        click.echo(f"summary: {len(report.findings)} findings across {report.scanned_files} files", err=True)
        for sev, n in sorted(report.summary_by_severity().items(), key=lambda kv: kv[0]):
            click.echo(f"  {sev:9} {n}", err=True)
        if report.skipped_rules:
            click.echo(f"  skipped: {len(report.skipped_rules)} rules", err=True)

    if fail_on != "never":
        rank = {"low": 1, "medium": 2, "high": 3, "critical": 4}[fail_on]
        worst = max(
            (
                {"info": 0, "low": 1, "medium": 2, "high": 3, "critical": 4, "variable": 2}.get(f.severity, 0)
                for f in report.findings
            ),
            default=0,
        )
        if worst >= rank:
            sys.exit(1)


if __name__ == "__main__":
    main()
