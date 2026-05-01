"""Helpers shared by skill rule check/fix methods."""

from __future__ import annotations

from pathlib import Path

_EXCLUDED_PARTS = frozenset(
    {
        ".git",
        "node_modules",
        "__pycache__",
        ".venv",
        ".tox",
        "dist",
        "build",
    }
)


def find_skill_md(repo_path: Path) -> Path | None:
    """Locate a single SKILL.md at depth 1 or 2 below ``repo_path``.

    Returns the alphabetically-first match for determinism. Depth-1
    matches take precedence over depth-2 matches. Excludes paths that
    pass through any directory in ``_EXCLUDED_PARTS``. Returns ``None``
    if no SKILL.md is found.
    """
    for depth in (1, 2):
        pattern = "*/" * (depth - 1) + "SKILL.md"
        candidates = sorted(
            p
            for p in repo_path.glob(pattern)
            if not (set(p.relative_to(repo_path).parts) & _EXCLUDED_PARTS)
        )
        if candidates:
            return candidates[0]
    return None
