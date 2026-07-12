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
    "dotnet": ("*.csproj", "*.sln"),
}


def _marker_present(path: Path, marker: str) -> bool:
    """A marker is either an exact filename or a glob pattern (contains `*`)."""
    if "*" in marker:
        return any(p.is_file() for p in path.glob(marker))
    return (path / marker).is_file()


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
    from intendant.adapters.claude_skill.inspectors import find_skill_md

    found: list[str] = []
    if find_skill_md(path) is not None:
        found.append("claude-skill")
    for stack, markers in _STACK_MARKERS.items():
        if any(_marker_present(path, marker) for marker in markers):
            found.append(stack)
    return tuple(found)


# Directories never scanned for nested stack roots: build output, vendored
# dependencies, virtualenvs — their manifests are not project roots.
_NESTED_SCAN_SKIP = {
    "node_modules",
    "target",
    "dist",
    "build",
    ".build",
    "bin",
    "obj",
    "vendor",
    "__pycache__",
    ".venv",
    "venv",
    "Pods",
}


def find_nested_stack_roots(path: Path, max_depth: int = 5) -> tuple[tuple[str, str], ...]:
    """Return every nested directory holding a stack marker, with its stack.

    Walks subdirectories of ``path`` down to ``max_depth`` levels (the root
    itself is excluded — root stacks are handled by ``detect_stacks``),
    skipping hidden directories and ``_NESTED_SCAN_SKIP``. Result is a
    sorted tuple of ``(posix-relative-dir, stack)`` pairs.
    """
    found: list[tuple[str, str]] = []

    def walk(directory: Path, depth: int) -> None:
        for entry in sorted(directory.iterdir()):
            if not entry.is_dir():
                continue
            if entry.name.startswith(".") or entry.name in _NESTED_SCAN_SKIP:
                continue
            for stack, markers in _STACK_MARKERS.items():
                if any(_marker_present(entry, marker) for marker in markers):
                    found.append((entry.relative_to(path).as_posix(), stack))
            if depth < max_depth:
                walk(entry, depth + 1)

    walk(path, 1)
    return tuple(sorted(found))


@dataclass(frozen=True)
class Repo:
    """A repository with its stack composition.

    ``stacks`` lists every language/stack that applies to this repo. When
    the list is empty under ``mode="auto"``, no stack-specific adapter
    matched and only transverse rules will run.

    ``mode`` records *how* the composition was determined:
    - ``auto``  — derived from filesystem markers via ``detect_stacks``.
    - ``manual`` — pinned in ``.intendant.toml`` (top-level ``stack`` or via
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
