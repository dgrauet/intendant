"""`intendant audit [PATH...]` — run the audit; optionally apply fixes."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from intendant.audit.fix import apply_fixes
from intendant.audit.output.human import render_human
from intendant.audit.output.json_format import render_json
from intendant.audit.output.md import render_markdown
from intendant.audit.registry import collect_rules, filter_for_repo
from intendant.audit.runner import resolve_repo, run_audit
from intendant.core.config import load_config
from intendant.core.report import Report

console = Console()

_SEVERITY_ORDER = {"required": 0, "recommended": 1, "optional": 2}


def audit(
    paths: Annotated[
        list[Path] | None,
        typer.Argument(help="Repo path(s) to audit. Defaults to current directory."),
    ] = None,
    output_format: Annotated[
        str,
        typer.Option("--format", help="Output format: human (default), json, md."),
    ] = "human",
    severity: Annotated[
        str | None,
        typer.Option("--severity", help="Threshold severity for non-zero exit."),
    ] = None,
    fix: Annotated[
        bool,
        typer.Option(
            "--fix", help="Apply safe fixes; deposit non-safe ones in .intendant/proposed/."
        ),
    ] = False,
    dry_run: Annotated[
        bool,
        typer.Option("--dry-run", help="With --fix, show what would be done without writing."),
    ] = False,
) -> None:
    """Run the intendant audit on one or more repos."""
    target_paths = paths if paths else [Path(".")]
    rules = collect_rules()
    has_failure = False

    for raw_path in target_paths:
        path = raw_path.resolve()
        if not path.is_dir():
            console.print(f"[red]Skipping {path}: not a directory.[/red]")
            has_failure = True
            continue
        config = load_config(path)
        repo = resolve_repo(path, config)
        # Multi-subproject mode: pass all rules so the runner can dispatch
        # transverse rules at the root and stack-specific rules per subproject.
        applicable = rules if config.subprojects else filter_for_repo(rules, repo, config)
        report = run_audit(repo, config, applicable, compute_fix_preview=fix)
        _emit(report, output_format)

        if fix:
            applied, proposed = apply_fixes(report, repo, config, dry_run=dry_run)
            if applied:
                action = "Would apply" if dry_run else "Applied"
                console.print(f"[green]{action} fixes for: {applied}[/green]")
            if proposed:
                action = "Would propose" if dry_run else "Proposed (in .intendant/proposed/)"
                console.print(f"[yellow]{action} fixes for: {proposed}[/yellow]")

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


def _report_has_blocking_failure(report: Report, severity_threshold: str | None) -> bool:
    threshold = severity_threshold or "required"
    threshold_idx = _SEVERITY_ORDER.get(threshold, 0)
    return any(
        f.status == "fail" and _SEVERITY_ORDER[f.severity] <= threshold_idx for f in report.findings
    )
