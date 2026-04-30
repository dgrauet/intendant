"""Resolve paths to suzerain assets (handbook, ADRs, templates)."""

from __future__ import annotations

import os
from pathlib import Path

import suzerain


def suzerain_root() -> Path:
    """Return the path to the suzerain repo root.

    Assumes editable install: ``src/suzerain/__init__.py`` lives 3 levels
    deep from the repo root. For non-editable installs, set the
    ``SUZERAIN_ROOT`` environment variable (palier 2 will introduce
    proper packaged-resource resolution).
    """
    env = os.environ.get("SUZERAIN_ROOT")
    if env:
        return Path(env).resolve()
    return Path(suzerain.__file__).resolve().parent.parent.parent


def docs_root() -> Path:
    return suzerain_root() / "docs"


def handbook_root() -> Path:
    return docs_root() / "handbook"


def adr_root() -> Path:
    return docs_root() / "adr"


def templates_root() -> Path:
    return suzerain_root() / "templates"
