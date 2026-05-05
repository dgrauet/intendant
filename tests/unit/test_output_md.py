"""Tests for Markdown (PR-comment friendly) output."""

from pathlib import Path

from intendant.audit.output.md import render_markdown
from intendant.core.report import Finding, Report


def test_md_starts_with_header(tmp_path: Path) -> None:
    report = Report(repo_path=tmp_path, stacks=("python",), mode="auto", findings=[])
    md = render_markdown(report)
    assert md.startswith("## intendant audit")


def test_md_contains_score_table(tmp_path: Path) -> None:
    findings = [
        Finding(rule_id="A", severity="required", status="pass", evidence="", fix_available=False),
    ]
    report = Report(repo_path=tmp_path, stacks=("python",), mode="auto", findings=findings)
    md = render_markdown(report)
    assert "| Score |" in md or "**Score**" in md


def test_md_lists_failures(tmp_path: Path) -> None:
    findings = [
        Finding(
            rule_id="PYTHON_LO001",
            severity="required",
            status="fail",
            evidence="missing src/",
            fix_available=True,
        ),
    ]
    report = Report(repo_path=tmp_path, stacks=("python",), mode="auto", findings=findings)
    md = render_markdown(report)
    assert "PYTHON_LO001" in md
    assert "missing src/" in md


def test_md_omits_pass_section_when_no_failures(tmp_path: Path) -> None:
    findings = [
        Finding(rule_id="A", severity="required", status="pass", evidence="", fix_available=False),
    ]
    report = Report(repo_path=tmp_path, stacks=("python",), mode="auto", findings=findings)
    md = render_markdown(report)
    assert "All required checks passing" in md or "✅" in md


def test_md_renders_subproject_sections_when_multi(tmp_path: Path) -> None:
    """Multi-subproject markdown emits one ## section per subproject + ROOT."""
    from intendant.audit.output.md import render_markdown
    from intendant.core.report import Finding, Report

    report = Report(
        repo_path=tmp_path,
        stacks=("python", "node"),
        mode="manual",
        findings=[
            Finding(
                rule_id="DG001",
                severity="required",
                status="pass",
                evidence="",
                fix_available=False,
                subproject=None,
            ),
            Finding(
                rule_id="PYTHON_LO001",
                severity="required",
                status="pass",
                evidence="",
                fix_available=False,
                subproject="backend",
            ),
        ],
    )
    out = render_markdown(report)
    assert "## ROOT" in out or "### ROOT" in out
    assert "backend" in out
    assert "DG001" in out
    assert "PYTHON_LO001" in out
