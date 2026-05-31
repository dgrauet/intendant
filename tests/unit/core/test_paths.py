"""Tests for asset-path resolution across editable vs installed (wheel) layouts."""

from __future__ import annotations

from pathlib import Path

from intendant.core.paths import _resolve_docs_root, _resolve_templates_root


def _make_editable_layout(tmp_path: Path) -> Path:
    """Create tmp/src/intendant/__init__.py + tmp/docs + tmp/templates; return pkg_file."""
    pkg = tmp_path / "src" / "intendant"
    pkg.mkdir(parents=True)
    pkg_file = pkg / "__init__.py"
    pkg_file.write_text("")
    (tmp_path / "docs" / "handbook").mkdir(parents=True)
    (tmp_path / "docs" / "adr").mkdir(parents=True)
    (tmp_path / "templates" / "_common").mkdir(parents=True)
    return pkg_file


def _make_wheel_layout(tmp_path: Path) -> Path:
    """Create site-packages/intendant/__init__.py with bundled _assets; return pkg_file."""
    pkg = tmp_path / "site-packages" / "intendant"
    pkg.mkdir(parents=True)
    pkg_file = pkg / "__init__.py"
    pkg_file.write_text("")
    (pkg / "_assets" / "handbook").mkdir(parents=True)
    (pkg / "_assets" / "adr").mkdir(parents=True)
    (pkg / "_assets" / "templates" / "_common").mkdir(parents=True)
    return pkg_file


def test_docs_root_prefers_bundled_assets_in_wheel(tmp_path: Path) -> None:
    """An installed wheel resolves docs from the package's bundled _assets/."""
    pkg_file = _make_wheel_layout(tmp_path)
    resolved = _resolve_docs_root(pkg_file, env=None)
    assert resolved == pkg_file.parent / "_assets"
    assert (resolved / "handbook").is_dir()


def test_templates_root_prefers_bundled_assets_in_wheel(tmp_path: Path) -> None:
    pkg_file = _make_wheel_layout(tmp_path)
    resolved = _resolve_templates_root(pkg_file, env=None)
    assert resolved == pkg_file.parent / "_assets" / "templates"
    assert resolved.is_dir()


def test_docs_root_falls_back_to_editable_checkout(tmp_path: Path) -> None:
    """Without bundled assets, resolve docs/ from the source checkout (editable)."""
    pkg_file = _make_editable_layout(tmp_path)
    resolved = _resolve_docs_root(pkg_file, env=None)
    assert resolved == tmp_path / "docs"


def test_templates_root_falls_back_to_editable_checkout(tmp_path: Path) -> None:
    pkg_file = _make_editable_layout(tmp_path)
    resolved = _resolve_templates_root(pkg_file, env=None)
    assert resolved == tmp_path / "templates"


def test_env_override_takes_precedence_for_docs(tmp_path: Path) -> None:
    """INTENDANT_ROOT wins over both bundled and editable resolution."""
    pkg_file = _make_wheel_layout(tmp_path)  # bundled assets present...
    override = tmp_path / "custom"
    resolved = _resolve_docs_root(pkg_file, env=str(override))
    assert resolved == override / "docs"


def test_env_override_takes_precedence_for_templates(tmp_path: Path) -> None:
    pkg_file = _make_wheel_layout(tmp_path)
    override = tmp_path / "custom"
    resolved = _resolve_templates_root(pkg_file, env=str(override))
    assert resolved == override / "templates"
