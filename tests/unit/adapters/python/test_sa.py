"""Tests for Python adapter SA rules."""

from pathlib import Path

from intendant.adapters.python.sa import PYTHON_SA001GitignoreBaseline
from intendant.core.repo import Repo


def test_python_sa001_skipped_when_no_gitignore(tmp_path: Path) -> None:
    repo = Repo(path=tmp_path, stacks=("python",))
    result = PYTHON_SA001GitignoreBaseline().check(repo)
    assert result.passing is True
    assert result.skipped is True
    assert "SA004" in result.evidence


def test_python_sa001_passes_when_baseline_present(tmp_path: Path) -> None:
    (tmp_path / ".gitignore").write_text("__pycache__/\n.DS_Store\n.venv/\n")
    repo = Repo(path=tmp_path, stacks=("python",))
    result = PYTHON_SA001GitignoreBaseline().check(repo)
    assert result.passing is True
    assert "Python baseline" in result.evidence


def test_python_sa001_fails_when_pycache_missing(tmp_path: Path) -> None:
    (tmp_path / ".gitignore").write_text(".DS_Store\n.venv/\n")
    repo = Repo(path=tmp_path, stacks=("python",))
    result = PYTHON_SA001GitignoreBaseline().check(repo)
    assert result.passing is False
    assert "__pycache__/" in result.evidence


def test_python_sa001_fails_when_venv_missing(tmp_path: Path) -> None:
    (tmp_path / ".gitignore").write_text("__pycache__/\n.DS_Store\n")
    repo = Repo(path=tmp_path, stacks=("python",))
    result = PYTHON_SA001GitignoreBaseline().check(repo)
    assert result.passing is False
    assert ".venv/" in result.evidence


def test_python_sa001_fails_when_both_missing(tmp_path: Path) -> None:
    (tmp_path / ".gitignore").write_text(".DS_Store\n")
    repo = Repo(path=tmp_path, stacks=("python",))
    result = PYTHON_SA001GitignoreBaseline().check(repo)
    assert result.passing is False
    assert "__pycache__/" in result.evidence or ".venv/" in result.evidence


def test_python_sa001_metadata() -> None:
    rule = PYTHON_SA001GitignoreBaseline()
    assert rule.id == "PYTHON_SA001"
    assert rule.severity == "required"
    assert "python" in rule.stacks
