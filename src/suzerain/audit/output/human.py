"""Render a Report to a Rich-formatted human-readable terminal output."""

from __future__ import annotations

from rich.console import Console
from rich.markup import escape
from rich.table import Table

from suzerain.core.report import Finding, Report

_STATUS_STYLE = {
    "pass": "green",
    "fail": "red",
    "exempt": "yellow",
    "skip": "dim",
}


def render_human(report: Report, console: Console | None = None) -> None:
    """Print the report to the given (or default) Console."""
    console = console or Console()
    stack_label = f"{report.mode} ({'/'.join(report.stacks)})" if report.stacks else report.mode
    console.print(
        f"[bold]{escape(str(report.repo_path))}[/bold]"
        f"  stack=[cyan]{stack_label}[/cyan]"
        f"  score=[bold]{report.score}/100[/bold]"
    )
    if not report.findings:
        console.print("[dim]No rules ran (empty registry).[/dim]")
        return

    has_subprojects = any(f.subproject is not None for f in report.findings)
    if not has_subprojects:
        _render_flat_table(report.findings, console)
    else:
        _render_sections(report.findings, console)

    console.print(
        f"[bold]Summary[/bold]: "
        f"{report.passing} passing · "
        f"{report.failing} failing · "
        f"{report.exempt} exempt · "
        f"{report.skipped} skipped · "
        f"{report.fixable} fixable"
    )


def _render_flat_table(findings: list[Finding], console: Console) -> None:
    table = Table(show_header=True, header_style="bold")
    table.add_column("Rule")
    table.add_column("Sev")
    table.add_column("Status")
    table.add_column("Evidence", overflow="fold")
    table.add_column("Fix", style="dim")
    for f in findings:
        table.add_row(
            f.rule_id,
            f.severity,
            f"[{_STATUS_STYLE[f.status]}]{f.status}[/{_STATUS_STYLE[f.status]}]",
            escape(f.evidence),
            "auto-fix available" if f.fix_available else "",
        )
    console.print(table)


def _render_sections(findings: list[Finding], console: Console) -> None:
    """Group findings by subproject and render one table per group.

    Order: ROOT (transverse, subproject=None) first, then subprojects in
    insertion order.
    """
    groups: dict[str | None, list[Finding]] = {}
    for f in findings:
        groups.setdefault(f.subproject, []).append(f)
    if None in groups:
        console.print("")
        console.print("[bold]ROOT (transverse rules)[/bold]")
        _render_flat_table(groups[None], console)
    for name, sub_findings in groups.items():
        if name is None:
            continue
        console.print("")
        console.print(f"[bold]{escape(name)}[/bold]")
        _render_flat_table(sub_findings, console)
