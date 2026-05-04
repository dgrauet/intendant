"""Helpers shared by Rust rule check methods."""

from __future__ import annotations

import tomllib
from pathlib import Path
from typing import Any


def has_cargo_toml(repo_path: Path) -> bool:
    return (repo_path / "Cargo.toml").is_file()


def load_cargo_toml(repo_path: Path) -> dict[str, Any] | None:
    """Load Cargo.toml as a dict. Returns None if missing or unparseable."""
    path = repo_path / "Cargo.toml"
    if not path.is_file():
        return None
    try:
        return tomllib.loads(path.read_text())
    except (tomllib.TOMLDecodeError, UnicodeDecodeError):
        return None


def find_test_annotations(repo_path: Path) -> list[Path]:
    """Return .rs files (under src/ or tests/) that contain a `#[test]` annotation."""
    hits: list[Path] = []
    for sub in ("src", "tests"):
        root = repo_path / sub
        if not root.is_dir():
            continue
        for rs in root.rglob("*.rs"):
            try:
                if "#[test]" in rs.read_text(errors="replace"):
                    hits.append(rs)
            except OSError:
                continue
    return hits
