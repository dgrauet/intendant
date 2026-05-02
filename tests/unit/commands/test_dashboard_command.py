"""Unit tests for the dashboard command (dataclass + scan helpers)."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from suzerain.commands.dashboard import DashboardScan, _scan_all, _scan_one
from suzerain.core.report import Report


def _make_marker(parent: Path, body: str = "") -> None:
    parent.mkdir(parents=True, exist_ok=True)
    default = '[suzerain]\nversion = "1"\nstack = "auto"\nmode = "advisory"\n'
    (parent / ".suzerain.toml").write_text(body or default)


def test_dashboard_scan_dataclass_is_frozen(tmp_path: Path) -> None:
    scan = DashboardScan(root=tmp_path, reports=[], timestamp=datetime.now())
    try:
        scan.root = tmp_path / "other"  # type: ignore[misc]
    except (AttributeError, TypeError):
        return
    raise AssertionError("DashboardScan must be frozen")


def test_scan_one_returns_report_for_valid_repo(tmp_path: Path) -> None:
    _make_marker(tmp_path)
    repo_path, result = _scan_one(tmp_path)
    assert repo_path == tmp_path
    assert isinstance(result, Report)


def test_scan_one_captures_exception_for_broken_toml(tmp_path: Path) -> None:
    _make_marker(tmp_path, body="this is not = valid TOML [")
    repo_path, result = _scan_one(tmp_path)
    assert repo_path == tmp_path
    assert isinstance(result, Exception)


def test_scan_all_finds_governed_repos(tmp_path: Path) -> None:
    _make_marker(tmp_path / "repo_a")
    _make_marker(tmp_path / "repo_b")
    (tmp_path / "ungoverned").mkdir()
    scan = _scan_all(tmp_path, maxdepth=2)
    assert scan.root == tmp_path
    assert len(scan.reports) == 2
    paths = sorted(p for p, _ in scan.reports)
    assert paths == [tmp_path / "repo_a", tmp_path / "repo_b"]


def test_scan_all_returns_empty_reports_when_no_governed_repos(tmp_path: Path) -> None:
    (tmp_path / "ungoverned").mkdir()
    scan = _scan_all(tmp_path, maxdepth=2)
    assert scan.reports == []


def test_scan_all_continues_after_per_repo_exception(tmp_path: Path) -> None:
    _make_marker(tmp_path / "repo_ok")
    _make_marker(tmp_path / "repo_broken", body="not = valid TOML [")
    scan = _scan_all(tmp_path, maxdepth=2)
    assert len(scan.reports) == 2
    statuses = {p.name: type(r).__name__ for p, r in scan.reports}
    assert statuses["repo_ok"] == "Report"
    assert statuses["repo_broken"] != "Report"
