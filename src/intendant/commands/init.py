"""`intendant init` — create .intendant.toml + adoption ADR in the current repo."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Annotated

import tomli_w
import typer
from rich.console import Console

from intendant.core.repo import Repo

console = Console()

_ADOPTION_ADR_TEMPLATE = """# ADR-0000 : Adopt intendant

- **Status** : accepted
- **Date** : {today}
- **Stacks** : * (transverse)

## Context

This repo adopts [intendant](https://github.com/dgrauet/intendant) as its
governance framework — handbook, audit (tier 2), scaffolder (tier 3). The
`.intendant.toml` file at the repo root declares the stack, the applied
compliance mode, and justified exemptions.

## Decision

- Stack detected at adoption: `{stack}`
- Initial mode: `advisory` (findings are reported but nothing is blocked).
- All future ADRs in this repo numbered starting from 0001.

## Consequences

- The auditor (intendant tier 2) can run on this repo and report
  deviations from the baseline.
- Exemptions must be listed in `.intendant.toml` with a reason.

## Alternatives considered

- Adopt nothing (keep implicit conventions). Rejected: conventional debt
  accumulates silently.
- Adopt another framework: no equivalent multi-stack framework identified at
  the time of adoption.

## Exit hatch / revision

- If intendant no longer tracks tool evolution, switch to `mode = advisory`
  permanently and manage the standards manually.
- If a `v2` baseline breaks too many rules: freeze at `version = "1"` and plan
  a targeted migration.
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
            help="Overwrite an existing .intendant.toml.",
        ),
    ] = False,
) -> None:
    """Create .intendant.toml + ADR-0000 in the target repo."""
    target = path.resolve()
    if not target.is_dir():
        console.print(f"[red]Target path does not exist or is not a directory: {target}[/red]")
        raise typer.Exit(code=1)

    config_path = target / ".intendant.toml"
    if config_path.exists() and not force:
        console.print(
            f"[red].intendant.toml already exists at {config_path}. Use --force to overwrite.[/red]"
        )
        raise typer.Exit(code=1)

    repo = Repo.from_path(target)

    intendant_block: dict[str, str] = {"version": "1", "enforcement": "advisory"}
    if len(repo.stacks) == 1:
        intendant_block["stack"] = repo.stacks[0]
    elif len(repo.stacks) > 1:
        console.print(
            f"[yellow]Detected multiple stacks ({list(repo.stacks)}); leaving "
            "auto-detection enabled. Convert to [[subprojects]] in .intendant.toml "
            "if you want per-directory rules.[/yellow]"
        )
    config_data = {"intendant": intendant_block, "exemptions": {}}
    config_path.write_bytes(tomli_w.dumps(config_data).encode("utf-8"))
    console.print(f"[green]Wrote[/green] {config_path}")

    adr_dir = target / "docs" / "adr"
    adr_dir.mkdir(parents=True, exist_ok=True)
    adoption_adr = adr_dir / "0000-adopt-intendant.md"
    if adoption_adr.exists():
        console.print(
            f"[yellow]ADR 0000 already exists at {adoption_adr}, leaving it untouched.[/yellow]"
        )
    else:
        adoption_adr.write_text(
            _ADOPTION_ADR_TEMPLATE.format(
                today=date.today().isoformat(),
                stack="/".join(repo.stacks) if repo.stacks else "auto",
            ),
            encoding="utf-8",
        )
        console.print(f"[green]Wrote[/green] {adoption_adr}")

    console.print()
    console.print("[bold]Next steps:[/bold]")
    console.print(r"  1. Review .intendant.toml and adjust \[exemptions] as needed.")
    console.print("  2. Commit the new files.")
    console.print("  3. Run `intendant explain <RULE_ID>` to read any specific rule.")
