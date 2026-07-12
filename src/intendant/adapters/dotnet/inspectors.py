"""Helpers shared by .NET rule check methods."""

from __future__ import annotations

import re
from pathlib import Path

_SKIP_PARTS = {"bin", "obj", "node_modules"}

_TARGET_FRAMEWORK_RE = re.compile(r"<TargetFrameworks?>\s*([^<]+?)\s*</TargetFrameworks?>")
_NULLABLE_RE = re.compile(r"<Nullable>\s*enable\s*</Nullable>", re.IGNORECASE)
_PACKAGE_REF_RE = re.compile(r"<PackageReference\s+[^>]*Include\s*=\s*\"([^\"]+)\"")


def find_csproj_files(repo_path: Path) -> list[Path]:
    """Return every ``*.csproj`` under the repo, skipping build output.

    Skips ``bin/``, ``obj/``, ``node_modules/``, and hidden directories —
    restored or generated project files there are not source of truth.
    """
    hits: list[Path] = []
    for csproj in sorted(repo_path.rglob("*.csproj")):
        rel_parts = csproj.relative_to(repo_path).parts[:-1]
        if any(p in _SKIP_PARTS or p.startswith(".") for p in rel_parts):
            continue
        hits.append(csproj)
    return hits


def target_frameworks(csproj: Path) -> list[str]:
    """Frameworks declared via ``<TargetFramework>`` or ``<TargetFrameworks>``."""
    try:
        text = csproj.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    match = _TARGET_FRAMEWORK_RE.search(text)
    if match is None:
        return []
    return [fw.strip() for fw in match.group(1).split(";") if fw.strip()]


def nullable_enabled(csproj: Path, repo_path: Path) -> bool:
    """True when the project (or a ``Directory.Build.props`` up to the root) enables Nullable."""
    candidates = [csproj]
    for parent in csproj.parents:
        candidates.append(parent / "Directory.Build.props")
        if parent == repo_path:
            break
    for candidate in candidates:
        if not candidate.is_file():
            continue
        try:
            text = candidate.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if _NULLABLE_RE.search(text):
            return True
    return False


def package_references(csproj: Path) -> list[str]:
    """NuGet package ids referenced via ``<PackageReference Include="…">``."""
    try:
        text = csproj.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    return _PACKAGE_REF_RE.findall(text)
