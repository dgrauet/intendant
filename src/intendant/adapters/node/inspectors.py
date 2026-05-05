"""Helpers shared by Node rule check methods."""

from __future__ import annotations

import json
from pathlib import Path


def has_package_json(repo_path: Path) -> bool:
    return (repo_path / "package.json").is_file()


def load_package_json(repo_path: Path) -> dict | None:
    """Load package.json as a dict. Returns None if missing or unparseable."""
    path = repo_path / "package.json"
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError:
        return None


def collect_dep_names(pkg: dict) -> set[str]:
    """Return all package names declared in dependencies, devDependencies,
    peerDependencies, optionalDependencies — lowercased."""
    out: set[str] = set()
    for section in (
        "dependencies",
        "devDependencies",
        "peerDependencies",
        "optionalDependencies",
    ):
        section_deps = pkg.get(section)
        if isinstance(section_deps, dict):
            out.update(name.lower() for name in section_deps)
    return out
