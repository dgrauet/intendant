"""Shared pytest fixtures."""

from pathlib import Path

import pytest


@pytest.fixture()
def fixtures_dir() -> Path:
    """Return the absolute path to ``tests/fixtures``."""
    return Path(__file__).parent / "fixtures"
