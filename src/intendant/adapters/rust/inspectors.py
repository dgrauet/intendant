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


def _workspace_member_globs(repo_path: Path) -> list[str]:
    """Return the `[workspace] members` glob patterns from Cargo.toml.

    Empty list when there is no workspace table or it declares no members.
    """
    cargo = load_cargo_toml(repo_path)
    if not cargo:
        return []
    workspace = cargo.get("workspace")
    if not isinstance(workspace, dict):
        return []
    members = workspace.get("members")
    if not isinstance(members, list):
        return []
    return [m for m in members if isinstance(m, str)]


def _crate_dirs(repo_path: Path) -> list[Path]:
    """Resolve the set of crate directories to scan for tests.

    Always includes the repo root (covers a plain package or the workspace
    root crate). For a Cargo *workspace*, each `members` entry is expanded —
    globs such as ``crates/*`` are resolved against the repo root — so that
    every member crate's ``src/`` and ``tests/`` get scanned.
    """
    dirs: list[Path] = [repo_path]
    for pattern in _workspace_member_globs(repo_path):
        # "." (and equivalents) is the workspace-root crate, already scanned.
        if pattern in ("", "."):
            continue
        # `glob` handles both literal members ("app") and globs ("crates/*").
        matched = sorted(repo_path.glob(pattern))
        if matched:
            dirs.extend(p for p in matched if p.is_dir())
        else:
            # Literal, non-glob member that exists on disk.
            candidate = repo_path / pattern
            if candidate.is_dir():
                dirs.append(candidate)
    return dirs


def find_test_annotations(repo_path: Path) -> list[Path]:
    """Return .rs files (under src/ or tests/) that contain a `#[test]` annotation.

    Scans the repo root plus every Cargo workspace member crate, so tests that
    live only in ``crates/<name>/src`` or ``crates/<name>/tests`` of a
    multi-crate workspace are not missed. Each matching file is reported once
    even when it is reachable from more than one crate directory.
    """
    hits: list[Path] = []
    seen: set[Path] = set()
    for crate_dir in _crate_dirs(repo_path):
        for sub in ("src", "tests"):
            root = crate_dir / sub
            if not root.is_dir():
                continue
            for rs in root.rglob("*.rs"):
                resolved = rs.resolve()
                if resolved in seen:
                    continue
                try:
                    if "#[test]" in rs.read_text(errors="replace"):
                        seen.add(resolved)
                        hits.append(rs)
                except OSError:
                    continue
    return hits
