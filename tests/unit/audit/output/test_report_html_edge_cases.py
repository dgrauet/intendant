"""Edge-case tests for render_html."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from suzerain.audit.output.report_html import render_html
from suzerain.commands.report import PortfolioReport
from suzerain.core.report import Finding, Report


def test_status_error_repo_renders_in_table(tmp_path: Path) -> None:
    """Repos with exception results render as a row with status=error."""
    scan = PortfolioReport(
        root=tmp_path,
        reports=[(tmp_path / "broken", RuntimeError("scan failed"))],
        timestamp=datetime(2026, 5, 4, 12, 0, 0),
    )
    html = render_html(scan)
    assert 'data-stack="error"' in html
    assert "scan failed" in html
    # Score class for error rows
    assert "score-error" in html


def test_empty_portfolio_renders_minimal_page(tmp_path: Path) -> None:
    """Zero-repo scan still produces a valid HTML doc with a clear message."""
    scan = PortfolioReport(
        root=tmp_path,
        reports=[],
        timestamp=datetime(2026, 5, 4, 12, 0, 0),
    )
    html = render_html(scan)
    assert html.startswith("<!doctype html>") or html.startswith("<!DOCTYPE html>")
    assert "No suzerain-governed repos found" in html
    # No table rendered when empty
    assert '<table id="repos"' not in html


def test_unknown_rule_id_appears_in_inline_findings(tmp_path: Path) -> None:
    """Unknown rule_ids still appear in the inline per-repo findings table."""
    findings = [
        Finding(
            rule_id="ZZZZZ_FAKE_999",
            severity="recommended",
            status="fail",
            evidence="synthetic",
            fix_available=False,
        )
    ]
    report = Report(repo_path=tmp_path / "r", stack="python", findings=findings)
    scan = PortfolioReport(
        root=tmp_path,
        reports=[(tmp_path / "r", report)],
        timestamp=datetime(2026, 5, 4, 12, 0, 0),
    )
    html = render_html(scan)
    assert "ZZZZZ_FAKE_999" in html
    assert "synthetic" in html


def test_html_escaping_in_repo_path_and_error(tmp_path: Path) -> None:
    """Special HTML chars in paths or exception messages are escaped."""
    scary_path = tmp_path / "<script>alert(1)</script>"
    scan = PortfolioReport(
        root=tmp_path,
        reports=[(scary_path, RuntimeError("<img src=x onerror=alert(1)>"))],
        timestamp=datetime(2026, 5, 4, 12, 0, 0),
    )
    html = render_html(scan)
    assert "<script>alert(1)</script>" not in html
    assert "&lt;script&gt;" in html
    assert "<img src=x" not in html
    assert "&lt;img" in html


def test_score_thresholds(tmp_path: Path) -> None:
    """Score classes follow the documented thresholds (>=85 good, >=60 warn, <60 bad)."""
    # All required pass → score 100 → good
    good_findings = [
        Finding(
            rule_id="DG001", severity="required", status="pass", evidence="", fix_available=False
        )
    ]
    # 1 of 2 required fails → score around 50 → bad
    bad_findings = [
        Finding(
            rule_id="DG001", severity="required", status="pass", evidence="", fix_available=False
        ),
        Finding(
            rule_id="DG002", severity="required", status="fail", evidence="", fix_available=False
        ),
    ]
    scan = PortfolioReport(
        root=tmp_path,
        reports=[
            (
                tmp_path / "good",
                Report(repo_path=tmp_path / "good", stack="python", findings=good_findings),
            ),
            (
                tmp_path / "bad",
                Report(repo_path=tmp_path / "bad", stack="python", findings=bad_findings),
            ),
        ],
        timestamp=datetime(2026, 5, 4, 12, 0, 0),
    )
    html = render_html(scan)
    assert 'class="score-good"' in html
    assert 'class="score-bad"' in html
