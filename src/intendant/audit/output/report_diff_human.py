"""Render a PortfolioDiff to terminal."""

from __future__ import annotations

from rich.console import Console
from rich.markup import escape

from intendant.audit.diff import PortfolioDiff


def render_diff(diff: PortfolioDiff, console: Console | None = None) -> None:
    """Print the portfolio diff to the given (or default) Console."""
    console = console or Console()
    cur_ts = diff.current.get("timestamp", "")
    prev_ts = diff.previous.get("timestamp", "")
    root = diff.current.get("root", "")
    cur_short = (
        cur_ts.split("T", 1)[0] + " " + cur_ts.split("T", 1)[1][:5] if "T" in cur_ts else cur_ts
    )
    prev_short = (
        prev_ts.split("T", 1)[0] + " " + prev_ts.split("T", 1)[1][:5] if "T" in prev_ts else prev_ts
    )
    console.print(f"[bold]PORTFOLIO DIFF[/bold]  {cur_short} vs {prev_short}")
    console.print(f"Root: [cyan]{escape(str(root))}[/cyan]")
    console.print("")

    score_changes = diff.score_changes
    if score_changes:
        console.print("[bold]Score changes:[/bold]")
        for sc in score_changes:
            arrow, color = _score_indicator(sc["delta"])
            sign = "+" if sc["delta"] > 0 else ""
            note = "(no change)" if sc["delta"] == 0 else f"({sign}{sc['delta']})"
            console.print(
                f"  [{color}]{arrow}[/{color}] {sc['path']:<30} "
                f"{sc['before']:>3}/100 → {sc['after']:>3}/100 {note}"
            )
        console.print("")

    new_fails = diff.new_failures
    if new_fails:
        console.print("[bold red]New failures:[/bold red]")
        by_repo: dict[str, list[str]] = {}
        for f in new_fails:
            by_repo.setdefault(f["path"], []).append(f"{f['rule_id']} ({f['severity']})")
        for path in sorted(by_repo):
            console.print(f"  {path}: {', '.join(by_repo[path])}")
        console.print("")

    resolved = diff.resolved_failures
    if resolved:
        console.print("[bold green]Resolved failures:[/bold green]")
        by_repo2: dict[str, list[str]] = {}
        for f in resolved:
            by_repo2.setdefault(f["path"], []).append(f"{f['rule_id']} ({f['severity']})")
        for path in sorted(by_repo2):
            console.print(f"  {path}: {', '.join(by_repo2[path])}")
        console.print("")

    if diff.new_repos:
        console.print("[bold]New repos:[/bold]")
        for p in diff.new_repos:
            console.print(f"  [green]+ {p}[/green]")
        console.print("")

    if diff.removed_repos:
        console.print("[bold]Removed repos:[/bold]")
        for p in diff.removed_repos:
            console.print(f"  [red]- {p}[/red]")
        console.print("")


def _score_indicator(delta: int) -> tuple[str, str]:
    """Return (arrow, color) for a score delta."""
    if delta > 0:
        return ("↑", "green")
    if delta < 0:
        return ("↓", "red")
    return (" ", "dim")
