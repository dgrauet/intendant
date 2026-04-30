"""Tests for Python adapter PK rules."""

from pathlib import Path

from suzerain.adapters.python.pk import PK001PyprojectExists, PK002UvLock, PK003PythonVersion
from suzerain.core.repo import Repo


def test_pk001_pass(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "x"\n')
    repo = Repo(path=tmp_path, stack="python")
    assert PK001PyprojectExists().check(repo).passing is True


def test_pk001_fail_missing(tmp_path: Path) -> None:
    repo = Repo(path=tmp_path, stack="python")
    result = PK001PyprojectExists().check(repo)
    assert result.passing is False


def test_pk001_fail_invalid_toml(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text("not valid toml ===\n")
    repo = Repo(path=tmp_path, stack="python")
    result = PK001PyprojectExists().check(repo)
    assert result.passing is False
    assert "parse" in result.evidence.lower() or "invalid" in result.evidence.lower()


def test_pk001_fail_missing_project_section(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text("[tool.foo]\nbar = 1\n")
    repo = Repo(path=tmp_path, stack="python")
    result = PK001PyprojectExists().check(repo)
    assert result.passing is False


def test_pk002_pass(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "x"\n')
    (tmp_path / "uv.lock").write_text("# lockfile\n")
    repo = Repo(path=tmp_path, stack="python")
    assert PK002UvLock().check(repo).passing is True


def test_pk002_fail_missing(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "x"\n')
    repo = Repo(path=tmp_path, stack="python")
    result = PK002UvLock().check(repo)
    assert result.passing is False


def test_pk003_pass(tmp_path: Path) -> None:
    (tmp_path / ".python-version").write_text("3.13\n")
    repo = Repo(path=tmp_path, stack="python")
    assert PK003PythonVersion().check(repo).passing is True


def test_pk003_fail_missing(tmp_path: Path) -> None:
    repo = Repo(path=tmp_path, stack="python")
    result = PK003PythonVersion().check(repo)
    assert result.passing is False
