"""Tests for Python adapter PK rules."""

from pathlib import Path

from suzerain.adapters.python.pk import (
    PK001PyprojectExists,
    PK002UvLock,
    PK003PythonVersion,
    _resolve_python_version,
)
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


# ---------------------------------------------------------------------------
# PK003 fix() tests
# ---------------------------------------------------------------------------


def test_pk003_fix_reads_requires_python(tmp_path: Path) -> None:
    """fix() uses the minimum version from requires-python in pyproject.toml."""
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "x"\nrequires-python = ">=3.10"\n')
    repo = Repo(path=tmp_path, stack="python")
    result = PK003PythonVersion().check(repo)
    assert result.passing is False
    patch = PK003PythonVersion().fix(repo, result)
    assert patch is not None
    assert patch.safe is True
    assert "3.10" in patch.content
    assert patch.kind == "create"
    assert ".python-version" in str(patch.target_path)


def test_pk003_fix_fallback_when_no_pyproject(tmp_path: Path) -> None:
    """fix() falls back to system python or '3.11' when pyproject.toml is absent."""
    repo = Repo(path=tmp_path, stack="python")
    result = PK003PythonVersion().check(repo)
    assert result.passing is False
    patch = PK003PythonVersion().fix(repo, result)
    assert patch is not None
    # Version must look like X.Y
    import re

    assert re.match(r"\d+\.\d+", patch.content.strip())


def test_pk003_fix_diff_format(tmp_path: Path) -> None:
    """fix() produces a unified diff referencing .python-version."""
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "x"\nrequires-python = ">=3.12"\n')
    repo = Repo(path=tmp_path, stack="python")
    result = PK003PythonVersion().check(repo)
    patch = PK003PythonVersion().fix(repo, result)
    assert patch is not None
    assert ".python-version" in patch.diff
    assert "3.12" in patch.diff


def test_resolve_python_version_from_pyproject(tmp_path: Path) -> None:
    """_resolve_python_version extracts the minor from requires-python."""
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "x"\nrequires-python = ">=3.11,<4"\n'
    )
    repo = Repo(path=tmp_path, stack="python")
    assert _resolve_python_version(repo) == "3.11"


def test_resolve_python_version_no_pyproject(tmp_path: Path) -> None:
    """_resolve_python_version returns a valid X.Y string even without pyproject."""
    import re

    repo = Repo(path=tmp_path, stack="python")
    version = _resolve_python_version(repo)
    assert re.match(r"\d+\.\d+", version)
