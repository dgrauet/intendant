"""Tests for Python adapter LO rules."""

from pathlib import Path

from intendant.adapters.python.lo import LO001SrcLayout, LO002TestsAtRoot
from intendant.core.repo import Repo


def test_lo001_pass_with_src_layout(tmp_path: Path) -> None:
    (tmp_path / "src" / "mypackage").mkdir(parents=True)
    (tmp_path / "src" / "mypackage" / "__init__.py").write_text("")
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "mypackage"\n')
    repo = Repo(path=tmp_path, stacks=("python",))
    assert LO001SrcLayout().check(repo).passing is True


def test_lo001_fail_with_flat_layout(tmp_path: Path) -> None:
    (tmp_path / "mypackage").mkdir()
    (tmp_path / "mypackage" / "__init__.py").write_text("")
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "mypackage"\n')
    repo = Repo(path=tmp_path, stacks=("python",))
    result = LO001SrcLayout().check(repo)
    assert result.passing is False


def test_lo001_skip_when_no_pyproject(tmp_path: Path) -> None:
    """Without pyproject.toml, can't reliably tell — pass with note."""
    repo = Repo(path=tmp_path, stacks=("python",))
    result = LO001SrcLayout().check(repo)
    # Should not fail when there's no pyproject — let other rules catch that
    assert result.passing is True


def test_lo002_pass(tmp_path: Path) -> None:
    (tmp_path / "tests").mkdir()
    repo = Repo(path=tmp_path, stacks=("python",))
    assert LO002TestsAtRoot().check(repo).passing is True


def test_lo002_fail_no_tests_dir(tmp_path: Path) -> None:
    repo = Repo(path=tmp_path, stacks=("python",))
    result = LO002TestsAtRoot().check(repo)
    assert result.passing is False
