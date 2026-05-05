"""Render a PortfolioDiff to a self-contained HTML document."""

from __future__ import annotations

import html as html_lib
from typing import TYPE_CHECKING

from intendant.audit.output._html_assets import CSS_INLINE, JS_INLINE

if TYPE_CHECKING:
    from intendant.audit.diff import PortfolioDiff
    from intendant.core.handbook import Handbook


def render_diff_html(diff: PortfolioDiff, handbook: Handbook | None = None) -> str:
    """Return a self-contained HTML document representing a portfolio diff."""
    title = "Intendant report diff"
    head = (
        "<head>\n"
        '<meta charset="utf-8">\n'
        f"<title>{html_lib.escape(title)}</title>\n"
        f"<style>\n{CSS_INLINE}\n</style>\n"
        "</head>"
    )
    body = "".join(
        [
            _render_header(diff),
            _render_banner(diff),
            _render_section_score_changes(diff),
            _render_section_new_failures(diff),
            _render_section_resolved_failures(diff),
            _render_section_new_repos(diff),
            _render_section_removed_repos(diff),
            f"<script>\n{JS_INLINE}\n</script>\n",
        ]
    )
    return f'<!doctype html>\n<html lang="en">\n{head}\n<body>\n{body}\n</body>\n</html>\n'


def _render_header(diff: PortfolioDiff) -> str:
    prev = html_lib.escape(diff.previous_path)
    return (
        "<header>\n"
        "<h1>Portfolio report — diff</h1>\n"
        f'<div class="subtitle">vs {prev}</div>\n'
        "</header>\n"
    )


def _render_banner(diff: PortfolioDiff) -> str:
    new_req = sum(1 for f in diff.new_failures if f.get("severity") == "required")
    avg_delta = _avg_score_delta(diff)
    delta_str = f"{avg_delta:+.1f}" if avg_delta is not None else "n/a"
    if new_req > 0:
        cls = "banner-regression"
        msg = f"{new_req} new required failure(s)"
    else:
        cls = "banner-ok"
        msg = "No regression — no new required failures"
    return (
        f'<div class="banner {cls}">\n'
        f"<strong>{html_lib.escape(msg)}</strong> · "
        f"average score delta: {html_lib.escape(delta_str)}\n"
        "</div>\n"
    )


def _avg_score_delta(diff: PortfolioDiff) -> float | None:
    deltas = [c["delta"] for c in diff.score_changes if isinstance(c.get("delta"), (int, float))]
    if not deltas:
        return 0.0
    return sum(deltas) / len(deltas)


def _render_section_score_changes(diff: PortfolioDiff) -> str:
    items = diff.score_changes
    if not items:
        return _empty_section("Score changes", 0)
    rows = [
        f"<tr><td>{html_lib.escape(c['path'])}</td>"
        f"<td>{c['before']}</td><td>{c['after']}</td>"
        f"<td>{c['delta']:+d}</td></tr>"
        for c in items
    ]
    return (
        f"<section><h2>Score changes ({len(items)})</h2>\n"
        "<table><thead><tr>"
        "<th>Path</th><th>Previous</th><th>Current</th><th>Δ</th>"
        "</tr></thead>\n"
        f"<tbody>{''.join(rows)}</tbody></table></section>\n"
    )


def _render_section_new_failures(diff: PortfolioDiff) -> str:
    items = diff.new_failures
    if not items:
        return _empty_section("New failures", 0)
    rows: list[str] = []
    for f in items:
        sev = f.get("severity", "recommended")
        rows.append(
            f'<li><span class="badge sev-{html_lib.escape(sev)}">'
            f"{html_lib.escape(sev)}</span> "
            f"<code>{html_lib.escape(f['rule_id'])}</code> on "
            f"<code>{html_lib.escape(f['path'])}</code></li>"
        )
    return f"<section><h2>New failures ({len(items)})</h2>\n<ul>{''.join(rows)}</ul></section>\n"


def _render_section_resolved_failures(diff: PortfolioDiff) -> str:
    items = diff.resolved_failures
    if not items:
        return _empty_section("Resolved failures", 0)
    rows = [
        f"<li><code>{html_lib.escape(f['rule_id'])}</code> on "
        f"<code>{html_lib.escape(f['path'])}</code></li>"
        for f in items
    ]
    return (
        f"<section><h2>Resolved failures ({len(items)})</h2>\n<ul>{''.join(rows)}</ul></section>\n"
    )


def _render_section_new_repos(diff: PortfolioDiff) -> str:
    items = diff.new_repos
    if not items:
        return _empty_section("New repos", 0)
    rows = [f"<li><code>{html_lib.escape(p)}</code></li>" for p in items]
    return f"<section><h2>New repos ({len(items)})</h2>\n<ul>{''.join(rows)}</ul></section>\n"


def _render_section_removed_repos(diff: PortfolioDiff) -> str:
    items = diff.removed_repos
    if not items:
        return _empty_section("Removed repos", 0)
    rows = [f"<li><code>{html_lib.escape(p)}</code></li>" for p in items]
    return f"<section><h2>Removed repos ({len(items)})</h2>\n<ul>{''.join(rows)}</ul></section>\n"


def _empty_section(title: str, count: int) -> str:
    return (
        f"<section><h2>{html_lib.escape(title)} ({count})</h2>\n"
        '<p class="empty">No changes</p></section>\n'
    )
