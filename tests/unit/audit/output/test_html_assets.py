"""Tests for the shared HTML assets module."""

from __future__ import annotations

from intendant.audit.output._html_assets import (
    CSS_INLINE,
    JS_INLINE,
    markdown_lite_to_html,
)


def test_css_contains_dark_mode_media_query() -> None:
    """CSS includes a prefers-color-scheme dark block."""
    assert "@media (prefers-color-scheme: dark)" in CSS_INLINE
    assert "--bg" in CSS_INLINE
    assert "--sev-required" in CSS_INLINE


def test_css_defines_severity_classes() -> None:
    """Severity badge classes are defined."""
    assert ".sev-required" in CSS_INLINE
    assert ".sev-recommended" in CSS_INLINE


def test_js_defines_sort_filter_expand_handlers() -> None:
    """The inline JS exposes the three interactivity functions."""
    assert "function sortTable" in JS_INLINE
    assert "function applyFilter" in JS_INLINE
    assert "function expandAllRows" in JS_INLINE
    assert "function toggleFindings" in JS_INLINE


def test_markdown_lite_paragraphs() -> None:
    """Blank-line-separated text becomes <p> blocks."""
    md = "First paragraph.\n\nSecond paragraph."
    html = markdown_lite_to_html(md)
    assert html.count("<p>") == 2
    assert "First paragraph." in html
    assert "Second paragraph." in html


def test_markdown_lite_inline_code() -> None:
    """Backticks become <code>."""
    md = "Use `pyproject.toml` for config."
    html = markdown_lite_to_html(md)
    assert "<code>pyproject.toml</code>" in html


def test_markdown_lite_fenced_code_block() -> None:
    """Triple-backtick fences become <pre><code>."""
    md = "Run:\n\n```\nuv lock\n```\n\nDone."
    html = markdown_lite_to_html(md)
    assert "<pre><code>" in html
    assert "uv lock" in html
    assert "</code></pre>" in html


def test_markdown_lite_escapes_html_chars() -> None:
    """Raw <script> tags in markdown are escaped, not passed through."""
    md = "Beware <script>alert(1)</script> in inputs."
    html = markdown_lite_to_html(md)
    assert "<script>" not in html
    assert "&lt;script&gt;" in html


def test_markdown_lite_empty_input_returns_empty_string() -> None:
    """Empty input produces empty output (no crash)."""
    assert markdown_lite_to_html("") == ""
    assert markdown_lite_to_html("   \n\n  ") == ""


def test_markdown_lite_bold() -> None:
    """**text** becomes <strong>text</strong>."""
    md = "**Severity:** required"
    html = markdown_lite_to_html(md)
    assert "<strong>Severity:</strong>" in html
    assert "**" not in html


def test_markdown_lite_bold_multiple_per_line() -> None:
    """Multiple bold spans on the same line each render."""
    md = "**Severity:** required · **Stacks:** python"
    html = markdown_lite_to_html(md)
    assert "<strong>Severity:</strong>" in html
    assert "<strong>Stacks:</strong>" in html


def test_markdown_lite_bold_does_not_match_unbalanced() -> None:
    """A lone ** does not produce a stray <strong>."""
    md = "Use ** carefully"
    html = markdown_lite_to_html(md)
    assert "<strong>" not in html


def test_markdown_lite_link_http() -> None:
    """[label](https://...) becomes a safe <a> tag."""
    md = "See [Keep-a-Changelog](https://keepachangelog.com/en/1.1.0/) for the format."
    html = markdown_lite_to_html(md)
    assert '<a href="https://keepachangelog.com/en/1.1.0/">Keep-a-Changelog</a>' in html


def test_markdown_lite_link_relative() -> None:
    """Relative links (anchor / path) are preserved."""
    md = "See [ADR-0001](../adr/0001-layout.md) for rationale."
    html = markdown_lite_to_html(md)
    assert '<a href="../adr/0001-layout.md">ADR-0001</a>' in html


def test_markdown_lite_link_rejects_javascript_scheme() -> None:
    """javascript: URLs are stripped to '#' to prevent XSS."""
    md = "Click [me](javascript:alert(1))."
    html = markdown_lite_to_html(md)
    assert "javascript:" not in html
    assert 'href="#"' in html


def test_markdown_lite_link_rejects_data_scheme() -> None:
    """data: URLs are also blocked."""
    md = "Open [doc](data:text/html,<script>alert(1)</script>)."
    html = markdown_lite_to_html(md)
    assert "data:" not in html
    assert 'href="#"' in html


def test_markdown_lite_link_escapes_attribute_quotes() -> None:
    """A double-quote in a URL cannot break out of the href attribute."""
    md = '[x](https://evil.example/" onmouseover=alert(1) ")'
    html = markdown_lite_to_html(md)
    assert "onmouseover=alert" not in html
    assert '"' not in html.split('href="')[1].split('"')[0]


def test_markdown_lite_bold_inside_paragraph() -> None:
    """Bold spans inside a paragraph keep the paragraph wrapper."""
    md = "First **important** word.\n\nSecond paragraph."
    html = markdown_lite_to_html(md)
    assert "<p>First <strong>important</strong> word.</p>" in html
