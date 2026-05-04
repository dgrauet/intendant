"""E2E: suzerain report --format=html against the portfolio_mini fixture."""

from __future__ import annotations

import shutil
from html.parser import HTMLParser
from pathlib import Path

import pytest
from typer.testing import CliRunner

from suzerain.cli import app

FIXTURE = Path(__file__).parent.parent / "fixtures" / "portfolio_mini"


class _StructureParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.has_doctype = False
        self.tags: list[str] = []

    def handle_decl(self, decl: str) -> None:
        if decl.lower().startswith("doctype"):
            self.has_doctype = True

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.tags.append(tag)


@pytest.fixture
def fixture_copy(tmp_path: Path) -> Path:
    """Copy the portfolio fixture to tmp_path so writes don't pollute the source."""
    dst = tmp_path / "portfolio_mini"
    shutil.copytree(FIXTURE, dst)
    return dst


def test_report_html_creates_parseable_file(fixture_copy: Path, tmp_path: Path) -> None:
    """The CLI writes a valid HTML doc that the stdlib parser accepts."""
    out = tmp_path / "report.html"
    runner = CliRunner()
    result = runner.invoke(
        app, ["report", str(fixture_copy), "--format=html", "--output", str(out)]
    )
    assert result.exit_code in (0, 1), f"unexpected exit: {result.output}"
    assert out.exists()

    content = out.read_text()
    parser = _StructureParser()
    parser.feed(content)
    assert parser.has_doctype
    assert "html" in parser.tags
    assert "head" in parser.tags
    assert "body" in parser.tags
    assert "table" in parser.tags


def test_report_html_contains_fixture_repo_names(fixture_copy: Path, tmp_path: Path) -> None:
    """The rendered HTML mentions every governed repo in the fixture."""
    out = tmp_path / "report.html"
    runner = CliRunner()
    runner.invoke(app, ["report", str(fixture_copy), "--format=html", "--output", str(out)])
    content = out.read_text()
    governed = [p.parent.name for p in fixture_copy.rglob(".suzerain.toml")]
    assert governed, "fixture has no governed repos — fix the fixture"
    for repo_name in governed:
        assert repo_name in content, f"missing {repo_name} in HTML output"


def test_report_html_no_external_assets(fixture_copy: Path, tmp_path: Path) -> None:
    """Rendered HTML has no <link href=> or <script src=> references."""
    out = tmp_path / "report.html"
    runner = CliRunner()
    runner.invoke(app, ["report", str(fixture_copy), "--format=html", "--output", str(out)])
    content = out.read_text().lower()
    assert "<link " not in content or 'href="http' not in content
    assert "<script src=" not in content
