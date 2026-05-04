"""Repository discovery for multi-repo report scans."""

from __future__ import annotations

from pathlib import Path


def find_suzerain_repos(root: Path, maxdepth: int = 2) -> list[Path]:
    """Find all directories under ``root`` containing a `.suzerain.toml` marker.

    Returns sorted list of repo root paths (alphabetical for determinism).
    Searches up to ``maxdepth`` levels under ``root`` (default 2 covers
    typical project layouts at depth 1, plus one level of grouping).
    Returns an empty list if ``root`` does not exist or is not a directory.
    """
    if not root.is_dir():
        return []
    candidates: set[Path] = set()
    for depth in range(1, maxdepth + 1):
        pattern = "*/" * depth + ".suzerain.toml"
        for marker in root.glob(pattern):
            candidates.add(marker.parent)
    return sorted(candidates)
