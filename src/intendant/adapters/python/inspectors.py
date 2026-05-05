"""Helpers shared by Python rule check/fix methods."""

from __future__ import annotations

import tomllib
from pathlib import Path


def has_pyproject(repo_path: Path) -> bool:
    return (repo_path / "pyproject.toml").is_file()


def load_pyproject(repo_path: Path) -> dict | None:
    """Load pyproject.toml as a dict. Returns None if missing or unparseable."""
    path = repo_path / "pyproject.toml"
    if not path.is_file():
        return None
    try:
        return tomllib.loads(path.read_text())
    except tomllib.TOMLDecodeError:
        return None


def pyproject_tool_section(repo_path: Path, tool: str) -> dict | None:
    """Return `[tool.<tool>]` section as dict, or None."""
    data = load_pyproject(repo_path)
    if data is None:
        return None
    return data.get("tool", {}).get(tool)
