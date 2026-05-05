"""Tests for the intendant audit command."""

import json
import shutil
import subprocess
from pathlib import Path

import pytest
from typer.testing import CliRunner

from intendant.cli import app

runner = CliRunner()


def _setup_repo(tmp_path: Path, fixture_name: str, fixtures_dir: Path) -> Path:
    target = tmp_path / "target"
    shutil.copytree(fixtures_dir / fixture_name, target)
    # Initialize git so RL002 has commits to inspect
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=target, check=True)
    subprocess.run(["git", "config", "user.email", "t@t.t"], cwd=target, check=True)
    subprocess.run(["git", "config", "user.name", "T"], cwd=target, check=True)
    subprocess.run(["git", "add", "-A"], cwd=target, check=True)
    subprocess.run(
        ["git", "commit", "-q", "-m", "feat: initial scaffold"],
        cwd=target,
        check=True,
    )
    return target


def test_audit_conformant_repo_exits_zero(tmp_path: Path, fixtures_dir: Path) -> None:
    target = _setup_repo(tmp_path, "conformant_python_repo", fixtures_dir)
    result = runner.invoke(app, ["audit", str(target)])
    assert result.exit_code == 0, result.stdout


def test_audit_nonconformant_repo_exits_one(tmp_path: Path, fixtures_dir: Path) -> None:
    target = _setup_repo(tmp_path, "nonconformant_python_repo", fixtures_dir)
    result = runner.invoke(app, ["audit", str(target)])
    assert result.exit_code == 1


def test_audit_json_format(tmp_path: Path, fixtures_dir: Path) -> None:
    target = _setup_repo(tmp_path, "conformant_python_repo", fixtures_dir)
    result = runner.invoke(app, ["audit", str(target), "--format", "json"])
    assert result.exit_code == 0
    parsed = json.loads(result.stdout)
    assert parsed["repo_path"] == str(target)
    assert parsed["score"] >= 80


def test_audit_md_format(tmp_path: Path, fixtures_dir: Path) -> None:
    target = _setup_repo(tmp_path, "conformant_python_repo", fixtures_dir)
    result = runner.invoke(app, ["audit", str(target), "--format", "md"])
    assert result.exit_code == 0
    assert "## intendant audit" in result.stdout


def test_audit_severity_filter(tmp_path: Path, fixtures_dir: Path) -> None:
    """--severity=required only fails if a `required` rule fails."""
    target = _setup_repo(tmp_path, "conformant_python_repo", fixtures_dir)
    result = runner.invoke(app, ["audit", str(target), "--severity", "required"])
    assert result.exit_code == 0


def test_audit_default_path_is_cwd(
    tmp_path: Path, fixtures_dir: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    target = _setup_repo(tmp_path, "conformant_python_repo", fixtures_dir)
    monkeypatch.chdir(target)
    result = runner.invoke(app, ["audit"])
    assert result.exit_code == 0
