"""Tests for human-readable Rich output."""

from io import StringIO
from pathlib import Path

from rich.console import Console

from suzerain.audit.output.human import render_human
from suzerain.core.report import Finding, Report


def _capture(report: Report) -> str:
    out = StringIO()
    console = Console(file=out, width=120, no_color=True)
    render_human(report, console=console)
    return out.getvalue()


def test_human_shows_repo_path(tmp_path: Path) -> None:
    report = Report(repo_path=tmp_path, stack="python", findings=[])
    text = _capture(report)
    assert str(tmp_path) in text


def test_human_shows_score(tmp_path: Path) -> None:
    findings = [
        Finding(rule_id="A", severity="required", status="pass", evidence="", fix_available=False),
    ]
    report = Report(repo_path=tmp_path, stack="python", findings=findings)
    text = _capture(report)
    assert "100" in text


def test_human_lists_failing_rules(tmp_path: Path) -> None:
    findings = [
        Finding(
            rule_id="PYTHON_LO001",
            severity="required",
            status="fail",
            evidence="missing src/",
            fix_available=False,
        ),
    ]
    report = Report(repo_path=tmp_path, stack="python", findings=findings)
    text = _capture(report)
    assert "PYTHON_LO001" in text
    assert "missing src/" in text


def test_human_marks_fixable(tmp_path: Path) -> None:
    findings = [
        Finding(rule_id="X", severity="required", status="fail", evidence="x", fix_available=True),
    ]
    report = Report(repo_path=tmp_path, stack="python", findings=findings)
    text = _capture(report)
    lower = text.lower()
    assert "fix" in lower or "auto" in lower
