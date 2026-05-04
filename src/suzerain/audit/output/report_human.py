"""Render a PortfolioReport to a Rich-formatted terminal output."""

from __future__ import annotations

from rich.console import Console
from rich.markup import escape
from rich.table import Table

from suzerain.audit.registry import collect_rules
from suzerain.commands.report import PortfolioReport
from suzerain.core.report import Report
from suzerain.core.rule import Rule


def render_report(scan: PortfolioReport, console: Console | None = None) -> None:
    """Print the portfolio report scan to the given (or default) Console."""
    console = console or Console()
    _render_header(scan, console)
    _render_summary(scan, console)
    _render_legend(scan, console)


def _render_header(scan: PortfolioReport, console: Console) -> None:
    ts = scan.timestamp.strftime("%Y-%m-%d %H:%M")
    console.print(f"[bold]PORTFOLIO REPORT[/bold]  {ts}")
    console.print(
        f"Root: [cyan]{escape(str(scan.root))}[/cyan]  ·  "
        f"Repos audited: [bold]{len(scan.reports)}[/bold]"
    )
    console.print("")


def _render_summary(scan: PortfolioReport, console: Console) -> None:
    table = Table(show_header=True, header_style="bold", box=None, pad_edge=False)
    table.add_column("repo")
    table.add_column("stack")
    table.add_column("score", justify="right")
    table.add_column("status")
    for repo_path, result in scan.reports:
        try:
            rel = repo_path.relative_to(scan.root)
        except ValueError:
            rel = repo_path
        if isinstance(result, Exception):
            err_msg = f"[{type(result).__name__}] {str(result)[:80]}"
            table.add_row(str(rel), "?", "-/-", f"[red]⚠ error[/red]\n  {escape(err_msg)}")
            continue
        score = f"{result.score}/100"
        failing = [f for f in result.findings if f.status == "fail"]
        if not failing:
            status = "[green]✓ all clean[/green]"
        else:
            required_n = sum(1 for f in failing if f.severity == "required")
            recommended_n = sum(1 for f in failing if f.severity == "recommended")
            fixable_n = sum(1 for f in failing if f.fix_available)
            ids = ", ".join(_format_rule_id(f.rule_id, f.fix_available) for f in failing)
            status = (
                f"[red]{required_n} req[/red]"
                f" · [yellow]{recommended_n} rec[/yellow]"
                f" · [green]{fixable_n} fix[/green]"
                f"\n  {ids}"
            )
        table.add_row(str(rel), result.stack, score, status)
    console.print(table)


def _render_legend(scan: PortfolioReport, console: Console) -> None:
    failing_ids = _collect_failing_ids(scan)
    if not failing_ids:
        return
    rules_by_id = {r.id: r for r in collect_rules()}
    grouped: dict[str, list[Rule]] = {"required": [], "recommended": [], "optional": []}
    fixable_ids = _collect_fixable_ids(scan)
    for rid in sorted(failing_ids):
        rule = rules_by_id.get(rid)
        if rule is None:
            continue
        grouped[rule.severity].append(rule)
    console.print("")
    console.print("[bold]Failing rules in this scan[/bold] (* = auto-fixable):")
    console.print("")
    for severity in ("required", "recommended", "optional"):
        rules = grouped[severity]
        if not rules:
            continue
        console.print(f"  [bold]{severity}[/bold]")
        for rule in sorted(rules, key=lambda r: r.id):
            mark = "*" if rule.id in fixable_ids else " "
            console.print(f"    {rule.id}{mark} - {escape(rule.title)}")


def _collect_failing_ids(scan: PortfolioReport) -> set[str]:
    ids: set[str] = set()
    for _, result in scan.reports:
        if isinstance(result, Report):
            ids.update(f.rule_id for f in result.findings if f.status == "fail")
    return ids


def _collect_fixable_ids(scan: PortfolioReport) -> set[str]:
    ids: set[str] = set()
    for _, result in scan.reports:
        if isinstance(result, Report):
            ids.update(f.rule_id for f in result.findings if f.status == "fail" and f.fix_available)
    return ids


def _format_rule_id(rule_id: str, fixable: bool) -> str:
    return f"{rule_id}*" if fixable else rule_id
