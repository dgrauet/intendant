"""Unit tests for the report human (Rich) formatter."""

from __future__ import annotations

from datetime import datetime
from io import StringIO
from pathlib import Path

from rich.console import Console

from intendant.audit.output.report_human import render_report
from intendant.commands.report import PortfolioReport
from intendant.core.report import Finding, Report


def _capture(scan: PortfolioReport) -> str:
    out = StringIO()
    console = Console(file=out, width=120, no_color=True)
    render_report(scan, console=console)
    return out.getvalue()


def _make_clean_report(repo_path: Path) -> Report:
    return Report(
        repo_path=repo_path,
        stacks=("python",),
        mode="auto",
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


def _make_failing_report(repo_path: Path, stack: str = "python") -> Report:
    return Report(
        repo_path=repo_path,
        stacks=(stack,),
        mode="auto",
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
                evidence="CHANGELOG.md not found",
                fix_available=False,
            ),
            Finding(
                rule_id="SA001",
                severity="required",
                status="fail",
                evidence="no .pre-commit-config.yaml",
                fix_available=True,
            ),
        ],
    )


def test_renders_header_with_root_and_count(tmp_path: Path) -> None:
    scan = PortfolioReport(root=tmp_path, reports=[], timestamp=datetime(2026, 5, 2, 15, 42))
    out = _capture(scan)
    assert "PORTFOLIO REPORT" in out
    assert str(tmp_path) in out
    assert "Repos audited: 0" in out


def test_renders_clean_repo_as_all_clean(tmp_path: Path) -> None:
    repo_a = tmp_path / "alpha"
    scan = PortfolioReport(
        root=tmp_path,
        reports=[(repo_a, _make_clean_report(repo_a))],
        timestamp=datetime(2026, 5, 2, 15, 42),
    )
    out = _capture(scan)
    assert "alpha" in out
    assert "all clean" in out


def test_renders_failing_repo_with_rule_ids(tmp_path: Path) -> None:
    repo_b = tmp_path / "bravo"
    scan = PortfolioReport(
        root=tmp_path,
        reports=[(repo_b, _make_failing_report(repo_b))],
        timestamp=datetime(2026, 5, 2, 15, 42),
    )
    out = _capture(scan)
    assert "2 req" in out  # both failing findings are required severity
    assert "0 rec" in out  # none are recommended
    assert "1 fix" in out  # one is fixable
    assert "RL001" in out
    assert "SA001*" in out  # asterisk marks fixable


def test_omits_legend_when_no_failing_rules(tmp_path: Path) -> None:
    repo_a = tmp_path / "alpha"
    scan = PortfolioReport(
        root=tmp_path,
        reports=[(repo_a, _make_clean_report(repo_a))],
        timestamp=datetime(2026, 5, 2, 15, 42),
    )
    out = _capture(scan)
    assert "Failing rules in this scan" not in out


def test_renders_legend_when_at_least_one_failure(tmp_path: Path) -> None:
    repo_b = tmp_path / "bravo"
    scan = PortfolioReport(
        root=tmp_path,
        reports=[(repo_b, _make_failing_report(repo_b))],
        timestamp=datetime(2026, 5, 2, 15, 42),
    )
    out = _capture(scan)
    assert "Failing rules in this scan" in out
    assert "required" in out


def test_renders_error_status_for_exception(tmp_path: Path) -> None:
    err = ValueError("invalid TOML at line 3")
    repo_c = tmp_path / "broken"
    scan = PortfolioReport(
        root=tmp_path,
        reports=[(repo_c, err)],
        timestamp=datetime(2026, 5, 2, 15, 42),
    )
    out = _capture(scan)
    assert "broken" in out
    assert "error" in out
    assert "ValueError" in out
    assert "invalid TOML" in out
