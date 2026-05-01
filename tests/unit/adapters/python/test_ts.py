"""Tests for Python adapter TS rules."""

from pathlib import Path

from suzerain.adapters.python.ts import TS001Pytest, TS003CoverageConfigured
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


# ---------------------------------------------------------------------------
# TS003CoverageConfigured
# ---------------------------------------------------------------------------


def test_ts003_pass_with_coverage_run(tmp_path: Path) -> None:
    """[tool.coverage.run] is enough — coverage is a subtable of tool.coverage."""
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "x"\n[tool.coverage.run]\nsource = ["src"]\n'
    )
    repo = Repo(path=tmp_path, stack="python")
    assert TS003CoverageConfigured().check(repo).passing is True


def test_ts003_pass_with_coverage_report(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "x"\n[tool.coverage.report]\nshow_missing = true\n'
    )
    repo = Repo(path=tmp_path, stack="python")
    assert TS003CoverageConfigured().check(repo).passing is True


def test_ts003_fail_no_coverage_section(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "x"\n')
    repo = Repo(path=tmp_path, stack="python")
    result = TS003CoverageConfigured().check(repo)
    assert result.passing is False
    assert "coverage" in result.evidence.lower()


def test_ts003_skip_no_pyproject(tmp_path: Path) -> None:
    """No pyproject.toml → skip (pass with evidence)."""
    repo = Repo(path=tmp_path, stack="python")
    result = TS003CoverageConfigured().check(repo)
    assert result.passing is True
    assert "no pyproject" in result.evidence.lower() or "skip" in result.evidence.lower()


def test_ts003_metadata() -> None:
    rule = TS003CoverageConfigured()
    assert rule.id == "TS003"
    assert rule.severity == "recommended"
    assert "python" in rule.stacks
