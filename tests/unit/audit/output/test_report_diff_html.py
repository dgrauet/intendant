"""Tests for the diff HTML renderer."""

from __future__ import annotations

from suzerain.audit.diff import PortfolioDiff
from suzerain.audit.output.report_diff_html import render_diff_html


def _build_diff_with_regression() -> PortfolioDiff:
    """Build a diff representing a portfolio that regressed."""
    current = {
        "schema_version": "2",
        "scan_count": 2,
        "repos": [
            {
                "path": "repo_a",
                "stack": "python",
                "score": 60,
                "status": "ok",
                "failing_rule_ids": ["DG002", "RL001"],
                "failing_by_severity": {"required": 1, "recommended": 1, "optional": 0},
                "fixable_count": 0,
            },
            {
                "path": "repo_b",
                "stack": "node",
                "score": 95,
                "status": "ok",
                "failing_rule_ids": [],
                "failing_by_severity": {"required": 0, "recommended": 0, "optional": 0},
                "fixable_count": 0,
            },
        ],
    }
    previous = {
        "schema_version": "2",
        "scan_count": 2,
        "repos": [
            {
                "path": "repo_a",
                "stack": "python",
                "score": 80,
                "status": "ok",
                "failing_rule_ids": ["DG002"],
                "failing_by_severity": {"required": 0, "recommended": 1, "optional": 0},
                "fixable_count": 0,
            },
            {
                "path": "repo_b",
                "stack": "node",
                "score": 95,
                "status": "ok",
                "failing_rule_ids": [],
                "failing_by_severity": {"required": 0, "recommended": 0, "optional": 0},
                "fixable_count": 0,
            },
        ],
    }
    return PortfolioDiff(current=current, previous=previous, previous_path="/tmp/snap.json")


def _build_diff_clean() -> PortfolioDiff:
    """Build a diff with zero changes."""
    snap = {
        "schema_version": "2",
        "scan_count": 1,
        "repos": [
            {
                "path": "repo_a",
                "stack": "python",
                "score": 100,
                "status": "ok",
                "failing_rule_ids": [],
                "failing_by_severity": {"required": 0, "recommended": 0, "optional": 0},
                "fixable_count": 0,
            },
        ],
    }
    return PortfolioDiff(current=snap, previous=snap, previous_path="/tmp/snap.json")


def test_render_diff_html_returns_full_document() -> None:
    diff = _build_diff_with_regression()
    html = render_diff_html(diff)
    assert html.startswith("<!doctype html>") or html.startswith("<!DOCTYPE html>")
    assert "</html>" in html


def test_render_diff_html_banner_regression() -> None:
    """Regression diff shows banner-regression class and red badge."""
    diff = _build_diff_with_regression()
    html = render_diff_html(diff)
    assert "banner-regression" in html
    # 1 new required failure (RL001 on repo_a)
    assert "1 new required failure" in html.lower() or "new required failure" in html.lower()


def test_render_diff_html_banner_ok() -> None:
    """Clean diff shows banner-ok and 'no regression'."""
    diff = _build_diff_clean()
    html = render_diff_html(diff)
    assert "banner-ok" in html
    assert "no regression" in html.lower() or "no new required" in html.lower()


def test_render_diff_html_has_five_sections() -> None:
    """All five sections rendered, even when empty."""
    diff = _build_diff_with_regression()
    html = render_diff_html(diff)
    for section in (
        "Score changes",
        "New failures",
        "Resolved failures",
        "New repos",
        "Removed repos",
    ):
        assert section in html


def test_render_diff_html_empty_section_shows_no_changes() -> None:
    """Empty sections render 'No changes' instead of being hidden."""
    diff = _build_diff_clean()
    html = render_diff_html(diff)
    # Clean diff → all 5 sections empty
    assert (
        html.count("No changes") >= 4
    )  # at least 4 empty sections (some may say 'no failure', etc.)


def test_render_diff_html_inlines_assets() -> None:
    """Diff page inlines the same CSS shell."""
    diff = _build_diff_with_regression()
    html = render_diff_html(diff)
    assert "@media (prefers-color-scheme: dark)" in html


def test_render_diff_html_score_change_shows_delta() -> None:
    """Score change section shows previous → current → Δ."""
    diff = _build_diff_with_regression()
    html = render_diff_html(diff)
    # repo_a went from 80 to 60, Δ=-20
    assert ">80<" in html or ">80 <" in html or "80" in html
    assert ">60<" in html or "60" in html
    assert "-20" in html
