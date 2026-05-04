"""End-to-end test: suzerain audit on a multi_subproject fixture."""

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
    subprocess.run(["git", "commit", "-q", "-m", "feat: initial fixture"], cwd=repo, check=True)


def test_audit_e2e_multi_subproject_json(tmp_path: Path, fixtures_dir: Path) -> None:
    target = tmp_path / "multi_subproject_repo"
    shutil.copytree(fixtures_dir / "multi_subproject_repo", target)
    _git_init(target)
    suzerain_repo = Path(__file__).resolve().parents[2]
    proc = subprocess.run(
        ["uv", "run", "suzerain", "audit", str(target), "--format", "json"],
        cwd=suzerain_repo,
        capture_output=True,
        text=True,
    )
    assert proc.returncode in (0, 1), proc.stderr
    parsed = json.loads(proc.stdout)
    assert "subprojects" in parsed
    names = [g["name"] for g in parsed["subprojects"]]
    assert "_global_" in names
    assert "root" in names
    assert "backend" in names
    global_entry = next(g for g in parsed["subprojects"] if g["name"] == "_global_")
    assert any(f["rule_id"] == "DG001" for f in global_entry["findings"])


def test_audit_e2e_multi_subproject_human(tmp_path: Path, fixtures_dir: Path) -> None:
    target = tmp_path / "multi_subproject_repo"
    shutil.copytree(fixtures_dir / "multi_subproject_repo", target)
    _git_init(target)
    suzerain_repo = Path(__file__).resolve().parents[2]
    proc = subprocess.run(
        ["uv", "run", "suzerain", "audit", str(target)],
        cwd=suzerain_repo,
        capture_output=True,
        text=True,
    )
    assert proc.returncode in (0, 1), proc.stderr
    assert "ROOT" in proc.stdout
    assert "backend" in proc.stdout
