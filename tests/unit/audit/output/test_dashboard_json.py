"""Unit tests for the dashboard JSON formatter."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from suzerain.audit.output.dashboard_json import render_dashboard_json
from suzerain.commands.dashboard import DashboardScan
from suzerain.core.report import Finding, Report


def _make_clean_report(repo_path: Path) -> Report:
    return Report(
        repo_path=repo_path,
        stack="python",
        findings=[
            Finding(
                rule_id="DG001",
                severity="required",
                status="pass",
                evidence="",
                fix_available=False,
            ),
        ],
    )


def _make_failing_report(repo_path: Path) -> Report:
    return Report(
        repo_path=repo_path,
        stack="python",
        findings=[
            Finding(
                rule_id="DG001",
                severity="required",
                status="pass",
                evidence="",
                fix_available=False,
            ),
            Finding(
                rule_id="RL001",
                severity="required",
                status="fail",
                evidence="missing",
                fix_available=False,
            ),
            Finding(
                rule_id="SA001",
                severity="required",
                status="fail",
                evidence="missing",
                fix_available=True,
            ),
        ],
    )


def test_render_returns_valid_json_string(tmp_path: Path) -> None:
    scan = DashboardScan(root=tmp_path, reports=[], timestamp=datetime(2026, 5, 2, 15, 42))
    text = render_dashboard_json(scan)
    parsed = json.loads(text)
    assert parsed["schema_version"] == "1"


def test_root_is_absolute_string(tmp_path: Path) -> None:
    scan = DashboardScan(root=tmp_path, reports=[], timestamp=datetime(2026, 5, 2, 15, 42))
    parsed = json.loads(render_dashboard_json(scan))
    assert parsed["root"] == str(tmp_path)


def test_timestamp_is_iso8601(tmp_path: Path) -> None:
    scan = DashboardScan(root=tmp_path, reports=[], timestamp=datetime(2026, 5, 2, 15, 42, 0))
    parsed = json.loads(render_dashboard_json(scan))
    assert parsed["timestamp"].startswith("2026-05-02T15:42:00")


def test_scan_count_matches_reports_length(tmp_path: Path) -> None:
    repo_a = tmp_path / "alpha"
    scan = DashboardScan(
        root=tmp_path,
        reports=[(repo_a, _make_clean_report(repo_a))],
        timestamp=datetime(2026, 5, 2, 15, 42),
    )
    parsed = json.loads(render_dashboard_json(scan))
    assert parsed["scan_count"] == 1


def test_repo_path_is_relative_to_root(tmp_path: Path) -> None:
    repo_a = tmp_path / "alpha"
    scan = DashboardScan(
        root=tmp_path,
        reports=[(repo_a, _make_clean_report(repo_a))],
        timestamp=datetime(2026, 5, 2, 15, 42),
    )
    parsed = json.loads(render_dashboard_json(scan))
    assert parsed["repos"][0]["path"] == "alpha"


def test_clean_repo_has_status_ok_no_failing_ids(tmp_path: Path) -> None:
    repo_a = tmp_path / "alpha"
    scan = DashboardScan(
        root=tmp_path,
        reports=[(repo_a, _make_clean_report(repo_a))],
        timestamp=datetime(2026, 5, 2, 15, 42),
    )
    parsed = json.loads(render_dashboard_json(scan))
    repo_obj = parsed["repos"][0]
    assert repo_obj["status"] == "ok"
    assert repo_obj["score"] == 100
    assert repo_obj["failing_rule_ids"] == []
    assert repo_obj["failing_by_severity"] == {"required": 0, "recommended": 0, "optional": 0}
    assert repo_obj["fixable_count"] == 0
    assert "error" not in repo_obj


def test_failing_repo_lists_rule_ids_and_fixable_count(tmp_path: Path) -> None:
    repo_b = tmp_path / "bravo"
    scan = DashboardScan(
        root=tmp_path,
        reports=[(repo_b, _make_failing_report(repo_b))],
        timestamp=datetime(2026, 5, 2, 15, 42),
    )
    parsed = json.loads(render_dashboard_json(scan))
    repo_obj = parsed["repos"][0]
    assert repo_obj["status"] == "ok"
    assert sorted(repo_obj["failing_rule_ids"]) == ["RL001", "SA001"]
    assert repo_obj["failing_by_severity"] == {"required": 2, "recommended": 0, "optional": 0}
    assert repo_obj["fixable_count"] == 1


def test_error_repo_has_status_error_and_message(tmp_path: Path) -> None:
    repo_c = tmp_path / "charlie"
    err = ValueError("invalid TOML at line 3")
    scan = DashboardScan(
        root=tmp_path,
        reports=[(repo_c, err)],
        timestamp=datetime(2026, 5, 2, 15, 42),
    )
    parsed = json.loads(render_dashboard_json(scan))
    repo_obj = parsed["repos"][0]
    assert repo_obj["status"] == "error"
    assert repo_obj["score"] is None
    assert repo_obj["stack"] is None
    assert repo_obj["failing_by_severity"] == {"required": 0, "recommended": 0, "optional": 0}
    assert "ValueError" in repo_obj["error"]
    assert "invalid TOML" in repo_obj["error"]


def test_rules_in_scan_only_includes_failing_rules(tmp_path: Path) -> None:
    repo_b = tmp_path / "bravo"
    scan = DashboardScan(
        root=tmp_path,
        reports=[(repo_b, _make_failing_report(repo_b))],
        timestamp=datetime(2026, 5, 2, 15, 42),
    )
    parsed = json.loads(render_dashboard_json(scan))
    rule_ids = sorted(r["id"] for r in parsed["rules_in_scan"])
    # Only RL001 and SA001 fail; DG001 passes and must be absent
    assert rule_ids == ["RL001", "SA001"]
    sa001 = next(r for r in parsed["rules_in_scan"] if r["id"] == "SA001")
    assert sa001["fixable"] is True
    assert sa001["severity"] == "required"
    assert sa001["title"]  # non-empty
