"""Intendant CLI entrypoint."""

from typing import Annotated

import typer

from intendant import __version__
from intendant.commands import audit as audit_cmd
from intendant.commands import doctor as doctor_cmd
from intendant.commands import explain as explain_cmd
from intendant.commands import init as init_cmd
from intendant.commands import mcp as mcp_cmd
from intendant.commands import new as new_cmd
from intendant.commands import report as report_cmd

app = typer.Typer(
    name="intendant",
    help="Multi-stack project governance framework.",
    no_args_is_help=False,
    add_completion=False,
)


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"intendant {__version__}")
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
    """Intendant entrypoint callback."""
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())


app.command("explain")(explain_cmd.explain)
app.command("init")(init_cmd.init)
app.command("audit")(audit_cmd.audit)
app.command("doctor")(doctor_cmd.doctor)
app.command("new")(new_cmd.new)
app.command("report")(report_cmd.report)
app.command("mcp")(mcp_cmd.mcp)


def main() -> None:
    """Run the CLI."""
    app()
