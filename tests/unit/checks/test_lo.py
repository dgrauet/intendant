"""Tests for transverse LO rules."""

from pathlib import Path

from suzerain.checks.lo import LO003DocsDirectory
from suzerain.core.repo import Repo


def _repo(tmp_path: Path) -> Repo:
    return Repo(path=tmp_path, stacks=("auto",))


def test_lo003_passes_when_docs_dir_exists(tmp_path: Path) -> None:
    (tmp_path / "docs").mkdir()
    assert LO003DocsDirectory().check(_repo(tmp_path)).passing is True


def test_lo003_fails_when_docs_dir_missing(tmp_path: Path) -> None:
    result = LO003DocsDirectory().check(_repo(tmp_path))
    assert result.passing is False
    assert "docs/" in result.evidence


def test_lo003_fails_when_docs_is_a_file(tmp_path: Path) -> None:
    (tmp_path / "docs").write_text("not a dir")
    assert LO003DocsDirectory().check(_repo(tmp_path)).passing is False
