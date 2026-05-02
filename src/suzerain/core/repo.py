"""Repository detection and metadata."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

# Ordered: first match wins. Add stacks here as adapters arrive.
# Note: skill stack is detected separately (file-walk based, not flat marker)
# and takes precedence over file-marker stacks below.
_STACK_MARKERS: dict[str, tuple[str, ...]] = {
    "python": ("pyproject.toml",),
    "node": ("package.json",),
    "rust": ("Cargo.toml",),
}


def detect_stack(path: Path) -> str | None:
    """Return the detected stack for ``path``, or ``None`` if unknown.

    Detection order:
    1. ``skill`` if a SKILL.md exists at depth ≤ 2 (via skill adapter inspector).
    2. ``python``/``node``/``rust`` if their root marker file exists.

    Raises ``FileNotFoundError`` if ``path`` does not exist.
    """
    if not path.exists():
        raise FileNotFoundError(f"path does not exist: {path}")
    # Lazy import to avoid circular: adapters depend on core, not the reverse.
    from suzerain.adapters.skill.inspectors import find_skill_md

    if find_skill_md(path) is not None:
        return "skill"
    for stack, markers in _STACK_MARKERS.items():
        if any((path / marker).is_file() for marker in markers):
            return stack
    return None


@dataclass(frozen=True)
class Repo:
    """A repository with its detected stack."""

    path: Path
    stack: str  # "skill" | "python" | "node" | "rust" | "auto"

    @classmethod
    def from_path(cls, path: Path) -> Repo:
        detected = detect_stack(path)
        return cls(path=path, stack=detected or "auto")
