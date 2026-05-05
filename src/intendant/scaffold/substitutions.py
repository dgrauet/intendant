"""Placeholder substitution helpers for the scaffolder."""

from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from datetime import date

# Matches {{ key }} or {{key}} or {{  key  }} — captures the bare key
_PLACEHOLDER_RE = re.compile(r"\{\{\s*([A-Za-z_]+)\s*\}\}")


def derive_package_name(project_name: str) -> str:
    """Convert a project name to a Python package identifier.

    Example: "my-cool-project" → "my_cool_project".
    """
    return re.sub(r"[^A-Za-z0-9_]", "_", project_name).lower()


def _detect_git_author() -> str:
    try:
        out = subprocess.run(
            ["git", "config", "--get", "user.name"],
            capture_output=True,
            text=True,
            timeout=2,
            check=False,
        )
        return out.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return ""


@dataclass(frozen=True)
class SubstitutionContext:
    """All values that can be substituted into a template."""

    project_name: str
    package_name: str
    description: str
    author: str
    year: str
    stack: str
    release_type: str

    @classmethod
    def from_minimal(
        cls,
        project_name: str,
        stack: str,
        description: str = "",
        author: str | None = None,
    ) -> SubstitutionContext:
        return cls(
            project_name=project_name,
            package_name=derive_package_name(project_name),
            description=description,
            author=author if author is not None else _detect_git_author(),
            year=str(date.today().year),
            stack=stack,
            release_type=stack,  # 1:1 for V1; could diverge later
        )


def resolve_placeholders(text: str, ctx: SubstitutionContext) -> str:
    """Replace `{{ key }}` tokens in `text` with values from `ctx`.

    Unknown keys are left as-is (forward compatibility).
    """
    table = {
        "project_name": ctx.project_name,
        "package_name": ctx.package_name,
        "description": ctx.description,
        "author": ctx.author,
        "year": ctx.year,
        "stack": ctx.stack,
        "release_type": ctx.release_type,
    }

    def _sub(match: re.Match[str]) -> str:
        key = match.group(1)
        return table.get(key, match.group(0))

    return _PLACEHOLDER_RE.sub(_sub, text)
