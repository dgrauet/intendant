"""Render a PortfolioReport to a self-contained HTML document."""

from __future__ import annotations

import html as html_lib
from typing import TYPE_CHECKING

from suzerain.audit.output._html_assets import (
    CSS_INLINE,
    JS_INLINE,
    markdown_lite_to_html,
)
from suzerain.core.report import Report

if TYPE_CHECKING:
    from suzerain.commands.report import PortfolioReport
    from suzerain.core.handbook import Handbook, RuleSection


def render_html(scan: PortfolioReport, handbook: Handbook | None = None) -> str:
    """Return a self-contained HTML document representing the portfolio report."""
    head = _render_head(scan)
    header = _render_header(scan)
    if not scan.reports:
        root_esc = html_lib.escape(str(scan.root))
        body = f"{header}<p>No suzerain-governed repos found under {root_esc}</p>"
    else:
        body = "".join(
            [
                header,
                _render_filter_bar(scan),
                _render_table(scan),
                _render_legend(scan, handbook),
                _render_script(),
            ]
        )
    return f'<!doctype html>\n<html lang="en">\n{head}\n<body>\n{body}\n</body>\n</html>\n'


def _render_head(scan: PortfolioReport) -> str:
    title = html_lib.escape(
        f"Suzerain report — {scan.root.name} — {scan.timestamp.isoformat(timespec='seconds')}"
    )
    return (
        "<head>\n"
        '<meta charset="utf-8">\n'
        f"<title>{title}</title>\n"
        f"<style>\n{CSS_INLINE}\n</style>\n"
        "</head>"
    )


def _render_header(scan: PortfolioReport) -> str:
    root = html_lib.escape(str(scan.root))
    ts = html_lib.escape(scan.timestamp.isoformat(timespec="seconds"))
    count = len(scan.reports)
    return (
        "<header>\n"
        "<h1>Portfolio report</h1>\n"
        f'<div class="subtitle">{root} · {ts} · {count} repo(s) scanned</div>\n'
        "</header>\n"
    )


def _render_filter_bar(scan: PortfolioReport) -> str:
    stacks = sorted(
        {_stack_for(result) for _, result in scan.reports if isinstance(result, Report)}
    )
    options = "\n".join(
        f'<option value="{html_lib.escape(s)}">{html_lib.escape(s)}</option>' for s in stacks
    )
    text_input = '<input id="filter-text" type="search" placeholder="filter by path…" oninput="applyFilter()">'  # noqa: E501
    req_label = '<label><input id="filter-req" type="checkbox" onchange="applyFilter()"> failing required only</label>'  # noqa: E501
    return (
        '<div class="filter-bar">\n'
        f"{text_input}\n"
        '<select id="filter-stack" onchange="applyFilter()">\n'
        '<option value="">all stacks</option>\n'
        f"{options}\n"
        "</select>\n"
        f"{req_label}\n"
        "</div>\n"
    )


def _render_table(scan: PortfolioReport) -> str:
    rows: list[str] = []
    for repo_path, result in scan.reports:
        try:
            rel = str(repo_path.relative_to(scan.root))
        except ValueError:
            rel = str(repo_path)
        if isinstance(result, Exception):
            rows.append(_render_row_error(rel, result))
        else:
            rows.append(_render_row_ok(rel, result))
    body = "\n".join(rows)
    return (
        '<table id="repos">\n'
        "<thead><tr>\n"
        '<th onclick="sortTable(0)">Path</th>\n'
        '<th onclick="sortTable(1)">Stack</th>\n'
        '<th onclick="sortTable(2)">Score</th>\n'
        '<th onclick="sortTable(3)">Required failures</th>\n'
        '<th onclick="sortTable(4)">Recommended failures</th>\n'
        '<th onclick="sortTable(5)">Fixable</th>\n'
        "</tr></thead>\n"
        f"<tbody>\n{body}\n</tbody>\n"
        "</table>\n"
    )


def _render_row_ok(rel_path: str, result: Report) -> str:
    failing = [f for f in result.findings if f.status == "fail"]
    req = sum(1 for f in failing if f.severity == "required")
    rec = sum(1 for f in failing if f.severity == "recommended")
    fix = sum(1 for f in failing if f.fix_available)
    score = result.score
    score_class = "score-good" if score >= 85 else "score-warn" if score >= 60 else "score-bad"
    stack_esc = html_lib.escape(_stack_for(result))
    path_esc = html_lib.escape(rel_path)
    return (
        f'<tr data-path="{path_esc}" data-stack="{stack_esc}" '
        f'data-failing-required="{req}">\n'
        f"<td>{path_esc}</td>\n"
        f"<td>{stack_esc}</td>\n"
        f'<td class="{score_class}" data-sort="{score}">{score}</td>\n'
        f'<td data-sort="{req}">{req}</td>\n'
        f'<td data-sort="{rec}">{rec}</td>\n'
        f'<td data-sort="{fix}">{fix}</td>\n'
        "</tr>"
    )


def _render_row_error(rel_path: str, exc: Exception) -> str:
    return (
        f'<tr data-path="{html_lib.escape(rel_path)}" data-stack="error" '
        f'data-failing-required="0">\n'
        f"<td>{html_lib.escape(rel_path)}</td>\n"
        '<td class="score-error">error</td>\n'
        f'<td class="score-error" data-sort="-1">N/A — {html_lib.escape(str(exc))}</td>\n'
        '<td data-sort="0">0</td>\n'
        '<td data-sort="0">0</td>\n'
        '<td data-sort="0">0</td>\n'
        "</tr>"
    )


def _render_legend(scan: PortfolioReport, handbook: Handbook | None) -> str:
    failing_by_id: dict[str, str] = {}  # rule_id -> severity
    for _, result in scan.reports:
        if isinstance(result, Report):
            for f in result.findings:
                if f.status == "fail":
                    failing_by_id.setdefault(f.rule_id, f.severity)
    if not failing_by_id:
        return (
            '<section id="failing-rules">'
            "<h2>Failing rules</h2>"
            '<p class="empty">No failing rules — clean portfolio.</p>'
            "</section>"
        )
    items: list[str] = []
    for rule_id in sorted(failing_by_id):
        severity = failing_by_id[rule_id]
        items.append(_render_rule_details(rule_id, severity, handbook))
    return (
        '<section id="failing-rules">\n'
        "<h2>Failing rules</h2>\n"
        '<div class="expand-controls">\n'
        '<button onclick="expandAll()">Expand all</button>\n'
        '<button onclick="collapseAll()">Collapse all</button>\n'
        "</div>\n" + "\n".join(items) + "\n</section>\n"
    )


def _render_rule_details(rule_id: str, severity: str, handbook: Handbook | None) -> str:
    rule: RuleSection | None = handbook.get_rule(rule_id) if handbook else None
    title = html_lib.escape(rule.title) if rule else "<em>(handbook entry not found)</em>"
    body_html = markdown_lite_to_html(rule.body) if rule else ""
    rid = html_lib.escape(rule_id)
    sev = html_lib.escape(severity)
    return (
        f'<details id="rule-{rid}" data-severity="{sev}">\n'
        f'<summary><span class="badge sev-{sev}">{sev}</span> '
        f"<code>{rid}</code> — {title}</summary>\n"
        f'<div class="rule-body">{body_html}</div>\n'
        "</details>"
    )


def _render_script() -> str:
    return f"<script>\n{JS_INLINE}\n</script>\n"


def _stack_for(result: Report) -> str:
    return result.stack or "auto"
