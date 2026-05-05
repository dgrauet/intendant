"""`intendant doctor` — verify the local install is healthy."""

from __future__ import annotations

from rich.console import Console

from intendant import __version__
from intendant.audit.registry import collect_rules
from intendant.core.handbook import Handbook
from intendant.core.paths import docs_root

console = Console()


def doctor() -> None:
    """Check that intendant itself is healthy: handbook loads, rules registered."""
    console.print(f"[bold]intendant {__version__}[/bold]")
    rules = collect_rules()
    console.print(f"[green]Rules loaded:[/green] {len(rules)}")
    for r in rules:
        stacks = ",".join(r.stacks) if r.stacks else "*"
        console.print(f"  • {r.id} ({r.severity}, stacks={stacks})")
    try:
        hb = Handbook(root=docs_root())
        handbook_rules = hb.list_rules()
        console.print(f"[green]Handbook entries:[/green] {len(handbook_rules)}")
    except FileNotFoundError as exc:
        console.print(f"[red]Handbook unreadable:[/red] {exc}")
