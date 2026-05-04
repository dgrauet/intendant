"""Shared HTML assets — CSS, JS, and a tiny markdown→HTML helper.

Used by report_html.py and report_diff_html.py to build self-contained HTML
documents with no external assets.
"""

from __future__ import annotations

import html
import re

# ruff: noqa: E501

CSS_INLINE = """\
:root {
  --bg: #ffffff;
  --bg-alt: #fafafa;
  --text: #24292e;
  --text-muted: #6a737d;
  --border: #e1e4e8;
  --accent: #0366d6;
  --sev-required: #d73a49;
  --sev-recommended: #f0ad4e;
  --sev-ok: #28a745;
  --score-good: #28a745;
  --score-warn: #f0ad4e;
  --score-bad: #d73a49;
  --score-error: #6a737d;
}
@media (prefers-color-scheme: dark) {
  :root {
    --bg: #0d1117;
    --bg-alt: #161b22;
    --text: #c9d1d9;
    --text-muted: #8b949e;
    --border: #30363d;
    --accent: #58a6ff;
  }
}
* { box-sizing: border-box; }
body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  background: var(--bg);
  color: var(--text);
  margin: 0;
  padding: 24px;
  line-height: 1.5;
}
header { border-bottom: 1px solid var(--border); padding-bottom: 16px; margin-bottom: 24px; }
header h1 { margin: 0 0 4px; font-size: 1.6em; }
header .subtitle { color: var(--text-muted); font-size: 0.9em; }
.banner { padding: 16px; border-radius: 6px; margin-bottom: 24px; }
.banner-ok { background: rgba(40, 167, 69, 0.1); border: 1px solid var(--sev-ok); }
.banner-regression { background: rgba(215, 58, 73, 0.1); border: 1px solid var(--sev-required); }
.filter-bar { display: flex; gap: 12px; align-items: center; margin-bottom: 12px; flex-wrap: wrap; }
.filter-bar input, .filter-bar select { padding: 6px 8px; border: 1px solid var(--border); border-radius: 4px; background: var(--bg); color: var(--text); }
table { border-collapse: collapse; width: 100%; margin-bottom: 24px; }
th, td { padding: 8px 12px; text-align: left; border-bottom: 1px solid var(--border); }
th { background: var(--bg-alt); cursor: pointer; user-select: none; }
th:hover { background: var(--border); }
tr:nth-child(even) td { background: var(--bg-alt); }
.score-good { color: var(--score-good); font-weight: 600; }
.score-warn { color: var(--score-warn); font-weight: 600; }
.score-bad { color: var(--score-bad); font-weight: 600; }
.score-error { color: var(--score-error); }
.badge { display: inline-block; border-radius: 12px; padding: 2px 8px; font-size: 0.75em; color: white; margin-right: 4px; }
.sev-required { background: var(--sev-required); }
.sev-recommended { background: var(--sev-recommended); color: #1a1a1a; }
.sev-ok { background: var(--sev-ok); }
section { margin-top: 32px; }
section h2 { border-bottom: 1px solid var(--border); padding-bottom: 8px; }
details { border: 1px solid var(--border); border-radius: 4px; padding: 8px 12px; margin-bottom: 8px; }
details summary { cursor: pointer; font-weight: 500; }
details[open] summary { margin-bottom: 8px; }
.rule-body { color: var(--text-muted); font-size: 0.95em; }
.rule-body p { margin: 8px 0; }
.rule-body code { background: var(--bg-alt); padding: 1px 4px; border-radius: 3px; font-size: 0.9em; }
.rule-body pre { background: var(--bg-alt); padding: 12px; border-radius: 4px; overflow-x: auto; }
.empty { color: var(--text-muted); font-style: italic; }
.expand-controls { margin-bottom: 12px; }
.expand-controls button { padding: 4px 12px; border: 1px solid var(--border); border-radius: 4px; background: var(--bg); color: var(--text); cursor: pointer; margin-right: 8px; }
"""

JS_INLINE = """\
function sortTable(columnIndex) {
  const table = document.getElementById('repos');
  if (!table) return;
  const tbody = table.tBodies[0];
  const rows = Array.from(tbody.rows);
  const dir = table.dataset.sortDir === 'asc' && table.dataset.sortCol === String(columnIndex) ? 'desc' : 'asc';
  rows.sort((a, b) => {
    const av = a.cells[columnIndex].dataset.sort || a.cells[columnIndex].textContent.trim();
    const bv = b.cells[columnIndex].dataset.sort || b.cells[columnIndex].textContent.trim();
    const an = parseFloat(av), bn = parseFloat(bv);
    const cmp = (!isNaN(an) && !isNaN(bn)) ? an - bn : av.localeCompare(bv);
    return dir === 'asc' ? cmp : -cmp;
  });
  rows.forEach(r => tbody.appendChild(r));
  table.dataset.sortCol = columnIndex;
  table.dataset.sortDir = dir;
}

function applyFilter() {
  const table = document.getElementById('repos');
  if (!table) return;
  const text = (document.getElementById('filter-text')?.value || '').toLowerCase();
  const stack = document.getElementById('filter-stack')?.value || '';
  const reqOnly = document.getElementById('filter-req')?.checked || false;
  for (const row of table.tBodies[0].rows) {
    const path = (row.dataset.path || '').toLowerCase();
    const rowStack = row.dataset.stack || '';
    const failingReq = parseInt(row.dataset.failingRequired || '0', 10);
    const matchText = !text || path.includes(text);
    const matchStack = !stack || rowStack === stack;
    const matchReq = !reqOnly || failingReq > 0;
    row.style.display = (matchText && matchStack && matchReq) ? '' : 'none';
  }
}

function expandAll() {
  document.querySelectorAll('details').forEach(d => d.open = true);
}

function collapseAll() {
  document.querySelectorAll('details').forEach(d => d.open = false);
}
"""


_FENCE_RE = re.compile(r"```(.*?)```", re.DOTALL)
_INLINE_CODE_RE = re.compile(r"`([^`\n]+)`")
_BOLD_RE = re.compile(r"\*\*([^*\n]+?)\*\*")
_LINK_RE = re.compile(r"\[([^\]\n]+)\]\(([^)\n]+)\)")


def _safe_href(url: str) -> str:
    """Return url if it uses a safe scheme/relative form, else '#'.

    Input is HTML-escaped text (so `"` appears as `&quot;`). Reject any URL
    containing whitespace or `&quot;` to prevent attribute breakouts, and
    reject schemes other than http/https/mailto. Relative URLs (no scheme,
    or anchor/path) are allowed.
    """
    if " " in url or "\t" in url or "&quot;" in url or "&#x27;" in url:
        return "#"
    lower = url.lower()
    if "://" in lower:
        if not (lower.startswith("http://") or lower.startswith("https://")):
            return "#"
    elif ":" in lower and not lower.startswith("mailto:"):
        return "#"
    return url


def markdown_lite_to_html(text: str) -> str:
    """Render a tiny markdown subset to HTML.

    Supports:
    - Paragraphs (blank-line separated)
    - Inline code: ``backtick`` → <code>...</code>
    - Fenced code blocks: ```...``` → <pre><code>...</code></pre>
    - Bold: **text** → <strong>text</strong>
    - Links: [label](url) → <a href="url">label</a> (unsafe schemes → href="#")

    Everything is HTML-escaped first, so <script> tags etc. never reach the DOM.
    Returns '' for empty/whitespace-only input.
    """
    if not text or not text.strip():
        return ""
    # Extract fenced code blocks first, replace with placeholders, restore at end
    fences: list[str] = []

    def _stash(match: re.Match[str]) -> str:
        fences.append(match.group(1))
        return f"\x00FENCE{len(fences) - 1}\x00"

    work = _FENCE_RE.sub(_stash, text)
    # Escape everything else
    work = html.escape(work)
    # Inline code
    work = _INLINE_CODE_RE.sub(
        lambda m: f"<code>{html.escape(m.group(1))}</code>",
        work,
    )
    # Bold (after inline code so we don't bold inside code spans)
    work = _BOLD_RE.sub(r"<strong>\1</strong>", work)
    # Links — sanitize the href; label is already escaped
    work = _LINK_RE.sub(
        lambda m: f'<a href="{_safe_href(m.group(2))}">{m.group(1)}</a>',
        work,
    )
    # Paragraphs (split on blank lines)
    paragraphs = [p.strip() for p in work.split("\n\n") if p.strip()]
    rendered: list[str] = []
    for p in paragraphs:
        # Restore fences
        if "\x00FENCE" in p:
            for i, code in enumerate(fences):
                p = p.replace(
                    f"\x00FENCE{i}\x00", f"<pre><code>{html.escape(code).strip()}</code></pre>"
                )
        else:
            p = f"<p>{p}</p>"
        rendered.append(p)
    return "\n".join(rendered)
