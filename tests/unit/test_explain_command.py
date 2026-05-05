"""Tests for the intendant explain command."""

import shutil
from pathlib import Path

import pytest
from typer.testing import CliRunner

from intendant.cli import app

runner = CliRunner()


@pytest.fixture()
def fake_root(fixtures_dir: Path) -> Path:
    """Build a fake intendant root with docs/handbook + docs/adr from handbook_mini."""
    root = fixtures_dir / "handbook_mini_root"
    if not root.exists():
        (root / "docs").mkdir(parents=True, exist_ok=True)
        shutil.copytree(fixtures_dir / "handbook_mini", root / "docs", dirs_exist_ok=True)
    return root


def test_explain_existing_rule(fake_root: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("INTENDANT_ROOT", str(fake_root))
    result = runner.invoke(app, ["explain", "XX001"])
    assert result.exit_code == 0
    assert "XX001" in result.stdout
    assert "First test rule" in result.stdout
    assert "marker.txt" in result.stdout
    assert "ADR-9999" in result.stdout


def test_explain_unknown_rule(fake_root: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("INTENDANT_ROOT", str(fake_root))
    result = runner.invoke(app, ["explain", "ZZ999"])
    assert result.exit_code == 1
    assert "not found" in result.stdout.lower()


def test_explain_rule_without_adr(fake_root: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("INTENDANT_ROOT", str(fake_root))
    result = runner.invoke(app, ["explain", "XX002"])
    assert result.exit_code == 0
    assert "XX002" in result.stdout


# --- D2: intendant explain --all ---


def test_explain_all_lists_every_registered_rule() -> None:
    """--all prints a table that includes rule IDs from every adapter."""
    result = runner.invoke(app, ["explain", "--all"])
    assert result.exit_code == 0
    # transverse rules
    assert "DG001" in result.stdout
    # python adapter
    assert "PYTHON_LO001" in result.stdout
    # claude-skill adapter
    assert "CLAUDE_SKILL_SK001" in result.stdout
    # node adapter
    assert "NODE_PK001" in result.stdout


def test_explain_with_neither_arg_nor_all_is_friendly() -> None:
    """Invoking explain with no args should not crash and print something sensible."""
    result = runner.invoke(app, ["explain"])
    # must not raise an unhandled exception
    assert result.exception is None
    # should print something (help text or a guidance message)
    assert len(result.stdout.strip()) > 0


def test_explain_with_both_rule_id_and_all_errors() -> None:
    """Passing both RULE_ID and --all is an error (exit 1)."""
    result = runner.invoke(app, ["explain", "PYTHON_LO001", "--all"])
    assert result.exit_code == 1
    combined = (result.stdout + (result.stderr or "")).lower()
    assert "both" in combined or "conflict" in combined or "either" in combined
