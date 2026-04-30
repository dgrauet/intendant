"""Tests for Python adapter TS rules."""

from pathlib import Path

from suzerain.adapters.python.ts import TS001Pytest
from suzerain.core.repo import Repo


def test_ts001_pass_with_pyproject_pytest_ini_options(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "x"\n[tool.pytest.ini_options]\ntestpaths = ["tests"]\n'
    )
    repo = Repo(path=tmp_path, stack="python")
    assert TS001Pytest().check(repo).passing is True


def test_ts001_pass_with_pytest_ini(tmp_path: Path) -> None:
    (tmp_path / "pytest.ini").write_text("[pytest]\naddopts = -v\n")
    repo = Repo(path=tmp_path, stack="python")
    assert TS001Pytest().check(repo).passing is True


def test_ts001_pass_with_tests_conftest(tmp_path: Path) -> None:
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "conftest.py").write_text("")
    repo = Repo(path=tmp_path, stack="python")
    assert TS001Pytest().check(repo).passing is True


def test_ts001_fail_when_no_pytest_configuration(tmp_path: Path) -> None:
    repo = Repo(path=tmp_path, stack="python")
    result = TS001Pytest().check(repo)
    assert result.passing is False
