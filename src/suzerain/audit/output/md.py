"""Render a Report to PR-comment-friendly Markdown."""

from __future__ import annotations

from suzerain.core.report import Report


def render_markdown(report: Report) -> str:
    lines: list[str] = []
    lines.append(f"## suzerain audit — `{report.repo_path}`")
    lines.append("")
    lines.append("| Score | Stack | Passing | Failing | Exempt | Skipped | Fixable |")
    lines.append("|---|---|---|---|---|---|---|")
    lines.append(
        f"| **{report.score}/100** | `{report.stack}` | "
        f"{report.passing} | {report.failing} | {report.exempt} | "
        f"{report.skipped} | {report.fixable} |"
    )
    lines.append("")
    failing = [f for f in report.findings if f.status == "fail"]
    if not failing:
        lines.append("✅ All required checks passing.")
        return "\n".join(lines) + "\n"
    lines.append("### Findings to address")
    lines.append("")
    for f in failing:
        marker = "🔧" if f.fix_available else "✏️"
        lines.append(f"- {marker} **{f.rule_id}** ({f.severity}) — {f.evidence}")
    return "\n".join(lines) + "\n"
