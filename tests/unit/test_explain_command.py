"""Tests for the suzerain explain command."""

import shutil
from pathlib import Path

import pytest
from typer.testing import CliRunner

from suzerain.cli import app

runner = CliRunner()


@pytest.fixture()
def fake_root(fixtures_dir: Path) -> Path:
    """Build a fake suzerain root with docs/handbook + docs/adr from handbook_mini."""
    root = fixtures_dir / "handbook_mini_root"
    if not root.exists():
        (root / "docs").mkdir(parents=True, exist_ok=True)
        shutil.copytree(fixtures_dir / "handbook_mini", root / "docs", dirs_exist_ok=True)
    return root


def test_explain_existing_rule(fake_root: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SUZERAIN_ROOT", str(fake_root))
    result = runner.invoke(app, ["explain", "XX001"])
    assert result.exit_code == 0
    assert "XX001" in result.stdout
    assert "Première règle de test" in result.stdout
    assert "marker.txt" in result.stdout
    assert "ADR-9999" in result.stdout


def test_explain_unknown_rule(fake_root: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SUZERAIN_ROOT", str(fake_root))
    result = runner.invoke(app, ["explain", "ZZ999"])
    assert result.exit_code == 1
    assert "not found" in result.stdout.lower()


def test_explain_rule_without_adr(fake_root: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SUZERAIN_ROOT", str(fake_root))
    result = runner.invoke(app, ["explain", "XX002"])
    assert result.exit_code == 0
    assert "XX002" in result.stdout
