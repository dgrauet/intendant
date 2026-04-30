"""`suzerain init` — create .suzerain.toml + adoption ADR in the current repo."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Annotated

import tomli_w
import typer
from rich.console import Console

from suzerain.core.repo import Repo

console = Console()

_ADOPTION_ADR_TEMPLATE = """# ADR-0000 : Adopt suzerain

- **Statut** : accepted
- **Date** : {today}
- **Stacks concernées** : * (transverse)

## Contexte

Ce repo adopte [suzerain](https://github.com/dgrauet/suzerain) comme framework
de gouvernance — handbook, audit (palier 2), scaffolder (palier 3). Le fichier
`.suzerain.toml` à la racine du repo déclare la stack, le mode de conformité
appliqué, et les exemptions justifiées.

## Décision

- Stack détectée à l'adoption : `{stack}`
- Mode initial : `advisory` (les findings sont rapportés mais ne bloquent rien).
- Toutes les ADRs futures du repo numérotées à partir de 0001.

## Conséquences

- L'auditeur (palier 2 de suzerain) pourra rouler sur ce repo et rapporter
  les écarts vs le baseline.
- Les exemptions doivent être listées dans `.suzerain.toml` avec une raison.

## Alternatives considérées

- Ne rien adopter (garder les conventions implicites). Rejeté : la dette
  conventionnelle s'accumule en silence.
- Adopter un autre framework : aucun équivalent multi-stack identifié au
  moment de l'adoption.

## Porte de sortie / révision

- Si suzerain ne suit plus l'évolution des outils, basculer en `mode = advisory`
  permanent et reprendre les standards à la main.
- Si un baseline `v2` casse trop de règles : geler à `version = "1"` et planifier
  une migration ciblée.
"""


def init(
    path: Annotated[
        Path,
        typer.Option(
            "--path",
            help="Target repo path (defaults to current directory).",
        ),
    ] = Path("."),
    force: Annotated[
        bool,
        typer.Option(
            "--force",
            help="Overwrite an existing .suzerain.toml.",
        ),
    ] = False,
) -> None:
    """Create .suzerain.toml + ADR-0000 in the target repo."""
    target = path.resolve()
    if not target.is_dir():
        console.print(f"[red]Target path does not exist or is not a directory: {target}[/red]")
        raise typer.Exit(code=1)

    config_path = target / ".suzerain.toml"
    if config_path.exists() and not force:
        console.print(
            f"[red].suzerain.toml already exists at {config_path}. Use --force to overwrite.[/red]"
        )
        raise typer.Exit(code=1)

    repo = Repo.from_path(target)

    config_data = {
        "suzerain": {
            "version": "1",
            "stack": repo.stack,
            "mode": "advisory",
        },
        "exemptions": {},
    }
    config_path.write_bytes(tomli_w.dumps(config_data).encode("utf-8"))
    console.print(f"[green]Wrote[/green] {config_path}")

    adr_dir = target / "docs" / "adr"
    adr_dir.mkdir(parents=True, exist_ok=True)
    adoption_adr = adr_dir / "0000-adopt-suzerain.md"
    if adoption_adr.exists():
        console.print(
            f"[yellow]ADR 0000 already exists at {adoption_adr}, leaving it untouched.[/yellow]"
        )
    else:
        adoption_adr.write_text(
            _ADOPTION_ADR_TEMPLATE.format(today=date.today().isoformat(), stack=repo.stack),
            encoding="utf-8",
        )
        console.print(f"[green]Wrote[/green] {adoption_adr}")

    console.print()
    console.print("[bold]Next steps:[/bold]")
    console.print(r"  1. Review .suzerain.toml and adjust \[exemptions] as needed.")
    console.print("  2. Commit the new files.")
    console.print("  3. Run `suzerain explain <RULE_ID>` to read any specific rule.")
