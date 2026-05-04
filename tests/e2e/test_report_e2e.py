"""End-to-end test for `suzerain report` against the portfolio_mini fixture."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path


def _git_init(repo: Path) -> None:
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.email", "t@t.t"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.name", "T"], cwd=repo, check=True)
    subprocess.run(["git", "add", "-A"], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "feat: initial scaffold"], cwd=repo, check=True)


def test_report_e2e_json_against_portfolio_mini(tmp_path: Path, fixtures_dir: Path) -> None:
    portfolio = tmp_path / "portfolio_mini"
    shutil.copytree(fixtures_dir / "portfolio_mini", portfolio)
    # Each governed repo needs git init for RL002 to pass and audit to run.
    for repo_name in ("repo_a_clean", "repo_b_partial"):
        _git_init(portfolio / repo_name)
    suzerain_repo = Path(__file__).resolve().parents[2]
    proc = subprocess.run(
        ["uv", "run", "suzerain", "report", str(portfolio), "--format", "json"],
        cwd=suzerain_repo,
        capture_output=True,
        text=True,
    )
    assert proc.returncode in (0, 1), proc.stderr
    parsed = json.loads(proc.stdout)
    assert parsed["schema_version"] == "2"
    assert parsed["scan_count"] == 2
    assert {r["path"] for r in parsed["repos"]} == {"repo_a_clean", "repo_b_partial"}
    repo_b = next(r for r in parsed["repos"] if r["path"] == "repo_b_partial")
    assert repo_b["status"] == "ok"
    assert repo_b["score"] is not None
    assert len(repo_b["failing_rule_ids"]) >= 1
    repo_a = next(r for r in parsed["repos"] if r["path"] == "repo_a_clean")
    assert repo_a["status"] == "ok"
    for repo in parsed["repos"]:
        assert "failing_by_severity" in repo
        assert set(repo["failing_by_severity"].keys()) == {"required", "recommended", "optional"}


def test_report_e2e_save_snapshot_and_diff(tmp_path: Path, fixtures_dir: Path) -> None:
    """Save a snapshot, then run --diff to compare current scan against it."""
    portfolio = tmp_path / "portfolio_mini"
    shutil.copytree(fixtures_dir / "portfolio_mini", portfolio)
    for repo_name in ("repo_a_clean", "repo_b_partial"):
        _git_init(portfolio / repo_name)
    suzerain_repo = Path(__file__).resolve().parents[2]

    # 1. First run: save snapshot
    proc1 = subprocess.run(
        ["uv", "run", "suzerain", "report", str(portfolio), "--save-snapshot", "--format=json"],
        cwd=suzerain_repo,
        capture_output=True,
        text=True,
    )
    assert proc1.returncode in (0, 1), proc1.stderr
    snap_dir = portfolio / ".suzerain" / "snapshots"
    assert snap_dir.is_dir(), "Snapshot directory was not created"
    snaps = list(snap_dir.glob("portfolio_mini-*.json"))
    assert len(snaps) == 1, f"Expected 1 snapshot file, found: {snaps}"
    saved_snap = snaps[0]
    assert "Snapshot saved:" in proc1.stderr

    # 2. Second run: diff against saved snapshot → no new failures (same codebase)
    proc2 = subprocess.run(
        [
            "uv",
            "run",
            "suzerain",
            "report",
            str(portfolio),
            "--diff",
            f"--against={saved_snap}",
        ],
        cwd=suzerain_repo,
        capture_output=True,
        text=True,
    )
    assert proc2.returncode in (0, 1), proc2.stderr
    assert "PORTFOLIO DIFF" in proc2.stdout

    # 3. Second run with --format=json: diff JSON has correct structure
    proc3 = subprocess.run(
        [
            "uv",
            "run",
            "suzerain",
            "report",
            str(portfolio),
            "--diff",
            f"--against={saved_snap}",
            "--format=json",
        ],
        cwd=suzerain_repo,
        capture_output=True,
        text=True,
    )
    assert proc3.returncode in (0, 1), proc3.stderr
    parsed = json.loads(proc3.stdout)
    assert parsed["schema_version"] == "2"
    assert "score_changes" in parsed
    assert "new_failures" in parsed
    assert "resolved_failures" in parsed
    assert "new_repos" in parsed
    assert "removed_repos" in parsed
    # Same codebase compared to itself → no new repos, no removed repos
    assert parsed["new_repos"] == []
    assert parsed["removed_repos"] == []


def test_report_e2e_human_against_portfolio_mini(tmp_path: Path, fixtures_dir: Path) -> None:
    portfolio = tmp_path / "portfolio_mini"
    shutil.copytree(fixtures_dir / "portfolio_mini", portfolio)
    for repo_name in ("repo_a_clean", "repo_b_partial"):
        _git_init(portfolio / repo_name)
    suzerain_repo = Path(__file__).resolve().parents[2]
    proc = subprocess.run(
        ["uv", "run", "suzerain", "report", str(portfolio)],
        cwd=suzerain_repo,
        capture_output=True,
        text=True,
    )
    assert proc.returncode in (0, 1), proc.stderr
    assert "PORTFOLIO REPORT" in proc.stdout
    assert "repo_a_clean" in proc.stdout
    assert "repo_b_partial" in proc.stdout
    # repo_c_no_marker is NOT governed: must not appear in the table
    assert "repo_c_no_marker" not in proc.stdout
