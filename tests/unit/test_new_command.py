"""Tests for `suzerain new`."""

import subprocess
import tomllib
from pathlib import Path

from typer.testing import CliRunner

from suzerain.cli import app

runner = CliRunner()


def test_new_creates_python_project(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        [
            "new",
            "my-app",
            "--stack",
            "python",
            "--description",
            "Test app",
            "--author",
            "Test",
            "--path",
            str(tmp_path),
            "--no-git",
        ],
    )
    assert result.exit_code == 0, result.stdout
    target = tmp_path / "my-app"
    assert target.is_dir()
    assert (target / "pyproject.toml").is_file()
    assert (target / "src" / "my_app" / "__init__.py").is_file()


def test_new_refuses_existing_target(tmp_path: Path) -> None:
    target = tmp_path / "exists"
    target.mkdir()
    result = runner.invoke(
        app,
        ["new", "exists", "--stack", "python", "--path", str(tmp_path), "--no-git"],
    )
    assert result.exit_code == 1
    assert "exists" in result.stdout.lower() or "already" in result.stdout.lower()


def test_new_unknown_stack(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        ["new", "x", "--stack", "rust", "--path", str(tmp_path), "--no-git"],
    )
    assert result.exit_code == 1
    assert "rust" in result.stdout.lower() or "stack" in result.stdout.lower()


def test_new_with_git_inits_repo(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        [
            "new",
            "git-test",
            "--stack",
            "python",
            "--description",
            "x",
            "--author",
            "T",
            "--path",
            str(tmp_path),
        ],
    )
    assert result.exit_code == 0, result.stdout
    target = tmp_path / "git-test"
    assert (target / ".git").is_dir()
    log = subprocess.run(
        ["git", "log", "--format=%s"],
        cwd=target,
        capture_output=True,
        text=True,
        check=True,
    )
    assert "scaffold from suzerain" in log.stdout


def test_new_substitutes_placeholders(tmp_path: Path) -> None:
    runner.invoke(
        app,
        [
            "new",
            "subtest",
            "--stack",
            "python",
            "--description",
            "Substitution test",
            "--author",
            "Tester",
            "--path",
            str(tmp_path),
            "--no-git",
        ],
    )
    target = tmp_path / "subtest"
    pyproject = tomllib.loads((target / "pyproject.toml").read_text())
    assert pyproject["project"]["name"] == "subtest"
    assert pyproject["project"]["description"] == "Substitution test"
    license_text = (target / "LICENSE").read_text()
    assert "Tester" in license_text
