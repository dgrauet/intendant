"""Tests for the snapshot HTML renderer."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from suzerain.audit.output.report_html import render_html
from suzerain.commands.report import PortfolioReport
from suzerain.core.handbook import Handbook
from suzerain.core.paths import docs_root
from suzerain.core.report import Finding, Report


def _build_scan(tmp_path: Path) -> PortfolioReport:
    """Build a 2-repo PortfolioReport for tests."""
    findings_a = [
        Finding(
            rule_id="DG002",
            severity="recommended",
            status="fail",
            evidence="missing CLAUDE.md",
            fix_available=False,
        ),
        Finding(
            rule_id="RL001",
            severity="required",
            status="fail",
            evidence="missing CHANGELOG.md",
            fix_available=True,
        ),
    ]
    report_a = Report(repo_path=tmp_path / "repo_a", stack="python", findings=findings_a)
    report_b = Report(
        repo_path=tmp_path / "repo_b",
        stack="node",
        findings=[
            Finding(
                rule_id="DG001",
                severity="required",
                status="pass",
                evidence="README.md present",
                fix_available=False,
            )
        ],
    )
    return PortfolioReport(
        root=tmp_path,
        reports=[
            (tmp_path / "repo_a", report_a),
            (tmp_path / "repo_b", report_b),
        ],
        timestamp=datetime(2026, 5, 4, 12, 0, 0),
    )


def test_render_html_returns_full_document(tmp_path: Path) -> None:
    """Output is a full <!doctype html> document."""
    scan = _build_scan(tmp_path)
    handbook = Handbook(root=docs_root())
    html = render_html(scan, handbook)
    assert html.startswith("<!doctype html>") or html.startswith("<!DOCTYPE html>")
    assert "</html>" in html


def test_render_html_contains_table_with_rows_per_repo(tmp_path: Path) -> None:
    """Main table has one <tr> per repo with data attributes for filtering."""
    scan = _build_scan(tmp_path)
    handbook = Handbook(root=docs_root())
    html = render_html(scan, handbook)
    assert '<table id="repos"' in html
    assert 'data-stack="python"' in html
    assert 'data-stack="node"' in html
    assert 'data-failing-required="1"' in html  # repo_a has 1 required fail
    assert 'data-failing-required="0"' in html  # repo_b has 0 fails


def test_render_html_inlines_dark_mode_css(tmp_path: Path) -> None:
    """The dark-mode media query is inlined into the document."""
    scan = _build_scan(tmp_path)
    html = render_html(scan, Handbook(root=docs_root()))
    assert "@media (prefers-color-scheme: dark)" in html


def test_render_html_legend_has_details_per_failing_rule(tmp_path: Path) -> None:
    """Each unique failing rule_id becomes a <details> with anchor id."""
    scan = _build_scan(tmp_path)
    html = render_html(scan, Handbook(root=docs_root()))
    assert 'id="rule-DG002"' in html
    assert 'id="rule-RL001"' in html
    # Passing rule should NOT appear in the legend
    assert 'id="rule-DG001"' not in html


def test_render_html_includes_handbook_body_for_known_rule(tmp_path: Path) -> None:
    """When the handbook has an entry for the rule, the body is embedded."""
    scan = _build_scan(tmp_path)
    handbook = Handbook(root=docs_root())
    html = render_html(scan, handbook)
    # DG002 is a real rule with a handbook entry — its title or body content should appear
    rule = handbook.get_rule("DG002")
    assert rule is not None
    assert rule.title in html


def test_render_html_inlines_filter_bar_and_script(tmp_path: Path) -> None:
    """Filter bar and JS interactivity are inlined."""
    scan = _build_scan(tmp_path)
    html = render_html(scan, Handbook(root=docs_root()))
    assert 'id="filter-text"' in html
    assert 'id="filter-stack"' in html
    assert 'id="filter-req"' in html
    assert "function sortTable" in html
    assert "function applyFilter" in html


def test_render_html_score_color_classes(tmp_path: Path) -> None:
    """Score cells have score-good/warn/bad classes based on thresholds."""
    scan = _build_scan(tmp_path)
    html = render_html(scan, Handbook(root=docs_root()))
    # repo_b has only 1 passing finding → score = 100 → score-good
    # repo_a has 2 failures → score < 100 → score-warn or score-bad
    assert 'class="score-good"' in html
    assert ('class="score-warn"' in html) or ('class="score-bad"' in html)


def test_render_html_handbook_none_falls_back(tmp_path: Path) -> None:
    """When handbook is None, legend entries show fallback message."""
    scan = _build_scan(tmp_path)
    html = render_html(scan, handbook=None)
    assert 'id="rule-DG002"' in html
    # No real handbook body, just the rule_id and a fallback marker
    assert "handbook entry not found" in html.lower() or "<em>" in html
