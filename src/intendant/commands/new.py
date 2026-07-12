"""`intendant new <name> --stack=...` — scaffold a new conformant repo."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from intendant.scaffold.engine import scaffold_project
from intendant.scaffold.substitutions import SubstitutionContext

console = Console()


def new(
    name: Annotated[
        str,
        typer.Argument(help="Project name (becomes the directory + pyproject name)."),
    ],
    stack: Annotated[
        str,
        typer.Option(
            "--stack",
            help=(
                "Target stack. Currently supported: "
                "python, claude-skill, node, rust, go, swift, dotnet."
            ),
        ),
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
    """Scaffold a new conformant intendant project."""
    target = (path / name).resolve()
    # For claude-skill, a non-empty description is required by SK002/SK003.
    # Default to a placeholder that passes validation (>= 10 chars).
    if stack == "claude-skill" and not description:
        description = "Use this skill when [TODO: describe trigger condition for the skill]"
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

    # Only inject fallback identity if the user hasn't configured one.
    # git config --get searches local → global → system, so a new repo that
    # inherits the user's global config will return 0 here.
    has_email = (
        subprocess.run(
            ["git", "config", "--get", "user.email"],
            cwd=target,
            capture_output=True,
        ).returncode
        == 0
    )
    has_name = (
        subprocess.run(
            ["git", "config", "--get", "user.name"],
            cwd=target,
            capture_output=True,
        ).returncode
        == 0
    )

    commit_args = ["git"]
    if not has_email:
        commit_args.extend(["-c", "user.email=intendant@scaffolder.local"])
    if not has_name:
        commit_args.extend(["-c", "user.name=intendant"])
    commit_args.extend(["commit", "-q", "-m", "chore: scaffold from intendant v1"])

    subprocess.run(commit_args, cwd=target, check=True)


def _print_quickstart(target: Path, stack: str) -> None:
    console.print()
    console.print("[bold]Next steps:[/bold]")
    if stack == "python":
        console.print(f"  cd {target}")
        console.print("  uv sync                      # install deps and create venv")
        console.print("  uv run pre-commit install    # activate hooks")
        console.print("  uv run pytest                # run the (empty) test suite")
        console.print("  intendant audit . --severity=required   # verify the scaffold conforms")
    elif stack == "claude-skill":
        console.print(f"  cd {target}")
        console.print("  # Edit <name>/SKILL.md to describe your skill")
        console.print("  # Add real eval cases to <name>/evals/")
        console.print("  intendant audit . --severity=required   # verify the scaffold conforms")
    elif stack == "node":
        console.print(f"  cd {target}")
        console.print("  npm install                  # install deps and generate lockfile")
        console.print("  npm test                     # run vitest")
        console.print("  npm run lint                 # run eslint")
        console.print("  npm run typecheck            # run tsc --noEmit")
        console.print("  intendant audit . --severity=required   # verify the scaffold conforms")
    elif stack == "rust":
        console.print(f"  cd {target}")
        console.print("  cargo build                  # generates Cargo.lock")
        console.print("  cargo test                   # run tests")
        console.print("  cargo clippy -- -D warnings  # lint")
        console.print("  cargo fmt                    # format")
        console.print("  intendant audit . --severity=required   # verify the scaffold conforms")
    elif stack == "go":
        console.print(f"  cd {target}")
        console.print("  go mod tidy                  # generates go.sum")
        console.print("  go test ./...                # run tests")
        console.print("  go vet ./...                 # vet")
        console.print("  golangci-lint run            # lint")
        console.print("  intendant audit . --severity=required   # verify the scaffold conforms")
    elif stack == "swift":
        console.print(f"  cd {target}")
        console.print("  swift package resolve        # generates Package.resolved")
        console.print("  swift build                  # build the package")
        console.print("  swift test                   # run XCTest suite")
        console.print("  swiftlint --strict           # lint (requires SwiftLint)")
        console.print("  intendant audit . --severity=required   # verify the scaffold conforms")
    elif stack == "dotnet":
        console.print(f"  cd {target}")
        console.print("  dotnet restore               # generates packages.lock.json")
        console.print("  dotnet build                 # build the project")
        console.print("  dotnet test                  # run xunit suite")
        console.print("  dotnet format --verify-no-changes   # format check")
        console.print("  intendant audit . --severity=required   # verify the scaffold conforms")
