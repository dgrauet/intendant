"""`intendant report [PATH]` — aggregate audit across governed repos."""

from __future__ import annotations

import json as _json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from intendant.audit.discovery import find_intendant_repos
from intendant.audit.registry import collect_rules, filter_for_repo
from intendant.audit.runner import resolve_repo, run_audit
from intendant.core.config import load_config
from intendant.core.report import Report

console = Console()


@dataclass(frozen=True)
class PortfolioReport:
    """Result of a multi-repo portfolio report scan."""

    root: Path
    reports: list[tuple[Path, Report | Exception]]
    timestamp: datetime


def _scan_one(repo_path: Path) -> tuple[Path, Report | Exception]:
    """Audit a single repo, capturing any exception as the result.

    Multi-subproject mode: passes ALL rules to ``run_audit`` so it can dispatch
    transverse rules at root and stack-specific rules per subproject.
    Legacy single-Repo mode: filters at the call site as before.
    """
    try:
        config = load_config(repo_path)
        repo = resolve_repo(repo_path, config)
        all_rules = collect_rules()
        rules = all_rules if config.subprojects else filter_for_repo(all_rules, repo, config)
        report = run_audit(repo, config, rules)
        return (repo_path, report)
    except Exception as exc:
        return (repo_path, exc)


def _scan_all(root: Path, maxdepth: int = 2) -> PortfolioReport:
    """Discover all governed repos under ``root`` and audit each in turn."""
    repo_paths = find_intendant_repos(root, maxdepth)
    results = [_scan_one(p) for p in repo_paths]
    return PortfolioReport(root=root, reports=results, timestamp=datetime.now())


def report(
    path: Annotated[
        Path | None,
        typer.Argument(
            help="Root path to scan for .intendant.toml repos. Defaults to current directory."
        ),
    ] = None,
    format: Annotated[
        str,
        typer.Option("--format", "-f", help="Output format: human (default) or json."),
    ] = "human",
    maxdepth: Annotated[
        int,
        typer.Option("--maxdepth", help="Max directory depth to search for .intendant.toml."),
    ] = 2,
    save_snapshot: Annotated[
        bool,
        typer.Option("--save-snapshot", help="Save the scan JSON to the snapshot directory."),
    ] = False,
    diff: Annotated[
        bool,
        typer.Option(
            "--diff", help="Compare current scan vs the latest snapshot and emit the diff."
        ),
    ] = False,
    against: Annotated[
        Path | None,
        typer.Option(
            "--against",
            help="Use the specified snapshot file for the diff (overrides 'latest').",
        ),
    ] = None,
    snapshot_dir: Annotated[
        Path | None,
        typer.Option(
            "--snapshot-dir",
            help="Override the snapshot directory (default: <root>/.intendant/snapshots/).",
        ),
    ] = None,
    output: Annotated[
        Path | None,
        typer.Option(
            "--output",
            help="Output file path. Required when --format=html. Ignored otherwise.",
        ),
    ] = None,
    from_snapshot: Annotated[
        Path | None,
        typer.Option(
            "--from-snapshot",
            help="Render an existing snapshot JSON instead of running a fresh scan. "
            "Incompatible with --diff.",
        ),
    ] = None,
) -> None:
    """Aggregate audit across all intendant-governed repos under PATH."""
    from intendant.audit.diff import compute_diff
    from intendant.audit.output.report_diff_human import render_diff
    from intendant.audit.output.report_diff_json import render_diff_json
    from intendant.audit.output.report_json import render_report_json
    from intendant.audit.snapshot import (
        default_snapshot_dir,
        find_latest_snapshot,
        load_snapshot,
    )
    from intendant.audit.snapshot import (
        save_snapshot as _save_snapshot,
    )

    # ----- Validate new flags up-front, before any scanning -----
    if format == "html" and output is None:
        typer.echo("--output PATH is required when --format=html", err=True)
        raise typer.Exit(code=2)
    if output is not None and format != "html":
        typer.echo(f"--output is ignored for --format={format}", err=True)
    if output is not None and output.exists() and output.is_dir():
        typer.echo("--output must be a file path, not a directory", err=True)
        raise typer.Exit(code=2)
    if from_snapshot is not None and not from_snapshot.exists():
        typer.echo(f"--from-snapshot path does not exist: {from_snapshot}", err=True)
        raise typer.Exit(code=2)
    if from_snapshot is not None and diff:
        typer.echo("--from-snapshot and --diff are incompatible", err=True)
        raise typer.Exit(code=2)
    resolved = path if path is not None else Path.cwd()
    if not resolved.exists():
        typer.echo(f"path does not exist: {resolved}", err=True)
        raise typer.Exit(code=2)

    # ----- --from-snapshot path: load instead of scan -----
    if from_snapshot is not None:
        from intendant.audit.snapshot import load_snapshot_as_portfolio_report

        scan = load_snapshot_as_portfolio_report(from_snapshot)
    else:
        scan = _scan_all(resolved, maxdepth=maxdepth)
        if not scan.reports:
            typer.echo(f"no intendant-governed repos found under {resolved}", err=True)
            raise typer.Exit(code=2)

    effective_snapshot_dir = (
        snapshot_dir if snapshot_dir is not None else default_snapshot_dir(resolved)
    )

    if diff:
        # Determine previous snapshot
        if against is not None:
            previous_snapshot_path: Path | None = against
        else:
            previous_snapshot_path = find_latest_snapshot(effective_snapshot_dir, resolved)

        if previous_snapshot_path is None:
            if save_snapshot:
                # First-run: no previous snapshot — save and warn, exit 0
                typer.echo(
                    "No previous snapshot found — saving first snapshot and exiting.",
                    err=True,
                )
                saved = _save_snapshot(scan, effective_snapshot_dir)
                typer.echo(f"Snapshot saved: {saved}", err=True)
                raise typer.Exit(code=0)
            else:
                typer.echo(
                    "No previous snapshot found. Run with --save-snapshot first.",
                    err=True,
                )
                raise typer.Exit(code=2)

        previous_dict = load_snapshot(previous_snapshot_path)
        current_dict = _json.loads(render_report_json(scan))
        portfolio_diff = compute_diff(current_dict, previous_dict, str(previous_snapshot_path))

        if format == "json":
            typer.echo(render_diff_json(portfolio_diff))
        elif format == "html":
            from intendant.audit.output.report_diff_html import render_diff_html
            from intendant.core.handbook import Handbook
            from intendant.core.paths import docs_root

            try:
                handbook: Handbook | None = Handbook(root=docs_root())
            except FileNotFoundError:
                handbook = None
            assert output is not None  # validated up-front
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(render_diff_html(portfolio_diff, handbook))
        else:
            render_diff(portfolio_diff, console=console)

        if save_snapshot:
            saved = _save_snapshot(scan, effective_snapshot_dir)
            typer.echo(f"Snapshot saved: {saved}", err=True)

        exit_code = 1 if portfolio_diff.has_new_required_failure else 0
        raise typer.Exit(code=exit_code)

    # No diff — emit normal report output
    if format == "json":
        typer.echo(render_report_json(scan))
    elif format == "html":
        from intendant.audit.output.report_html import render_html

        assert output is not None  # validated up-front
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(render_html(scan))
    else:
        from intendant.audit.output.report_human import render_report

        render_report(scan, console=console)

    if save_snapshot:
        saved = _save_snapshot(scan, effective_snapshot_dir)
        typer.echo(f"Snapshot saved: {saved}", err=True)

    raise typer.Exit(code=_exit_code(scan))


def _exit_code(scan: PortfolioReport) -> int:
    """Return 1 if any repo has at least one required-severity fail, else 0."""
    for _, result in scan.reports:
        if isinstance(result, Report):
            for finding in result.findings:
                if finding.status == "fail" and finding.severity == "required":
                    return 1
    return 0
