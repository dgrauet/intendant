"""Helpers shared by skill rule check/fix methods."""

from __future__ import annotations

import re
from pathlib import Path

import yaml

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

_FRONTMATTER_RE = re.compile(r"^---\n(.*?\n)---\n", re.DOTALL)
_BOM = "﻿"


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


def parse_frontmatter(skill_md_path: Path) -> dict | None:
    """Extract and parse YAML frontmatter from a SKILL.md file.

    Returns the parsed dict, or ``None`` if frontmatter is absent or malformed.
    Treats UTF-8 BOM at file start as if it were not there.
    """
    text = skill_md_path.read_text(encoding="utf-8", errors="replace")
    if text.startswith(_BOM):
        text = text[len(_BOM) :]
    match = _FRONTMATTER_RE.match(text)
    if not match:
        return None
    try:
        data = yaml.safe_load(match.group(1))
    except yaml.YAMLError:
        return None
    return data if isinstance(data, dict) else None
