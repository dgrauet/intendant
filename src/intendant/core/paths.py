"""Resolve paths to intendant assets (handbook, ADRs, templates)."""

from __future__ import annotations

import os
from pathlib import Path

import intendant


def intendant_root() -> Path:
    """Return the path to the intendant repo root.

    Assumes editable install: ``src/intendant/__init__.py`` lives 3 levels
    deep from the repo root. For non-editable installs, set the
    ``INTENDANT_ROOT`` environment variable (palier 2 will introduce
    proper packaged-resource resolution).
    """
    env = os.environ.get("INTENDANT_ROOT")
    if env:
        return Path(env).resolve()
    return Path(intendant.__file__).resolve().parent.parent.parent


def docs_root() -> Path:
    return intendant_root() / "docs"


def handbook_root() -> Path:
    return docs_root() / "handbook"


def adr_root() -> Path:
    return docs_root() / "adr"


def templates_root() -> Path:
    return intendant_root() / "templates"
