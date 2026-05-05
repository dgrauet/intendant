"""E2E: intendant report --diff --format=html."""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest
from typer.testing import CliRunner

from intendant.cli import app

FIXTURE = Path(__file__).parent.parent / "fixtures" / "portfolio_mini"


@pytest.fixture
def fixture_copy(tmp_path: Path) -> Path:
    dst = tmp_path / "portfolio_mini"
    shutil.copytree(FIXTURE, dst)
    return dst


def test_report_diff_html_renders_diff_doc(fixture_copy: Path, tmp_path: Path) -> None:
    """Two snapshots → --diff --format=html produces a diff HTML doc."""
    runner = CliRunner()
    # Save first snapshot
    result = runner.invoke(app, ["report", str(fixture_copy), "--save-snapshot"])
    assert result.exit_code in (0, 1)

    # Render diff to HTML
    out = tmp_path / "diff.html"
    result = runner.invoke(
        app,
        ["report", str(fixture_copy), "--diff", "--format=html", "--output", str(out)],
    )
    assert result.exit_code in (0, 1)
    assert out.exists()
    content = out.read_text()
    assert "Portfolio report — diff" in content
    # All five sections header text appears
    for h in ("Score changes", "New failures", "Resolved failures", "New repos", "Removed repos"):
        assert h in content
    # Banner present
    assert "banner-ok" in content or "banner-regression" in content
