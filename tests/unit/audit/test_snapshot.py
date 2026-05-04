"""Unit tests for suzerain.audit.snapshot."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import pytest

from suzerain.audit.snapshot import (
    DEFAULT_SNAPSHOT_DIRNAME,
    default_snapshot_dir,
    find_latest_snapshot,
    load_snapshot,
    save_snapshot,
    snapshot_filename,
)
from suzerain.commands.report import PortfolioReport

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_minimal_scan(root: Path) -> PortfolioReport:
    """Return a PortfolioReport with no repos for snapshot tests."""
    return PortfolioReport(root=root, reports=[], timestamp=datetime(2026, 5, 3, 14, 22, 0))


# ---------------------------------------------------------------------------
# default_snapshot_dir
# ---------------------------------------------------------------------------


def test_default_snapshot_dir_uses_suzerain_snapshots(tmp_path: Path) -> None:
    result = default_snapshot_dir(tmp_path)
    assert result == tmp_path / DEFAULT_SNAPSHOT_DIRNAME


def test_default_snapshot_dir_does_not_create_directory(tmp_path: Path) -> None:
    result = default_snapshot_dir(tmp_path)
    assert not result.exists()


# ---------------------------------------------------------------------------
# snapshot_filename
# ---------------------------------------------------------------------------


def test_snapshot_filename_format(tmp_path: Path) -> None:
    root = tmp_path / "MyPortfolio"
    ts = datetime(2026, 5, 3, 14, 22, 0)
    fname = snapshot_filename(root, ts)
    assert fname == "MyPortfolio-2026-05-03T142200.json"


def test_snapshot_filename_no_colons(tmp_path: Path) -> None:
    root = tmp_path / "Work"
    ts = datetime(2026, 4, 15, 9, 0, 0)
    fname = snapshot_filename(root, ts)
    assert ":" not in fname
    assert fname == "Work-2026-04-15T090000.json"


def test_snapshot_filename_uses_root_basename(tmp_path: Path) -> None:
    root = tmp_path / "deep" / "nested" / "portfolio"
    ts = datetime(2026, 1, 1, 0, 0, 0)
    fname = snapshot_filename(root, ts)
    assert fname.startswith("portfolio-")


# ---------------------------------------------------------------------------
# save_snapshot
# ---------------------------------------------------------------------------


def test_save_snapshot_creates_directory_if_missing(tmp_path: Path) -> None:
    snap_dir = tmp_path / "nonexistent" / "snapshots"
    scan = _make_minimal_scan(tmp_path / "myroot")
    saved_path = save_snapshot(scan, snap_dir)
    assert snap_dir.is_dir()
    assert saved_path.exists()


def test_save_snapshot_returns_path_under_snapshot_dir(tmp_path: Path) -> None:
    snap_dir = tmp_path / "snapshots"
    scan = _make_minimal_scan(tmp_path / "myroot")
    saved_path = save_snapshot(scan, snap_dir)
    assert saved_path.parent == snap_dir


def test_save_snapshot_content_is_valid_json(tmp_path: Path) -> None:
    snap_dir = tmp_path / "snapshots"
    root = tmp_path / "myroot"
    scan = _make_minimal_scan(root)
    saved_path = save_snapshot(scan, snap_dir)
    content = saved_path.read_text()
    parsed = json.loads(content)
    assert parsed["schema_version"] == "1"
    assert "timestamp" in parsed
    assert "repos" in parsed


def test_save_snapshot_filename_matches_convention(tmp_path: Path) -> None:
    snap_dir = tmp_path / "snapshots"
    root = tmp_path / "myroot"
    ts = datetime(2026, 5, 3, 14, 22, 0)
    scan = PortfolioReport(root=root, reports=[], timestamp=ts)
    saved_path = save_snapshot(scan, snap_dir)
    assert saved_path.name == "myroot-2026-05-03T142200.json"


def test_save_snapshot_is_idempotent_for_different_timestamps(tmp_path: Path) -> None:
    snap_dir = tmp_path / "snapshots"
    root = tmp_path / "myroot"
    ts1 = datetime(2026, 5, 3, 14, 22, 0)
    ts2 = datetime(2026, 5, 3, 15, 0, 0)
    scan1 = PortfolioReport(root=root, reports=[], timestamp=ts1)
    scan2 = PortfolioReport(root=root, reports=[], timestamp=ts2)
    path1 = save_snapshot(scan1, snap_dir)
    path2 = save_snapshot(scan2, snap_dir)
    assert path1 != path2
    assert path1.exists()
    assert path2.exists()


# ---------------------------------------------------------------------------
# load_snapshot
# ---------------------------------------------------------------------------


def test_load_snapshot_returns_dict(tmp_path: Path) -> None:
    snap_dir = tmp_path / "snapshots"
    scan = _make_minimal_scan(tmp_path / "myroot")
    saved_path = save_snapshot(scan, snap_dir)
    result = load_snapshot(saved_path)
    assert isinstance(result, dict)
    assert result["schema_version"] == "1"


def test_load_snapshot_roundtrip_preserves_timestamp(tmp_path: Path) -> None:
    snap_dir = tmp_path / "snapshots"
    root = tmp_path / "myroot"
    ts = datetime(2026, 5, 3, 14, 22, 0)
    scan = PortfolioReport(root=root, reports=[], timestamp=ts)
    saved_path = save_snapshot(scan, snap_dir)
    loaded = load_snapshot(saved_path)
    assert loaded["timestamp"] == "2026-05-03T14:22:00"


def test_load_snapshot_raises_on_invalid_json(tmp_path: Path) -> None:
    bad_file = tmp_path / "bad.json"
    bad_file.write_text("not valid json {{{")
    with pytest.raises(json.JSONDecodeError):
        load_snapshot(bad_file)


# ---------------------------------------------------------------------------
# find_latest_snapshot
# ---------------------------------------------------------------------------


def test_find_latest_snapshot_returns_none_when_dir_missing(tmp_path: Path) -> None:
    snap_dir = tmp_path / "nonexistent"
    root = tmp_path / "myroot"
    result = find_latest_snapshot(snap_dir, root)
    assert result is None


def test_find_latest_snapshot_returns_none_when_no_matches(tmp_path: Path) -> None:
    snap_dir = tmp_path / "snapshots"
    snap_dir.mkdir()
    # Write a file for a different root
    (snap_dir / "otherroot-2026-05-03T140000.json").write_text("{}")
    root = tmp_path / "myroot"
    result = find_latest_snapshot(snap_dir, root)
    assert result is None


def test_find_latest_snapshot_returns_alphabetically_last(tmp_path: Path) -> None:
    snap_dir = tmp_path / "snapshots"
    snap_dir.mkdir()
    root = tmp_path / "myroot"
    files = [
        "myroot-2026-04-15T090000.json",
        "myroot-2026-05-01T120000.json",
        "myroot-2026-05-03T142200.json",
    ]
    for f in files:
        (snap_dir / f).write_text("{}")
    result = find_latest_snapshot(snap_dir, root)
    assert result is not None
    assert result.name == "myroot-2026-05-03T142200.json"


def test_find_latest_snapshot_single_file(tmp_path: Path) -> None:
    snap_dir = tmp_path / "snapshots"
    snap_dir.mkdir()
    root = tmp_path / "myroot"
    fname = "myroot-2026-04-01T080000.json"
    (snap_dir / fname).write_text("{}")
    result = find_latest_snapshot(snap_dir, root)
    assert result is not None
    assert result.name == fname


def test_find_latest_snapshot_ignores_subdirectories(tmp_path: Path) -> None:
    snap_dir = tmp_path / "snapshots"
    snap_dir.mkdir()
    root = tmp_path / "myroot"
    # Create a directory that matches the glob but is not a file
    fake_dir = snap_dir / "myroot-2026-05-03T999999.json"
    fake_dir.mkdir()
    (snap_dir / "myroot-2026-04-01T080000.json").write_text("{}")
    result = find_latest_snapshot(snap_dir, root)
    assert result is not None
    assert result.name == "myroot-2026-04-01T080000.json"


def test_find_latest_snapshot_uses_root_name_as_prefix(tmp_path: Path) -> None:
    """Ensure prefix matching uses root.name, not full path."""
    snap_dir = tmp_path / "snapshots"
    snap_dir.mkdir()
    # root basename is 'portfolio'
    root = tmp_path / "some" / "deep" / "portfolio"
    (snap_dir / "portfolio-2026-05-03T140000.json").write_text("{}")
    result = find_latest_snapshot(snap_dir, root)
    assert result is not None
    assert result.name == "portfolio-2026-05-03T140000.json"


# ---------------------------------------------------------------------------
# load_snapshot_as_portfolio_report
# ---------------------------------------------------------------------------


def test_load_snapshot_as_portfolio_report_reconstructs_scan(tmp_path: Path) -> None:
    """load_snapshot_as_portfolio_report rebuilds a PortfolioReport from JSON."""
    from suzerain.audit.snapshot import load_snapshot_as_portfolio_report
    from suzerain.core.report import Report

    snapshot = {
        "schema_version": "1",
        "root": str(tmp_path),
        "timestamp": "2026-05-04T120000",
        "scan_count": 2,
        "repos": [
            {
                "path": "repo_a",
                "stack": "python",
                "score": 75,
                "status": "ok",
                "failing_rule_ids": ["DG002", "RL001"],
                "failing_by_severity": {"required": 1, "recommended": 1, "optional": 0},
                "fixable_count": 1,
            },
            {
                "path": "repo_b",
                "stack": None,
                "score": None,
                "status": "error",
                "failing_rule_ids": [],
                "failing_by_severity": {"required": 0, "recommended": 0, "optional": 0},
                "fixable_count": 0,
                "error": "RuntimeError: boom",
            },
        ],
    }
    snap_path = tmp_path / "snap.json"
    snap_path.write_text(json.dumps(snapshot))

    portfolio = load_snapshot_as_portfolio_report(snap_path)

    assert isinstance(portfolio, PortfolioReport)
    assert portfolio.root == tmp_path
    assert portfolio.timestamp.year == 2026 and portfolio.timestamp.month == 5
    assert len(portfolio.reports) == 2

    # repo_a → reconstructed Report with two failing findings
    path_a, result_a = portfolio.reports[0]
    assert path_a == tmp_path / "repo_a"
    assert isinstance(result_a, Report)
    assert result_a.stack == "python"
    failing = [f for f in result_a.findings if f.status == "fail"]
    assert sorted(f.rule_id for f in failing) == ["DG002", "RL001"]

    # repo_b → reconstructed as exception
    path_b, result_b = portfolio.reports[1]
    assert path_b == tmp_path / "repo_b"
    assert isinstance(result_b, Exception)
    assert "boom" in str(result_b)


def test_load_snapshot_as_portfolio_report_rejects_unknown_schema(tmp_path: Path) -> None:
    """Unknown schema_version raises ValueError."""
    from suzerain.audit.snapshot import load_snapshot_as_portfolio_report

    snapshot = {
        "schema_version": "99",
        "root": str(tmp_path),
        "timestamp": "2026-05-04T120000",
        "scan_count": 0,
        "repos": [],
    }
    snap_path = tmp_path / "snap.json"
    snap_path.write_text(json.dumps(snapshot))

    with pytest.raises(ValueError, match="schema_version"):
        load_snapshot_as_portfolio_report(snap_path)


def test_load_snapshot_preserves_original_score(tmp_path: Path) -> None:
    """Reconstructed Report.score returns the snapshot's stored score, not a recomputed one."""
    from suzerain.audit.snapshot import load_snapshot_as_portfolio_report
    from suzerain.core.report import Report

    snapshot = {
        "schema_version": "1",
        "root": str(tmp_path),
        "timestamp": "2026-05-04T120000",
        "scan_count": 1,
        "repos": [
            {
                "path": "repo_a",
                "stack": "python",
                "score": 75,
                "status": "ok",
                "failing_rule_ids": ["DG002", "RL001"],
                "failing_by_severity": {"required": 1, "recommended": 1, "optional": 0},
                "fixable_count": 0,
            },
        ],
    }
    snap_path = tmp_path / "snap.json"
    snap_path.write_text(json.dumps(snapshot))

    portfolio = load_snapshot_as_portfolio_report(snap_path)
    _, result = portfolio.reports[0]
    assert isinstance(result, Report)
    # Without the override, score would be 0 (all synthesized findings are failing).
    # With the override, it returns the stored score.
    assert result.score == 75
