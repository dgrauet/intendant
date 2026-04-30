"""`suzerain audit [PATH...]` — run the audit on one or more repos."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from suzerain.audit.output.human import render_human
from suzerain.audit.output.json_format import render_json
from suzerain.audit.output.md import render_markdown
from suzerain.audit.registry import collect_rules, filter_for_repo
from suzerain.audit.runner import run_audit
from suzerain.core.config import load_config
from suzerain.core.repo import Repo
from suzerain.core.report import Report

console = Console()


def audit(
    paths: Annotated[
        list[Path] | None,
        typer.Argument(
            help="Repo path(s) to audit. Defaults to current directory.",
        ),
    ] = None,
    output_format: Annotated[
        str,
        typer.Option(
            "--format",
            help="Output format: human (default), json, md.",
        ),
    ] = "human",
    severity: Annotated[
        str | None,
        typer.Option(
            "--severity",
            help="Only fail (exit 1) if a finding of this severity or higher is failing.",
        ),
    ] = None,
) -> None:
    """Run the suzerain audit on one or more repos."""
    target_paths = paths if paths else [Path(".")]
    rules = collect_rules()
    has_failure = False

    for raw_path in target_paths:
        path = raw_path.resolve()
        if not path.is_dir():
            console.print(f"[red]Skipping {path}: not a directory.[/red]")
            has_failure = True
            continue
        repo = Repo.from_path(path)
        config = load_config(path)
        applicable = filter_for_repo(rules, repo, config)
        report = run_audit(repo, config, applicable)
        _emit(report, output_format)
        if _report_has_blocking_failure(report, severity):
            has_failure = True

    if has_failure:
        raise typer.Exit(code=1)


def _emit(report: Report, fmt: str) -> None:
    if fmt == "json":
        typer.echo(render_json(report))
    elif fmt == "md":
        typer.echo(render_markdown(report))
    else:
        render_human(report, console=console)


_SEVERITY_ORDER = {"required": 0, "recommended": 1, "optional": 2}


def _report_has_blocking_failure(report: Report, severity_threshold: str | None) -> bool:
    threshold = severity_threshold or "required"
    threshold_idx = _SEVERITY_ORDER.get(threshold, 0)
    return any(
        f.status == "fail" and _SEVERITY_ORDER[f.severity] <= threshold_idx for f in report.findings
    )
