"""Tests for Subproject dataclass."""

from __future__ import annotations

from intendant.core.subproject import Subproject


def test_subproject_has_three_fields() -> None:
    sp = Subproject(name="backend", path="backend", stack="python")
    assert sp.name == "backend"
    assert sp.path == "backend"
    assert sp.stack == "python"


def test_subproject_is_frozen() -> None:
    sp = Subproject(name="backend", path="backend", stack="python")
    try:
        sp.name = "other"  # ty: ignore[invalid-assignment]
    except (AttributeError, TypeError):
        return
    raise AssertionError("Subproject must be frozen")
