"""Tests for the snapshot HTML renderer."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from suzerain.audit.output.report_html import render_html
from suzerain.commands.report import PortfolioReport
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
    html = render_html(scan)
    assert html.startswith("<!doctype html>") or html.startswith("<!DOCTYPE html>")
    assert "</html>" in html


def test_render_html_contains_table_with_rows_per_repo(tmp_path: Path) -> None:
    """Main table has one <tr> per repo with data attributes for filtering."""
    scan = _build_scan(tmp_path)
    html = render_html(scan)
    assert '<table id="repos"' in html
    assert 'data-stack="python"' in html
    assert 'data-stack="node"' in html
    assert 'data-failing-required="1"' in html  # repo_a has 1 required fail
    assert 'data-failing-required="0"' in html  # repo_b has 0 fails


def test_render_html_inlines_dark_mode_css(tmp_path: Path) -> None:
    """The dark-mode media query is inlined into the document."""
    scan = _build_scan(tmp_path)
    html = render_html(scan)
    assert "@media (prefers-color-scheme: dark)" in html


def test_render_html_no_failing_rules_legend(tmp_path: Path) -> None:
    """The standalone 'Failing rules' legend section was removed."""
    html = render_html(_build_scan(tmp_path))
    assert 'id="failing-rules"' not in html
    assert 'id="rule-DG002"' not in html
    assert ">Failing rules<" not in html


def test_render_html_inlines_filter_bar_and_script(tmp_path: Path) -> None:
    """Filter bar and JS interactivity are inlined."""
    scan = _build_scan(tmp_path)
    html = render_html(scan)
    assert 'id="filter-text"' in html
    assert 'id="filter-stack"' in html
    assert 'id="filter-req"' in html
    assert "function sortTable" in html
    assert "function applyFilter" in html


def test_render_html_score_color_classes(tmp_path: Path) -> None:
    """Score cells have score-good/warn/bad classes based on thresholds."""
    scan = _build_scan(tmp_path)
    html = render_html(scan)
    # repo_b has only 1 passing finding → score = 100 → score-good
    # repo_a has 2 failures → score < 100 → score-warn or score-bad
    assert 'class="score-good"' in html
    assert ('class="score-warn"' in html) or ('class="score-bad"' in html)


def test_render_html_renames_failure_columns(tmp_path: Path) -> None:
    """Column headers say 'Failed required/recommended rules' (not 'failures')."""
    html = render_html(_build_scan(tmp_path))
    assert "Failed required rules" in html
    assert "Failed recommended rules" in html
    assert ">Required failures<" not in html
    assert ">Recommended failures<" not in html


def test_render_html_stack_label_auto_when_no_config(tmp_path: Path) -> None:
    """Without .suzerain.toml the stack cell shows the bare detected stack."""
    scan = _build_scan(tmp_path)
    html = render_html(scan)
    # data-stack stays the resolved stack (used by the filter)
    assert 'data-stack="python"' in html
    # No config file present → no mode badge
    assert "manual (python)" not in html
    assert "auto (python)" not in html


def test_render_html_stack_label_undetected_shows_plain_auto(tmp_path: Path) -> None:
    """When auto-detection found nothing (stack='auto'), display just 'auto'."""
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / ".suzerain.toml").write_text(
        '[suzerain]\nversion = "1"\nstack = "auto"\nmode = "advisory"\n'
    )
    scan = PortfolioReport(
        root=tmp_path,
        reports=[
            (repo, Report(repo_path=repo, stack="auto", findings=[])),
        ],
        timestamp=datetime(2026, 5, 5, 0, 0, 0),
    )
    html = render_html(scan)
    assert "auto (auto)" not in html
    assert ">auto<" in html


def test_render_html_stack_label_subprojects(tmp_path: Path) -> None:
    """With [[subprojects]], cell shows 'manual (a/b)' from declared stacks."""
    repo = tmp_path / "repo"
    (repo / "frontend").mkdir(parents=True)
    (repo / "backend").mkdir(parents=True)
    (repo / ".suzerain.toml").write_text(
        '[suzerain]\nversion = "1"\nstack = "auto"\nmode = "advisory"\n'
        '[[subprojects]]\npath = "frontend"\nstack = "swift"\n'
        '[[subprojects]]\npath = "backend"\nstack = "python"\n'
    )
    scan = PortfolioReport(
        root=tmp_path,
        reports=[
            (repo, Report(repo_path=repo, stack="multi", findings=[])),
        ],
        timestamp=datetime(2026, 5, 5, 0, 0, 0),
    )
    html = render_html(scan)
    assert "manual (swift/python)" in html
    assert "auto (multi)" not in html


def test_render_html_stack_label_manual_when_config_pins_stack(tmp_path: Path) -> None:
    """With stack='node' in .suzerain.toml, the cell shows 'manual (node)'."""
    scan = _build_scan(tmp_path)
    repo_b = tmp_path / "repo_b"
    repo_b.mkdir(parents=True, exist_ok=True)
    (repo_b / ".suzerain.toml").write_text(
        '[suzerain]\nversion = "1"\nstack = "node"\nmode = "advisory"\n'
    )
    html = render_html(scan)
    assert "manual (node)" in html


def test_render_html_stack_label_auto_when_config_says_auto(tmp_path: Path) -> None:
    """With stack='auto' explicitly set, the cell shows 'auto (python)'."""
    scan = _build_scan(tmp_path)
    repo_a = tmp_path / "repo_a"
    repo_a.mkdir(parents=True, exist_ok=True)
    (repo_a / ".suzerain.toml").write_text(
        '[suzerain]\nversion = "1"\nstack = "auto"\nmode = "advisory"\n'
    )
    html = render_html(scan)
    assert "auto (python)" in html


def test_render_html_inline_findings_row_per_repo(tmp_path: Path) -> None:
    """Each repo row is followed by a hidden findings-row with its rules table."""
    scan = _build_scan(tmp_path)
    html = render_html(scan)
    # Toggle cell on the main row
    assert 'class="row-toggle"' in html
    assert "toggleFindings" in html
    # Hidden inline expansion row carrying the per-rule table
    assert 'class="findings-row"' in html
    assert '<table class="findings"' in html
    # Failing rule_ids from repo_a appear inside the inline expansion
    assert "DG002" in html
    assert "RL001" in html
    # status classes used in the inline mini-table
    assert 'class="status-fail"' in html
    assert 'class="status-pass"' in html


def test_render_html_table_has_top_level_expand_collapse(tmp_path: Path) -> None:
    """The repos table exposes scoped expand/collapse buttons."""
    html = render_html(_build_scan(tmp_path))
    assert "expandAllRows('repos')" in html
    assert "collapseAllRows('repos')" in html


def test_render_html_no_separate_per_repo_section(tmp_path: Path) -> None:
    """The standalone per-repo section was folded back into the main table."""
    html = render_html(_build_scan(tmp_path))
    assert 'id="per-repo-findings"' not in html
    assert "Per-project rule mapping" not in html
