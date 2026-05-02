"""`suzerain dashboard [PATH]` — aggregate audit across governed repos."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from suzerain.audit.discovery import find_suzerain_repos
from suzerain.audit.registry import collect_rules, filter_for_repo
from suzerain.audit.runner import run_audit
from suzerain.core.config import load_config
from suzerain.core.repo import Repo
from suzerain.core.report import Report


@dataclass(frozen=True)
class DashboardScan:
    """Result of a multi-repo dashboard scan."""

    root: Path
    reports: list[tuple[Path, Report | Exception]]
    timestamp: datetime


def _scan_one(repo_path: Path) -> tuple[Path, Report | Exception]:
    """Audit a single repo, capturing any exception as the result."""
    try:
        repo = Repo.from_path(repo_path)
        config = load_config(repo_path)
        rules = filter_for_repo(collect_rules(), repo, config)
        report = run_audit(repo, config, rules)
        return (repo_path, report)
    except Exception as exc:
        return (repo_path, exc)


def _scan_all(root: Path, maxdepth: int = 2) -> DashboardScan:
    """Discover all governed repos under ``root`` and audit each in turn."""
    repo_paths = find_suzerain_repos(root, maxdepth)
    results = [_scan_one(p) for p in repo_paths]
    return DashboardScan(root=root, reports=results, timestamp=datetime.now())
