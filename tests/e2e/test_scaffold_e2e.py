"""End-to-end test: scaffold a new repo and verify it audits clean."""

import subprocess
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


@pytest.mark.e2e()
def test_scaffold_claude_skill_passes_required_audit(tmp_path: Path) -> None:
    """Success criterion: fresh claude-skill scaffold passes suzerain audit --severity=required."""
    target = tmp_path / "my-test-skill"
    suzerain_repo = Path(__file__).resolve().parents[2]
    proc = subprocess.run(
        [
            "uv",
            "run",
            "suzerain",
            "new",
            "my-test-skill",
            "--stack",
            "claude-skill",
            "--path",
            str(tmp_path),
        ],
        cwd=suzerain_repo,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, f"scaffold failed: {proc.stderr}"
    assert target.is_dir()
    # SKILL.md must exist at the expected nested location
    assert (target / "my-test-skill" / "SKILL.md").is_file()
    # evals/ must have at least one file (SK005)
    evals_files = list((target / "my-test-skill" / "evals").iterdir())
    assert any(f.is_file() for f in evals_files)
    # README must mention install path (SK007)
    readme_text = (target / "README.md").read_text()
    assert "~/.claude/skills/" in readme_text
    # Audit must pass at required severity
    audit_proc = subprocess.run(
        ["uv", "run", "suzerain", "audit", str(target), "--severity=required"],
        cwd=suzerain_repo,
        capture_output=True,
        text=True,
    )
    assert audit_proc.returncode == 0, (
        f"audit failed:\nstdout:\n{audit_proc.stdout}\nstderr:\n{audit_proc.stderr}"
    )
