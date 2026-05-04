"""Tests for the shared HTML assets module."""

from __future__ import annotations

from suzerain.audit.output._html_assets import (
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
    assert "function expandAll" in JS_INLINE


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
