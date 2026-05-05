"""Tests for the intendant CLI entrypoint."""

from typer.testing import CliRunner

from intendant import __version__
from intendant.cli import app

runner = CliRunner()


def test_cli_version_flag_prints_version() -> None:
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert __version__ in result.stdout


def test_cli_no_args_shows_help() -> None:
    result = runner.invoke(app, [])
    assert result.exit_code == 0
    assert "intendant" in result.stdout.lower()
