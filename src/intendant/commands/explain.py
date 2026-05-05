"""`intendant explain RULE_ID` — show a rule's handbook section + ADR."""

from __future__ import annotations

from typing import Annotated

import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

from intendant.audit.registry import collect_rules
from intendant.core.handbook import Handbook
from intendant.core.paths import docs_root

console = Console()

_SEVERITY_ORDER = {"required": 0, "recommended": 1, "optional": 2}


def explain(
    rule_id: Annotated[
        str | None,
        typer.Argument(help="Rule ID to explain (e.g., PYTHON_LO001). Optional with --all."),
    ] = None,
    all_rules: Annotated[
        bool,
        typer.Option("--all", help="List all registered rules with title and severity."),
    ] = False,
) -> None:
    """Show the handbook section and linked ADR for RULE_ID, or list all rules with --all."""
    if rule_id is not None and all_rules:
        console.print(
            "[red]Error:[/red] use either RULE_ID or --all, not both.",
        )
        raise typer.Exit(code=1)

    if all_rules:
        _print_all_rules()
        return

    if rule_id is None:
        # No argument and no --all: print friendly guidance.
        console.print(
            "Usage: intendant explain RULE_ID\n"
            "       intendant explain --all\n\n"
            "Provide a rule ID (e.g. PYTHON_LO001) to see its handbook entry,\n"
            "or pass --all to list every registered rule."
        )
        return

    _print_single_rule(rule_id)


def _print_all_rules() -> None:
    """Print a Rich table of all registered rules, grouped by severity."""
    rules = collect_rules()
    rules_sorted = sorted(
        rules,
        key=lambda r: (_SEVERITY_ORDER.get(r.severity, 99), r.id),
    )

    table = Table(title="All registered rules", show_header=True, header_style="bold cyan")
    table.add_column("Rule ID", style="bold", no_wrap=True)
    table.add_column("Severity", no_wrap=True)
    table.add_column("Stacks", no_wrap=True)
    table.add_column("Title")

    severity_colors = {
        "required": "red",
        "recommended": "yellow",
        "optional": "green",
    }

    for rule in rules_sorted:
        stacks_text = ", ".join(rule.stacks) if rule.stacks else "*"
        color = severity_colors.get(rule.severity, "white")
        table.add_row(
            rule.id,
            f"[{color}]{rule.severity}[/{color}]",
            stacks_text,
            rule.title,
        )

    console.print(table)


def _print_single_rule(rule_id: str) -> None:
    """Print the handbook entry (and ADR if available) for a single rule."""
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
