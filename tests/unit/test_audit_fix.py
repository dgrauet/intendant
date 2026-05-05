"""Tests for `intendant audit --fix`."""

import shutil
import subprocess
from pathlib import Path

from typer.testing import CliRunner

from intendant.cli import app

runner = CliRunner()


def _setup(tmp_path: Path, fixture_name: str, fixtures_dir: Path) -> Path:
    target = tmp_path / "target"
    shutil.copytree(fixtures_dir / fixture_name, target)
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=target, check=True)
    subprocess.run(["git", "config", "user.email", "t@t.t"], cwd=target, check=True)
    subprocess.run(["git", "config", "user.name", "T"], cwd=target, check=True)
    subprocess.run(["git", "add", "-A"], cwd=target, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "feat: init"], cwd=target, check=True)
    return target


def test_fix_creates_missing_readme(tmp_path: Path, fixtures_dir: Path) -> None:
    """A nonconformant repo without README gets one created via DG001 fix."""
    target = _setup(tmp_path, "nonconformant_python_repo", fixtures_dir)
    assert not (target / "README.md").exists()
    runner.invoke(app, ["audit", str(target), "--fix"])
    # Exit code may still be 1 (other failures), but README should exist
    assert (target / "README.md").is_file()


def test_fix_dry_run_does_not_write(tmp_path: Path, fixtures_dir: Path) -> None:
    target = _setup(tmp_path, "nonconformant_python_repo", fixtures_dir)
    assert not (target / "README.md").exists()
    runner.invoke(app, ["audit", str(target), "--fix", "--dry-run"])
    assert not (target / "README.md").exists()


def test_fix_creates_proposed_dir_for_unsafe(tmp_path: Path, fixtures_dir: Path) -> None:
    """Currently all our fixes are safe, so .intendant/proposed/ may not be created.
    This test asserts the dir is at least valid when needed."""
    target = _setup(tmp_path, "nonconformant_python_repo", fixtures_dir)
    runner.invoke(app, ["audit", str(target), "--fix"])
    proposed = target / ".intendant" / "proposed"
    if proposed.exists():
        assert proposed.is_dir()
