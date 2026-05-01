"""End-to-end test: scaffold a new repo and verify it audits clean."""

import tomllib
from pathlib import Path

import pytest
from typer.testing import CliRunner

from suzerain.cli import app

runner = CliRunner()


@pytest.mark.e2e()
def test_scaffold_then_audit_passes_required(tmp_path: Path) -> None:
    """Scaffold a new project and immediately audit it. Required rules must pass."""
    # Step 1: scaffold (with git init so RL002 has a commit to inspect)
    result_new = runner.invoke(
        app,
        [
            "new",
            "scaffold-e2e",
            "--stack",
            "python",
            "--description",
            "e2e fixture",
            "--author",
            "Test",
            "--path",
            str(tmp_path),
        ],
    )
    assert result_new.exit_code == 0, result_new.stdout
    target = tmp_path / "scaffold-e2e"
    assert target.is_dir()

    # Step 2: audit the scaffolded repo
    # We invoke suzerain via the CLI so the registry picks up the real rules.
    result_audit = runner.invoke(
        app,
        ["audit", str(target), "--severity", "required"],
    )
    assert result_audit.exit_code == 0, (
        f"Scaffolded project failed required audit:\n{result_audit.stdout}"
    )


@pytest.mark.e2e()
def test_scaffold_creates_uv_lock_capable_project(tmp_path: Path) -> None:
    """The scaffolded pyproject.toml is valid for `uv lock`.

    Note: we don't actually run `uv lock` (network-bound, slow). We only
    verify the pyproject parses and has the necessary fields.
    """
    runner.invoke(
        app,
        [
            "new",
            "lockable",
            "--stack",
            "python",
            "--author",
            "T",
            "--path",
            str(tmp_path),
            "--no-git",
        ],
    )
    target = tmp_path / "lockable"
    pyproject_text = (target / "pyproject.toml").read_text()
    data = tomllib.loads(pyproject_text)
    assert "project" in data
    assert data["project"]["name"] == "lockable"
    assert data["project"]["requires-python"]
    assert "build-system" in data
