"""E2E: intendant report --from-snapshot --format=html (no live scan)."""

from __future__ import annotations

import json
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


def test_render_from_snapshot_matches_snapshot_paths(fixture_copy: Path, tmp_path: Path) -> None:
    """--from-snapshot HTML contains the same repos+scores as the snapshot JSON."""
    runner = CliRunner()
    # 1. Save snapshot
    result = runner.invoke(app, ["report", str(fixture_copy), "--save-snapshot"])
    assert result.exit_code in (0, 1)

    snap_dir = fixture_copy / ".intendant" / "snapshots"
    snaps = sorted(snap_dir.glob("*.json"))
    assert snaps, "no snapshot file produced"
    snap_path = snaps[-1]
    snap = json.loads(snap_path.read_text())

    # 2. Render from snapshot (no live scan)
    out = tmp_path / "from-snap.html"
    result = runner.invoke(
        app,
        [
            "report",
            str(fixture_copy),
            "--format=html",
            "--output",
            str(out),
            "--from-snapshot",
            str(snap_path),
        ],
    )
    assert result.exit_code in (0, 1)
    assert out.exists()
    content = out.read_text()
    for repo in snap["repos"]:
        if repo["status"] == "ok":
            assert repo["path"] in content
            assert str(repo["score"]) in content
