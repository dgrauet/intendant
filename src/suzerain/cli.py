"""Suzerain CLI entrypoint."""

from typing import Annotated

import typer

from suzerain import __version__
from suzerain.commands import audit as audit_cmd
from suzerain.commands import explain as explain_cmd
from suzerain.commands import init as init_cmd

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


app.command("explain")(explain_cmd.explain)
app.command("init")(init_cmd.init)
app.command("audit")(audit_cmd.audit)


def main() -> None:
    """Run the CLI."""
    app()
