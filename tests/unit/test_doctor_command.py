"""Tests for `intendant doctor`."""

from typer.testing import CliRunner

from intendant import __version__
from intendant.cli import app

runner = CliRunner()


def test_doctor_exits_zero_on_healthy_install() -> None:
    result = runner.invoke(app, ["doctor"])
    assert result.exit_code == 0
    assert __version__ in result.stdout


def test_doctor_reports_rule_count() -> None:
    result = runner.invoke(app, ["doctor"])
    assert "rules loaded" in result.stdout.lower() or "loaded" in result.stdout.lower()
