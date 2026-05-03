"""Unit tests for the dashboard command (dataclass + scan helpers)."""

from __future__ import annotations

import json as _json
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

from typer.testing import CliRunner

from suzerain.cli import app
from suzerain.commands.dashboard import DashboardScan, _scan_all, _scan_one
from suzerain.core.report import Report

cli_runner = CliRunner()


def _make_marker(parent: Path, body: str = "") -> None:
    parent.mkdir(parents=True, exist_ok=True)
    default = '[suzerain]\nversion = "1"\nstack = "auto"\nmode = "advisory"\n'
    (parent / ".suzerain.toml").write_text(body or default)


def test_dashboard_scan_dataclass_is_frozen(tmp_path: Path) -> None:
    scan = DashboardScan(root=tmp_path, reports=[], timestamp=datetime.now())
    try:
        scan.root = tmp_path / "other"  # ty: ignore[invalid-assignment]
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


def _seed_governed(target: Path) -> None:
    target.mkdir(parents=True, exist_ok=True)
    (target / ".suzerain.toml").write_text(
        '[suzerain]\nversion = "1"\nstack = "auto"\nmode = "advisory"\n'
    )


def test_cli_exit_2_when_path_does_not_exist(tmp_path: Path) -> None:
    result = cli_runner.invoke(app, ["dashboard", str(tmp_path / "nope")])
    assert result.exit_code == 2


def test_cli_exit_2_when_no_governed_repos(tmp_path: Path) -> None:
    (tmp_path / "ungoverned").mkdir()
    result = cli_runner.invoke(app, ["dashboard", str(tmp_path)])
    assert result.exit_code == 2


def test_cli_exit_0_when_all_clean(tmp_path: Path, fixtures_dir: Path) -> None:
    portfolio = tmp_path / "portfolio"
    portfolio.mkdir()
    target = portfolio / "conformant"
    shutil.copytree(fixtures_dir / "conformant_python_repo", target)
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=target, check=True)
    subprocess.run(["git", "config", "user.email", "t@t.t"], cwd=target, check=True)
    subprocess.run(["git", "config", "user.name", "T"], cwd=target, check=True)
    subprocess.run(["git", "add", "-A"], cwd=target, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "feat: initial scaffold"], cwd=target, check=True)
    result = cli_runner.invoke(app, ["dashboard", str(portfolio)])
    assert result.exit_code == 0, result.stdout


def test_cli_exit_1_when_required_fail(tmp_path: Path, fixtures_dir: Path) -> None:
    portfolio = tmp_path / "portfolio"
    portfolio.mkdir()
    target = portfolio / "nonconformant"
    shutil.copytree(fixtures_dir / "nonconformant_python_repo", target)
    result = cli_runner.invoke(app, ["dashboard", str(portfolio)])
    assert result.exit_code == 1, result.stdout


def test_cli_json_format_emits_valid_json(tmp_path: Path) -> None:
    _seed_governed(tmp_path / "alpha")
    result = cli_runner.invoke(app, ["dashboard", str(tmp_path), "--format", "json"])
    # Either exit 0 (clean) or exit 1 (required fails); both produce JSON.
    assert result.exit_code in (0, 1)
    parsed = _json.loads(result.stdout)
    assert parsed["schema_version"] == "1"
    assert parsed["scan_count"] == 1


# ---------------------------------------------------------------------------
# --save-snapshot tests
# ---------------------------------------------------------------------------


def test_cli_save_snapshot_writes_to_default_dir(tmp_path: Path) -> None:
    _seed_governed(tmp_path / "repo_a")
    result = cli_runner.invoke(app, ["dashboard", str(tmp_path), "--save-snapshot"])
    assert result.exit_code in (0, 1), result.output
    # Default dir: <root>/.suzerain/snapshots/
    snap_dir = tmp_path / ".suzerain" / "snapshots"
    assert snap_dir.is_dir(), f"Snapshot dir not created: {snap_dir}"
    snaps = list(snap_dir.glob(f"{tmp_path.name}-*.json"))
    assert len(snaps) == 1, f"Expected 1 snapshot, found: {snaps}"
    # Snapshot must be valid JSON
    parsed = _json.loads(snaps[0].read_text())
    assert parsed["schema_version"] == "1"


def test_cli_save_snapshot_with_custom_dir(tmp_path: Path) -> None:
    _seed_governed(tmp_path / "repo_a")
    custom_dir = tmp_path / "my_snaps"
    result = cli_runner.invoke(
        app,
        ["dashboard", str(tmp_path), "--save-snapshot", f"--snapshot-dir={custom_dir}"],
    )
    assert result.exit_code in (0, 1), result.output
    assert custom_dir.is_dir()
    snaps = list(custom_dir.glob("*.json"))
    assert len(snaps) == 1


def test_cli_save_snapshot_message_on_stderr(tmp_path: Path) -> None:
    _seed_governed(tmp_path / "repo_a")
    result = cli_runner.invoke(app, ["dashboard", str(tmp_path), "--save-snapshot"])
    assert result.exit_code in (0, 1)
    # typer.echo(..., err=True) goes to stdout in the CliRunner (mixed) by default
    assert "Snapshot saved:" in result.output


# ---------------------------------------------------------------------------
# --diff tests
# ---------------------------------------------------------------------------


def _make_snapshot_file(snap_dir: Path, root: Path, content: dict) -> Path:
    """Write a hand-crafted snapshot file for testing --diff."""
    import json

    snap_dir.mkdir(parents=True, exist_ok=True)
    fname = f"{root.name}-2026-01-01T000000.json"
    p = snap_dir / fname
    p.write_text(json.dumps(content))
    return p


def test_cli_diff_fails_when_no_previous_snapshot(tmp_path: Path) -> None:
    _seed_governed(tmp_path / "repo_a")
    result = cli_runner.invoke(app, ["dashboard", str(tmp_path), "--diff"])
    assert result.exit_code == 2


def test_cli_diff_against_specific_snapshot(tmp_path: Path) -> None:
    _seed_governed(tmp_path / "repo_a")
    # Create a snapshot that looks identical to what the current scan will produce
    snap_dir = tmp_path / "snaps"
    prev_content = {
        "schema_version": "1",
        "root": str(tmp_path),
        "timestamp": "2026-01-01T00:00:00",
        "scan_count": 1,
        "repos": [
            {
                "path": "repo_a",
                "stack": "auto",
                "score": 100,
                "status": "ok",
                "failing_rule_ids": [],
                "failing_by_severity": {"required": 0, "recommended": 0, "optional": 0},
                "fixable_count": 0,
            }
        ],
        "rules_in_scan": [],
    }
    snap_file = _make_snapshot_file(snap_dir, tmp_path, prev_content)
    result = cli_runner.invoke(
        app,
        ["dashboard", str(tmp_path), "--diff", f"--against={snap_file}"],
    )
    # Diff renders without crashing; exit code 0 or 1 depending on failures
    assert result.exit_code in (0, 1), result.output
    assert "PORTFOLIO DIFF" in result.output


def test_cli_diff_exit_1_on_new_required_failure(tmp_path: Path, fixtures_dir: Path) -> None:
    """Diff against a clean previous snapshot, current has required failure → exit 1."""
    portfolio = tmp_path / "portfolio"
    portfolio.mkdir()
    target = portfolio / "nonconformant"
    shutil.copytree(fixtures_dir / "nonconformant_python_repo", target)
    snap_dir = tmp_path / "snaps"
    # Previous snapshot: repo was passing all required rules
    prev_content = {
        "schema_version": "1",
        "root": str(portfolio),
        "timestamp": "2026-01-01T00:00:00",
        "scan_count": 1,
        "repos": [
            {
                "path": "nonconformant",
                "stack": "python",
                "score": 100,
                "status": "ok",
                "failing_rule_ids": [],
                "failing_by_severity": {"required": 0, "recommended": 0, "optional": 0},
                "fixable_count": 0,
            }
        ],
        "rules_in_scan": [],
    }
    snap_file = _make_snapshot_file(snap_dir, portfolio, prev_content)
    result = cli_runner.invoke(
        app,
        ["dashboard", str(portfolio), "--diff", f"--against={snap_file}"],
    )
    # New required failures → exit code 1
    assert result.exit_code == 1, result.output


def test_cli_diff_exit_0_when_no_new_required_failure(tmp_path: Path) -> None:
    """Diff with no regressions → exit 0.

    Strategy: save a snapshot of the current state first, then diff against it.
    Since the codebase hasn't changed between the two runs, there are zero new
    failures, so the exit code must be 0 regardless of how many failures exist.
    """
    _seed_governed(tmp_path / "repo_a")
    snap_dir = tmp_path / "snaps"
    # Run once to capture the actual current state as a snapshot
    save_result = cli_runner.invoke(
        app,
        ["dashboard", str(tmp_path), "--save-snapshot", f"--snapshot-dir={snap_dir}"],
    )
    assert save_result.exit_code in (0, 1), save_result.output
    snaps = list(snap_dir.glob("*.json"))
    assert len(snaps) == 1
    snap_file = snaps[0]
    # Now diff against that snapshot — same codebase → no new required failures → exit 0
    result = cli_runner.invoke(
        app,
        ["dashboard", str(tmp_path), "--diff", f"--against={snap_file}"],
    )
    assert result.exit_code == 0, result.output


def test_cli_save_and_diff_combined_handles_first_run_gracefully(tmp_path: Path) -> None:
    """--save-snapshot --diff with no previous snapshot → warning + exit 0."""
    _seed_governed(tmp_path / "repo_a")
    result = cli_runner.invoke(
        app,
        ["dashboard", str(tmp_path), "--save-snapshot", "--diff"],
    )
    # First run: no previous snapshot → save + exit 0
    assert result.exit_code == 0, result.output
    # Warning message present in output (CliRunner mixes stderr into stdout by default)
    assert "first snapshot" in result.output.lower() or "no previous" in result.output.lower()
    # Snapshot was still saved
    snap_dir = tmp_path / ".suzerain" / "snapshots"
    snaps = list(snap_dir.glob("*.json"))
    assert len(snaps) == 1


def test_cli_diff_json_format_emits_valid_json(tmp_path: Path) -> None:
    _seed_governed(tmp_path / "repo_a")
    snap_dir = tmp_path / "snaps"
    prev_content = {
        "schema_version": "1",
        "root": str(tmp_path),
        "timestamp": "2026-01-01T00:00:00",
        "scan_count": 1,
        "repos": [
            {
                "path": "repo_a",
                "stack": "auto",
                "score": 100,
                "status": "ok",
                "failing_rule_ids": [],
                "failing_by_severity": {"required": 0, "recommended": 0, "optional": 0},
                "fixable_count": 0,
            }
        ],
        "rules_in_scan": [],
    }
    snap_file = _make_snapshot_file(snap_dir, tmp_path, prev_content)
    result = cli_runner.invoke(
        app,
        [
            "dashboard",
            str(tmp_path),
            "--diff",
            f"--against={snap_file}",
            "--format=json",
        ],
    )
    assert result.exit_code in (0, 1), result.output
    parsed = _json.loads(result.stdout)
    assert parsed["schema_version"] == "1"
    assert "score_changes" in parsed
    assert "new_failures" in parsed
    assert "resolved_failures" in parsed
