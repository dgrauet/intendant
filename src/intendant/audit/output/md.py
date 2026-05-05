"""Render a Report to PR-comment-friendly Markdown."""

from __future__ import annotations

from intendant.core.report import Finding, Report


def render_markdown(report: Report) -> str:
    lines: list[str] = []
    lines.append(f"## intendant audit — `{report.repo_path}`")
    lines.append("")
    stack_label = f"{report.mode} ({'/'.join(report.stacks)})" if report.stacks else report.mode
    lines.append("| Score | Stack | Passing | Failing | Exempt | Skipped | Fixable |")
    lines.append("|---|---|---|---|---|---|---|")
    lines.append(
        f"| **{report.score}/100** | `{stack_label}` | "
        f"{report.passing} | {report.failing} | {report.exempt} | "
        f"{report.skipped} | {report.fixable} |"
    )
    lines.append("")

    has_subprojects = any(f.subproject is not None for f in report.findings)
    if not has_subprojects:
        _append_flat_findings(report.findings, lines)
    else:
        _append_sections(report.findings, lines)

    return "\n".join(lines) + "\n"


def _append_flat_findings(findings: list[Finding], lines: list[str]) -> None:
    failing = [f for f in findings if f.status == "fail"]
    if not failing:
        lines.append("✅ All required checks passing.")
        return
    lines.append("### Findings to address")
    lines.append("")
    for f in failing:
        marker = "🔧" if f.fix_available else "✏️"
        lines.append(f"- {marker} **{f.rule_id}** ({f.severity}) — {f.evidence}")


def _append_sections(findings: list[Finding], lines: list[str]) -> None:
    """Group findings by subproject and emit one section per group."""
    groups: dict[str | None, list[Finding]] = {}
    for f in findings:
        groups.setdefault(f.subproject, []).append(f)

    if None in groups:
        lines.append("## ROOT (transverse rules)")
        lines.append("")
        _append_section_findings(groups[None], lines)
        lines.append("")

    for name, sub_findings in groups.items():
        if name is None:
            continue
        lines.append(f"## {name}")
        lines.append("")
        _append_section_findings(sub_findings, lines)
        lines.append("")


def _append_section_findings(findings: list[Finding], lines: list[str]) -> None:
    """Emit a findings table for a single subproject section."""
    lines.append("| Rule | Severity | Status | Evidence |")
    lines.append("|---|---|---|---|")
    for f in findings:
        lines.append(f"| **{f.rule_id}** | {f.severity} | {f.status} | {f.evidence} |")
    lines.append("")
    failing = [f for f in findings if f.status == "fail"]
    if not failing:
        lines.append("✅ All required checks passing.")
    else:
        lines.append("### Findings to address")
        lines.append("")
        for f in failing:
            marker = "🔧" if f.fix_available else "✏️"
            lines.append(f"- {marker} **{f.rule_id}** ({f.severity}) — {f.evidence}")
