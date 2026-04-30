"""`suzerain explain RULE_ID` — show a rule's handbook section + ADR."""

from __future__ import annotations

import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from suzerain.core.handbook import Handbook
from suzerain.core.paths import docs_root

console = Console()


def explain(rule_id: str) -> None:
    """Show the handbook section and linked ADR for ``RULE_ID``."""
    handbook = Handbook(root=docs_root())
    rule = handbook.get_rule(rule_id)
    if rule is None:
        console.print(f"[red]Rule '{rule_id}' not found.[/red]")
        available = handbook.list_rules()
        if available:
            console.print(f"Available rules: {', '.join(available)}")
        raise typer.Exit(code=1)

    stacks_text = ", ".join(rule.stacks) if rule.stacks else "*"
    console.print(
        Panel.fit(
            f"[bold]{rule.rule_id} — {rule.title}[/bold]\n"
            f"severity: {rule.severity} · stacks: {stacks_text}",
            title="Rule",
            border_style="cyan",
        )
    )
    console.print(Markdown(rule.body))

    if rule.adr_ref:
        adr_text = handbook.get_adr(rule.adr_ref)
        if adr_text:
            console.print()
            console.print(
                Panel.fit(
                    f"[bold]Linked ADR: {rule.adr_ref}[/bold]",
                    border_style="magenta",
                )
            )
            console.print(Markdown(adr_text))
        else:
            console.print(f"[yellow]ADR '{rule.adr_ref}' referenced but not found.[/yellow]")
