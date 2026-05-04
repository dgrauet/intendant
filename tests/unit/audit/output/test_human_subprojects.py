"""Tests for multi-subproject human (Rich) terminal rendering."""

from __future__ import annotations

from io import StringIO
from pathlib import Path
from typing import Literal

from rich.console import Console

from suzerain.audit.output.human import render_human
from suzerain.core.report import Finding, Report


def _capture(report: Report) -> str:
    out = StringIO()
    console = Console(file=out, width=120, no_color=True)
    render_human(report, console=console)
    return out.getvalue()


def _make_finding(
    rule_id: str,
    status: Literal["pass", "fail", "skip", "exempt"],
    subproject: str | None,
) -> Finding:
    return Finding(
        rule_id=rule_id,
        severity="required",
        status=status,
        evidence="",
        fix_available=False,
        subproject=subproject,
    )


def test_human_renders_single_section_when_all_findings_have_no_subproject(
    tmp_path: Path,
) -> None:
    """Backward compat: legacy single-Repo report renders as a single flat table."""
    report = Report(
        repo_path=tmp_path,
        stack="python",
        findings=[_make_finding("PYTHON_LO001", "pass", None)],
    )
    out = _capture(report)
    assert "ROOT" not in out
    assert "PYTHON_LO001" in out


def test_human_renders_multi_sections_when_findings_have_subprojects(
    tmp_path: Path,
) -> None:
    """Multi-subproject report renders one section per subproject + ROOT for transverse."""
    report = Report(
        repo_path=tmp_path,
        stack="multi",
        findings=[
            _make_finding("DG001", "pass", None),
            _make_finding("PYTHON_LO001", "pass", "backend"),
            _make_finding("NODE_PK001", "pass", "frontend"),
        ],
    )
    out = _capture(report)
    assert "ROOT" in out
    assert "backend" in out
    assert "frontend" in out
    assert "DG001" in out
    assert "PYTHON_LO001" in out
    assert "NODE_PK001" in out
