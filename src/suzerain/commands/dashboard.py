"""`suzerain dashboard [PATH]` — aggregate audit across governed repos."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from suzerain.audit.discovery import find_suzerain_repos
from suzerain.audit.registry import collect_rules, filter_for_repo
from suzerain.audit.runner import run_audit
from suzerain.core.config import load_config
from suzerain.core.repo import Repo
from suzerain.core.report import Report

console = Console()


@dataclass(frozen=True)
class DashboardScan:
    """Result of a multi-repo dashboard scan."""

    root: Path
    reports: list[tuple[Path, Report | Exception]]
    timestamp: datetime


def _scan_one(repo_path: Path) -> tuple[Path, Report | Exception]:
    """Audit a single repo, capturing any exception as the result."""
    try:
        repo = Repo.from_path(repo_path)
        config = load_config(repo_path)
        rules = filter_for_repo(collect_rules(), repo, config)
        report = run_audit(repo, config, rules)
        return (repo_path, report)
    except Exception as exc:
        return (repo_path, exc)


def _scan_all(root: Path, maxdepth: int = 2) -> DashboardScan:
    """Discover all governed repos under ``root`` and audit each in turn."""
    repo_paths = find_suzerain_repos(root, maxdepth)
    results = [_scan_one(p) for p in repo_paths]
    return DashboardScan(root=root, reports=results, timestamp=datetime.now())


def dashboard(
    path: Annotated[
        Path | None,
        typer.Argument(
            help="Root path to scan for .suzerain.toml repos. Defaults to current directory."
        ),
    ] = None,
    format: Annotated[
        str,
        typer.Option("--format", "-f", help="Output format: human (default) or json."),
    ] = "human",
    maxdepth: Annotated[
        int,
        typer.Option("--maxdepth", help="Max directory depth to search for .suzerain.toml."),
    ] = 2,
) -> None:
    """Aggregate audit across all suzerain-governed repos under PATH."""
    resolved = path if path is not None else Path.cwd()
    if not resolved.exists():
        typer.echo(f"path does not exist: {resolved}", err=True)
        raise typer.Exit(code=2)
    scan = _scan_all(resolved, maxdepth=maxdepth)
    if not scan.reports:
        typer.echo(f"no suzerain-governed repos found under {resolved}", err=True)
        raise typer.Exit(code=2)
    if format == "json":
        from suzerain.audit.output.dashboard_json import render_dashboard_json

        typer.echo(render_dashboard_json(scan))
    else:
        from suzerain.audit.output.dashboard_human import render_dashboard

        render_dashboard(scan, console=console)
    raise typer.Exit(code=_exit_code(scan))


def _exit_code(scan: DashboardScan) -> int:
    """Return 1 if any repo has at least one required-severity fail, else 0."""
    for _, result in scan.reports:
        if isinstance(result, Report):
            for finding in result.findings:
                if finding.status == "fail" and finding.severity == "required":
                    return 1
    return 0
