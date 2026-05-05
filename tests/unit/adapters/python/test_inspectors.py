"""Tests for Python inspector helpers."""

from pathlib import Path

from intendant.adapters.python.inspectors import (
    has_pyproject,
    load_pyproject,
    pyproject_tool_section,
)


def test_has_pyproject_true(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "x"\n')
    assert has_pyproject(tmp_path) is True


def test_has_pyproject_false(tmp_path: Path) -> None:
    assert has_pyproject(tmp_path) is False


def test_load_pyproject_returns_dict(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "x"\nversion = "1.0"\n')
    data = load_pyproject(tmp_path)
    assert data is not None
    assert data["project"]["name"] == "x"


def test_load_pyproject_returns_none_if_missing(tmp_path: Path) -> None:
    assert load_pyproject(tmp_path) is None


def test_load_pyproject_returns_none_on_parse_error(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text("not valid toml ===\n")
    assert load_pyproject(tmp_path) is None


def test_pyproject_tool_section(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "x"\n[tool.ruff]\nline-length = 100\n'
    )
    assert pyproject_tool_section(tmp_path, "ruff") == {"line-length": 100}


def test_pyproject_tool_section_missing(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "x"\n')
    assert pyproject_tool_section(tmp_path, "ruff") is None
