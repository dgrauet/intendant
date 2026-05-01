"""`suzerain new <name> --stack=...` — scaffold a new conformant repo."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from suzerain.scaffold.engine import scaffold_project
from suzerain.scaffold.substitutions import SubstitutionContext

console = Console()


def new(
    name: Annotated[
        str,
        typer.Argument(help="Project name (becomes the directory + pyproject name)."),
    ],
    stack: Annotated[
        str,
        typer.Option("--stack", help="Target stack. Currently supported: python."),
    ] = "python",
    description: Annotated[
        str,
        typer.Option("--description", help="Short project description."),
    ] = "",
    author: Annotated[
        str | None,
        typer.Option("--author", help="Author name (default: git config user.name)."),
    ] = None,
    path: Annotated[
        Path,
        typer.Option("--path", help="Parent directory in which to create the project."),
    ] = Path("."),
    no_git: Annotated[
        bool,
        typer.Option("--no-git", help="Skip git init + initial commit."),
    ] = False,
) -> None:
    """Scaffold a new conformant suzerain project."""
    target = (path / name).resolve()
    context = SubstitutionContext.from_minimal(
        project_name=name,
        stack=stack,
        description=description,
        author=author,
    )
    try:
        scaffold_project(target, stack, context)
    except FileExistsError:
        console.print(f"[red]Target already exists: {target}[/red]")
        raise typer.Exit(code=1) from None
    except ValueError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(code=1) from None

    console.print(f"[green]Scaffolded[/green] {target}")

    if not no_git:
        _git_init_and_commit(target)
        console.print("[green]Initialized git repo with first commit.[/green]")

    _print_quickstart(target, stack)


def _git_init_and_commit(target: Path) -> None:
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=target, check=True)
    subprocess.run(["git", "add", "-A"], cwd=target, check=True)
    subprocess.run(
        ["git", "commit", "-q", "-m", "chore: scaffold from suzerain v1"],
        cwd=target,
        check=True,
    )


def _print_quickstart(target: Path, stack: str) -> None:
    console.print()
    console.print("[bold]Next steps:[/bold]")
    if stack == "python":
        console.print(f"  cd {target}")
        console.print("  uv sync                      # install deps and create venv")
        console.print("  uv run pre-commit install    # activate hooks")
        console.print("  uv run pytest                # run the (empty) test suite")
        console.print("  suzerain audit . --severity=required   # verify the scaffold conforms")
