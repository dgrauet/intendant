"""Suzerain CLI entrypoint."""

from typing import Annotated

import typer

from suzerain import __version__

app = typer.Typer(
    name="suzerain",
    help="Multi-stack project governance framework.",
    no_args_is_help=False,
    add_completion=False,
)


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"suzerain {__version__}")
        raise typer.Exit()


@app.callback(invoke_without_command=True)
def main_callback(
    ctx: typer.Context,
    version: Annotated[
        bool | None,
        typer.Option(
            "--version",
            callback=_version_callback,
            is_eager=True,
            help="Show the version and exit.",
        ),
    ] = None,
) -> None:
    """Suzerain entrypoint callback."""
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())


def main() -> None:
    """Run the CLI."""
    app()
