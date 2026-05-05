"""Tests for transverse TS rules."""

from pathlib import Path

from intendant.checks.ts import TS002RegressionTestsLayout
from intendant.core.repo import Repo


def _repo(tmp_path: Path) -> Repo:
    return Repo(path=tmp_path, stacks=("auto",))


def test_ts002_skipped_when_no_regression_tests_dir(tmp_path: Path) -> None:
    result = TS002RegressionTestsLayout().check(_repo(tmp_path))
    assert result.passing is True
    assert result.skipped is True


def test_ts002_passes_when_regression_tests_has_files(tmp_path: Path) -> None:
    rt = tmp_path / "regression_tests"
    rt.mkdir()
    (rt / "test_smoke.py").write_text("# smoke test\n")
    result = TS002RegressionTestsLayout().check(_repo(tmp_path))
    assert result.passing is True
    assert "1 file" in result.evidence


def test_ts002_fails_when_regression_tests_is_empty(tmp_path: Path) -> None:
    (tmp_path / "regression_tests").mkdir()
    result = TS002RegressionTestsLayout().check(_repo(tmp_path))
    assert result.passing is False
    assert "empty" in result.evidence
