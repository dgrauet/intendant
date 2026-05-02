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
