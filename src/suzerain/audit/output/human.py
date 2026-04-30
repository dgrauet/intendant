"""Render a Report to a Rich-formatted human-readable terminal output."""

from __future__ import annotations

from rich.console import Console
from rich.markup import escape
from rich.table import Table

from suzerain.core.report import Report

_STATUS_STYLE = {
    "pass": "green",
    "fail": "red",
    "exempt": "yellow",
    "skip": "dim",
}


def render_human(report: Report, console: Console | None = None) -> None:
    """Print the report to the given (or default) Console."""
    console = console or Console()
    console.print(
        f"[bold]{escape(str(report.repo_path))}[/bold]"
        f"  stack=[cyan]{report.stack}[/cyan]"
        f"  score=[bold]{report.score}/100[/bold]"
    )
    if not report.findings:
        console.print("[dim]No rules ran (empty registry).[/dim]")
        return
    table = Table(show_header=True, header_style="bold")
    table.add_column("Rule")
    table.add_column("Sev")
    table.add_column("Status")
    table.add_column("Evidence", overflow="fold")
    table.add_column("Fix", style="dim")
    for f in report.findings:
        table.add_row(
            f.rule_id,
            f.severity,
            f"[{_STATUS_STYLE[f.status]}]{f.status}[/{_STATUS_STYLE[f.status]}]",
            escape(f.evidence),
            "auto-fix available" if f.fix_available else "",
        )
    console.print(table)
    console.print(
        f"[bold]Summary[/bold]: "
        f"{report.passing} passing · "
        f"{report.failing} failing · "
        f"{report.exempt} exempt · "
        f"{report.skipped} skipped · "
        f"{report.fixable} fixable"
    )
