"""Tests for Python adapter QU rules."""

from pathlib import Path

from intendant.adapters.python.qu import (
    QU001Ruff,
    QU002Ty,
    QU003StrictTypeAnnotations,
    QU004TyCheck,
)
from intendant.core.repo import Repo
from intendant.core.rule import CheckResult


def test_qu001_pass_with_pyproject_section(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "x"\n[tool.ruff]\nline-length = 100\n'
    )
    repo = Repo(path=tmp_path, stacks=("python",))
    assert QU001Ruff().check(repo).passing is True


def test_qu001_pass_with_ruff_toml(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "x"\n')
    (tmp_path / "ruff.toml").write_text("line-length = 100\n")
    repo = Repo(path=tmp_path, stacks=("python",))
    assert QU001Ruff().check(repo).passing is True


def test_qu001_fail(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "x"\n')
    repo = Repo(path=tmp_path, stacks=("python",))
    result = QU001Ruff().check(repo)
    assert result.passing is False


def test_qu002_pass_with_ty_in_dev_deps(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "x"\n[dependency-groups]\ndev = ["ty>=0.0.1"]\n'
    )
    repo = Repo(path=tmp_path, stacks=("python",))
    assert QU002Ty().check(repo).passing is True


def test_qu002_pass_with_optional_deps(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "x"\n[project.optional-dependencies]\ndev = ["ty>=0.0.1"]\n'
    )
    repo = Repo(path=tmp_path, stacks=("python",))
    assert QU002Ty().check(repo).passing is True


def test_qu002_pass_when_pyright_present_as_fallback(tmp_path: Path) -> None:
    """ADR-0003 documents pyright as fallback. QU002 accepts it."""
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "x"\n[dependency-groups]\ndev = ["pyright>=1.1"]\n'
    )
    repo = Repo(path=tmp_path, stacks=("python",))
    result = QU002Ty().check(repo)
    assert result.passing is True
    assert "pyright" in result.evidence.lower() or "fallback" in result.evidence.lower()


def test_qu002_fail_no_typechecker(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "x"\n[dependency-groups]\ndev = ["pytest"]\n'
    )
    repo = Repo(path=tmp_path, stacks=("python",))
    result = QU002Ty().check(repo)
    assert result.passing is False


def test_qu004_skipped_when_no_typechecker(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "x"\n[dependency-groups]\ndev = ["pytest"]\n'
    )
    repo = Repo(path=tmp_path, stacks=("python",))
    rule = QU004TyCheck()
    assert rule.applies(repo) is False  # no ty/pyright → skip


def test_qu004_applies_when_ty_in_deps(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "x"\n[dependency-groups]\ndev = ["ty>=0.0.1"]\n'
    )
    repo = Repo(path=tmp_path, stacks=("python",))
    assert QU004TyCheck().applies(repo) is True


def test_qu004_applies_when_pyright_in_deps(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "x"\n[project.optional-dependencies]\ndev = ["pyright"]\n'
    )
    repo = Repo(path=tmp_path, stacks=("python",))
    assert QU004TyCheck().applies(repo) is True


def test_qu004_no_fix(tmp_path: Path) -> None:
    """QU004 has no auto-fix (type errors are application logic)."""
    rule = QU004TyCheck()
    repo = Repo(path=tmp_path, stacks=("python",))
    # Must NOT raise; just returns None.
    # We don't actually invoke check (subprocess) here — too slow + flaky.
    assert rule.fix(repo, CheckResult(passing=False, evidence="x")) is None


# ---------------------------------------------------------------------------
# QU003StrictTypeAnnotations
# ---------------------------------------------------------------------------


def test_qu003_skipped_when_no_pyproject(tmp_path: Path) -> None:
    repo = Repo(path=tmp_path, stacks=("python",))
    result = QU003StrictTypeAnnotations().check(repo)
    assert result.passing is True
    assert result.skipped is True


def test_qu003_passes_with_pyrightconfig_json(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "x"\n')
    (tmp_path / "pyrightconfig.json").write_text('{"typeCheckingMode": "strict"}\n')
    repo = Repo(path=tmp_path, stacks=("python",))
    assert QU003StrictTypeAnnotations().check(repo).passing is True


def test_qu003_passes_with_tool_ty_section(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "x"\n[tool.ty]\n')
    repo = Repo(path=tmp_path, stacks=("python",))
    assert QU003StrictTypeAnnotations().check(repo).passing is True


def test_qu003_passes_with_pyright_strict(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "x"\n[tool.pyright]\ntypeCheckingMode = "strict"\n'
    )
    repo = Repo(path=tmp_path, stacks=("python",))
    assert QU003StrictTypeAnnotations().check(repo).passing is True


def test_qu003_passes_with_mypy_strict(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "x"\n[tool.mypy]\nstrict = true\n')
    repo = Repo(path=tmp_path, stacks=("python",))
    assert QU003StrictTypeAnnotations().check(repo).passing is True


def test_qu003_fails_when_no_strict_config(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "x"\n[tool.ruff]\n')
    repo = Repo(path=tmp_path, stacks=("python",))
    result = QU003StrictTypeAnnotations().check(repo)
    assert result.passing is False
    assert "strict" in result.evidence.lower()
