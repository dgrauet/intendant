"""Helpers shared by Go rule check methods."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

_MODULE_RE = re.compile(r"^module\s+(\S+)\s*$", re.MULTILINE)
_GO_DIRECTIVE_RE = re.compile(r"^go\s+(\d+\.\d+(?:\.\d+)?)\s*$", re.MULTILINE)
_TEST_FUNC_RE = re.compile(r"^func\s+Test[A-Z_]\w*\s*\(", re.MULTILINE)


@dataclass(frozen=True)
class GoMod:
    module: str | None
    go_version: str | None


def has_go_mod(repo_path: Path) -> bool:
    return (repo_path / "go.mod").is_file()


def load_go_mod(repo_path: Path) -> GoMod | None:
    """Parse go.mod for the `module` and `go` directives. None if missing/unreadable."""
    path = repo_path / "go.mod"
    if not path.is_file():
        return None
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return None
    module_match = _MODULE_RE.search(text)
    go_match = _GO_DIRECTIVE_RE.search(text)
    return GoMod(
        module=module_match.group(1) if module_match else None,
        go_version=go_match.group(1) if go_match else None,
    )


def find_test_files(repo_path: Path) -> list[Path]:
    """Return *_test.go files containing a `func Test*(` declaration.

    Walks the repo, skipping `vendor/`, `node_modules/`, `.git/`, and any
    hidden directories at the top level.
    """
    hits: list[Path] = []
    skip_dirs = {"vendor", "node_modules", ".git", "target", "dist"}
    for test_file in repo_path.rglob("*_test.go"):
        rel_parts = test_file.relative_to(repo_path).parts[:-1]
        if any(p in skip_dirs or p.startswith(".") for p in rel_parts):
            continue
        try:
            if _TEST_FUNC_RE.search(test_file.read_text(errors="replace")):
                hits.append(test_file)
        except OSError:
            continue
    return hits
