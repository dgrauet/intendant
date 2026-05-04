"""Repository detection and metadata."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

# Ordered: matters only for display, not for filtering — `detect_stacks`
# returns ALL stacks present at the root (multi-stack repos are first-class).
# Note: skill stack is detected separately (file-walk based, not flat marker)
# and is always listed first when present.
_STACK_MARKERS: dict[str, tuple[str, ...]] = {
    "python": ("pyproject.toml",),
    "node": ("package.json",),
    "rust": ("Cargo.toml",),
    "go": ("go.mod",),
    "swift": ("Package.swift",),
}


def detect_stacks(path: Path) -> tuple[str, ...]:
    """Return every stack auto-detected at ``path``.

    Walks the markers in ``_STACK_MARKERS`` and ``claude-skill`` and collects
    each match. An empty list means nothing was detected (the caller decides
    what that means — usually display ``mode=auto`` with no stack).

    Raises ``FileNotFoundError`` if ``path`` does not exist.
    """
    if not path.exists():
        raise FileNotFoundError(f"path does not exist: {path}")
    # Lazy import to avoid circular: adapters depend on core, not the reverse.
    from suzerain.adapters.claude_skill.inspectors import find_skill_md

    found: list[str] = []
    if find_skill_md(path) is not None:
        found.append("claude-skill")
    for stack, markers in _STACK_MARKERS.items():
        if any((path / marker).is_file() for marker in markers):
            found.append(stack)
    return tuple(found)


@dataclass(frozen=True)
class Repo:
    """A repository with its stack composition.

    ``stacks`` lists every language/stack that applies to this repo. When
    the list is empty under ``mode="auto"``, no stack-specific adapter
    matched and only transverse rules will run.

    ``mode`` records *how* the composition was determined:
    - ``auto``  — derived from filesystem markers via ``detect_stacks``.
    - ``manual`` — pinned in ``.suzerain.toml`` (top-level ``stack`` or via
      ``[[subprojects]]``).
    """

    path: Path
    stacks: tuple[str, ...] = ()
    mode: Literal["auto", "manual"] = "auto"
    name: str | None = None  # subproject name; None for root meta-Repo or single-subproject

    @classmethod
    def from_path(cls, path: Path) -> Repo:
        """Build a Repo by auto-detecting stacks from the filesystem."""
        return cls(path=path, stacks=detect_stacks(path), mode="auto")
