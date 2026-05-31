"""Resolve paths to intendant assets (handbook, ADRs, templates).

Assets live at the repo root (``docs/``, ``templates/``) for humans, but an
installed wheel bundles them inside the package at ``intendant/_assets/`` (see
the ``force-include`` mapping in ``pyproject.toml``). Resolution therefore
checks, in order: an explicit ``INTENDANT_ROOT`` override, the bundled
``_assets`` directory next to the package, then the editable source checkout.
"""

from __future__ import annotations

import os
from pathlib import Path

import intendant

# Directory bundled into the wheel alongside the package (via force-include).
_ASSETS_DIRNAME = "_assets"


def _bundled_assets(pkg_file: Path) -> Path:
    """The packaged assets directory next to ``intendant/__init__.py``."""
    return pkg_file.resolve().parent / _ASSETS_DIRNAME


def _checkout_root(pkg_file: Path) -> Path:
    """The repo root in an editable install: ``src/intendant/__init__.py`` → repo."""
    return pkg_file.resolve().parents[2]


def _resolve_docs_root(pkg_file: Path, env: str | None) -> Path:
    if env:
        return Path(env).resolve() / "docs"
    bundled = _bundled_assets(pkg_file)
    if (bundled / "handbook").is_dir():
        return bundled
    return _checkout_root(pkg_file) / "docs"


def _resolve_templates_root(pkg_file: Path, env: str | None) -> Path:
    if env:
        return Path(env).resolve() / "templates"
    bundled = _bundled_assets(pkg_file) / "templates"
    if bundled.is_dir():
        return bundled
    return _checkout_root(pkg_file) / "templates"


def _pkg_file() -> Path:
    return Path(intendant.__file__)


def intendant_root() -> Path:
    """Return the intendant repo root (editable) or ``INTENDANT_ROOT`` override.

    Prefer :func:`docs_root` / :func:`templates_root` for locating assets; this
    remains for callers that need the checkout root directly.
    """
    env = os.environ.get("INTENDANT_ROOT")
    if env:
        return Path(env).resolve()
    return _checkout_root(_pkg_file())


def docs_root() -> Path:
    return _resolve_docs_root(_pkg_file(), os.environ.get("INTENDANT_ROOT"))


def handbook_root() -> Path:
    return docs_root() / "handbook"


def adr_root() -> Path:
    return docs_root() / "adr"


def templates_root() -> Path:
    return _resolve_templates_root(_pkg_file(), os.environ.get("INTENDANT_ROOT"))
