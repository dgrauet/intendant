"""Render a PortfolioReport to a self-contained HTML document."""

from __future__ import annotations

import html as html_lib
from typing import TYPE_CHECKING

from suzerain.audit.output._html_assets import CSS_INLINE, JS_INLINE
from suzerain.core.report import Report

if TYPE_CHECKING:
    from suzerain.commands.report import PortfolioReport


def render_html(scan: PortfolioReport) -> str:
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
    stacks: set[str] = set()
    for _, result in scan.reports:
        if isinstance(result, Report):
            stacks.update(result.stacks)
    stacks_sorted = sorted(stacks)
    options = "\n".join(
        f'<option value="{html_lib.escape(s)}">{html_lib.escape(s)}</option>' for s in stacks_sorted
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
    controls = (
        '<div class="expand-controls">\n'
        "<button onclick=\"expandAllRows('repos')\">Expand all</button>\n"
        "<button onclick=\"collapseAllRows('repos')\">Collapse all</button>\n"
        "</div>\n"
    )
    return (
        f"{controls}"
        '<table id="repos">\n'
        "<thead><tr>\n"
        "<th></th>\n"
        '<th onclick="sortTable(1)">Path</th>\n'
        '<th onclick="sortTable(2)">Stack</th>\n'
        '<th onclick="sortTable(3)">Score</th>\n'
        '<th onclick="sortTable(4)">Failed required rules</th>\n'
        '<th onclick="sortTable(5)">Failed recommended rules</th>\n'
        '<th onclick="sortTable(6)">Fixable</th>\n'
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
    stack_attr = html_lib.escape("/".join(result.stacks))
    stack_label_esc = html_lib.escape(_stack_label(result))
    path_esc = html_lib.escape(rel_path)
    has_findings = bool(result.findings)
    toggle_cell = (
        '<td class="row-toggle" onclick="toggleFindings(this)"><span class="caret">▸</span></td>'
        if has_findings
        else '<td class="row-toggle"></td>'
    )
    main_row = (
        f'<tr class="repo-row" data-path="{path_esc}" data-stack="{stack_attr}" '
        f'data-failing-required="{req}">\n'
        f"{toggle_cell}\n"
        f"<td>{path_esc}</td>\n"
        f"<td>{stack_label_esc}</td>\n"
        f'<td class="{score_class}" data-sort="{score}">{score}</td>\n'
        f'<td data-sort="{req}">{req}</td>\n'
        f'<td data-sort="{rec}">{rec}</td>\n'
        f'<td data-sort="{fix}">{fix}</td>\n'
        "</tr>"
    )
    if not has_findings:
        return main_row
    findings_row = (
        '<tr class="findings-row" hidden>\n'
        f'<td></td><td colspan="6">{_render_findings_table(result)}</td>\n'
        "</tr>"
    )
    return f"{main_row}\n{findings_row}"


def _render_row_error(rel_path: str, exc: Exception) -> str:
    return (
        f'<tr class="repo-row" data-path="{html_lib.escape(rel_path)}" data-stack="error" '
        f'data-failing-required="0">\n'
        '<td class="row-toggle"></td>\n'
        f"<td>{html_lib.escape(rel_path)}</td>\n"
        '<td class="score-error">error</td>\n'
        f'<td class="score-error" data-sort="-1">N/A — {html_lib.escape(str(exc))}</td>\n'
        '<td data-sort="0">0</td>\n'
        '<td data-sort="0">0</td>\n'
        '<td data-sort="0">0</td>\n'
        "</tr>"
    )


def _render_findings_table(result: Report) -> str:
    rank = {"fail": 0, "pass": 1, "exempt": 2, "skip": 3}
    sorted_findings = sorted(result.findings, key=lambda f: (rank.get(f.status, 9), f.rule_id))
    rows: list[str] = []
    for f in sorted_findings:
        rid = html_lib.escape(f.rule_id)
        sev = html_lib.escape(f.severity)
        status = html_lib.escape(f.status)
        evidence = html_lib.escape(f.evidence)
        sub = html_lib.escape(f.subproject) if f.subproject else ""
        rid_cell = f"<code>{rid}</code>" + (f' <span class="muted">[{sub}]</span>' if sub else "")
        rows.append(
            f"<tr>"
            f"<td>{rid_cell}</td>"
            f'<td><span class="badge sev-{sev}">{sev}</span></td>'
            f'<td class="status-{status}">{status}</td>'
            f"<td>{evidence}</td>"
            f"</tr>"
        )
    return (
        '<table class="findings"><thead><tr>'
        "<th>Rule</th><th>Severity</th><th>Status</th><th>Evidence</th>"
        "</tr></thead><tbody>\n" + "\n".join(rows) + "\n</tbody></table>"
    )


def _render_script() -> str:
    return f"<script>\n{JS_INLINE}\n</script>\n"


def _stack_label(result: Report) -> str:
    """Return ``"<mode> (<stacks>)"`` for the stack column.

    Examples: ``auto``, ``auto (python)``, ``auto (python/swift)``,
    ``manual (node)``, ``manual (swift/python)``.
    """
    if result.stacks:
        return f"{result.mode} ({'/'.join(result.stacks)})"
    return result.mode
