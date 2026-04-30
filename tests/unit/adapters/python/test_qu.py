"""Tests for Python adapter QU rules."""

from pathlib import Path

from suzerain.adapters.python.qu import QU001Ruff, QU002Ty
from suzerain.core.repo import Repo


def test_qu001_pass_with_pyproject_section(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "x"\n[tool.ruff]\nline-length = 100\n'
    )
    repo = Repo(path=tmp_path, stack="python")
    assert QU001Ruff().check(repo).passing is True


def test_qu001_pass_with_ruff_toml(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "x"\n')
    (tmp_path / "ruff.toml").write_text("line-length = 100\n")
    repo = Repo(path=tmp_path, stack="python")
    assert QU001Ruff().check(repo).passing is True


def test_qu001_fail(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "x"\n')
    repo = Repo(path=tmp_path, stack="python")
    result = QU001Ruff().check(repo)
    assert result.passing is False


def test_qu002_pass_with_ty_in_dev_deps(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "x"\n[dependency-groups]\ndev = ["ty>=0.0.1"]\n'
    )
    repo = Repo(path=tmp_path, stack="python")
    assert QU002Ty().check(repo).passing is True


def test_qu002_pass_with_optional_deps(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "x"\n[project.optional-dependencies]\ndev = ["ty>=0.0.1"]\n'
    )
    repo = Repo(path=tmp_path, stack="python")
    assert QU002Ty().check(repo).passing is True


def test_qu002_pass_when_pyright_present_as_fallback(tmp_path: Path) -> None:
    """ADR-0003 documents pyright as fallback. QU002 accepts it."""
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "x"\n[dependency-groups]\ndev = ["pyright>=1.1"]\n'
    )
    repo = Repo(path=tmp_path, stack="python")
    result = QU002Ty().check(repo)
    assert result.passing is True
    assert "pyright" in result.evidence.lower() or "fallback" in result.evidence.lower()


def test_qu002_fail_no_typechecker(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "x"\n[dependency-groups]\ndev = ["pytest"]\n'
    )
    repo = Repo(path=tmp_path, stack="python")
    result = QU002Ty().check(repo)
    assert result.passing is False
