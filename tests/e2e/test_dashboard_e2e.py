"""End-to-end test for `suzerain dashboard` against the portfolio_mini fixture."""

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


def test_dashboard_e2e_json_against_portfolio_mini(tmp_path: Path, fixtures_dir: Path) -> None:
    portfolio = tmp_path / "portfolio_mini"
    shutil.copytree(fixtures_dir / "portfolio_mini", portfolio)
    # Each governed repo needs git init for RL002 to pass and audit to run.
    for repo_name in ("repo_a_clean", "repo_b_partial"):
        _git_init(portfolio / repo_name)
    suzerain_repo = Path(__file__).resolve().parents[2]
    proc = subprocess.run(
        ["uv", "run", "suzerain", "dashboard", str(portfolio), "--format", "json"],
        cwd=suzerain_repo,
        capture_output=True,
        text=True,
    )
    assert proc.returncode in (0, 1), proc.stderr
    parsed = json.loads(proc.stdout)
    assert parsed["schema_version"] == "1"
    assert parsed["scan_count"] == 2
    assert {r["path"] for r in parsed["repos"]} == {"repo_a_clean", "repo_b_partial"}
    repo_b = next(r for r in parsed["repos"] if r["path"] == "repo_b_partial")
    assert repo_b["status"] == "ok"
    assert repo_b["score"] is not None
    assert len(repo_b["failing_rule_ids"]) >= 1
    repo_a = next(r for r in parsed["repos"] if r["path"] == "repo_a_clean")
    assert repo_a["status"] == "ok"


def test_dashboard_e2e_human_against_portfolio_mini(tmp_path: Path, fixtures_dir: Path) -> None:
    portfolio = tmp_path / "portfolio_mini"
    shutil.copytree(fixtures_dir / "portfolio_mini", portfolio)
    for repo_name in ("repo_a_clean", "repo_b_partial"):
        _git_init(portfolio / repo_name)
    suzerain_repo = Path(__file__).resolve().parents[2]
    proc = subprocess.run(
        ["uv", "run", "suzerain", "dashboard", str(portfolio)],
        cwd=suzerain_repo,
        capture_output=True,
        text=True,
    )
    assert proc.returncode in (0, 1), proc.stderr
    assert "PORTFOLIO DASHBOARD" in proc.stdout
    assert "repo_a_clean" in proc.stdout
    assert "repo_b_partial" in proc.stdout
    # repo_c_no_marker is NOT governed: must not appear in the table
    assert "repo_c_no_marker" not in proc.stdout
