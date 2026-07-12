"""Tests for transverse LO rules."""

from pathlib import Path

from intendant.checks.lo import LO003DocsDirectory, LO004NestedStackCoverage
from intendant.core.repo import Repo


def _repo(tmp_path: Path) -> Repo:
    return Repo(path=tmp_path, stacks=("auto",))


def test_lo003_passes_when_docs_dir_exists(tmp_path: Path) -> None:
    (tmp_path / "docs").mkdir()
    assert LO003DocsDirectory().check(_repo(tmp_path)).passing is True


def test_lo003_fails_when_docs_dir_missing(tmp_path: Path) -> None:
    result = LO003DocsDirectory().check(_repo(tmp_path))
    assert result.passing is False
    assert "docs/" in result.evidence


def test_lo003_fails_when_docs_is_a_file(tmp_path: Path) -> None:
    (tmp_path / "docs").write_text("not a dir")
    assert LO003DocsDirectory().check(_repo(tmp_path)).passing is False


# --- LO004: nested stack roots covered by governance ---


def _write_config(path: Path, body: str) -> None:
    (path / ".intendant.toml").write_text(body)


def test_lo004_fail_orphan_nested_stack(tmp_path: Path) -> None:
    """A nested marker whose stack no ancestor declares is an orphan (apps/windows case)."""
    _write_config(
        tmp_path,
        '[intendant]\nversion = "1"\n\n'
        '[[subprojects]]\nname = "core"\npath = "."\nstack = "rust"\n',
    )
    (tmp_path / "Cargo.toml").write_text("[workspace]\n")
    win = tmp_path / "apps" / "windows"
    win.mkdir(parents=True)
    (win / "App.sln").write_text("sln\n")
    result = LO004NestedStackCoverage().check(Repo(path=tmp_path, stacks=("rust",)))
    assert result.passing is False
    assert "apps/windows" in result.evidence
    assert "dotnet" in result.evidence


def test_lo004_pass_covered_by_subproject_at_ancestor(tmp_path: Path) -> None:
    _write_config(
        tmp_path,
        "[intendant]\n"
        'version = "1"\n\n'
        '[[subprojects]]\nname = "core"\npath = "."\nstack = "rust"\n\n'
        '[[subprojects]]\nname = "windows-app"\npath = "apps/windows"\nstack = "dotnet"\n',
    )
    (tmp_path / "Cargo.toml").write_text("[workspace]\n")
    nested = tmp_path / "apps" / "windows" / "App"
    nested.mkdir(parents=True)
    (nested / "App.csproj").write_text("<Project/>\n")
    result = LO004NestedStackCoverage().check(Repo(path=tmp_path, stacks=("rust",)))
    assert result.passing is True


def test_lo004_pass_workspace_members_covered_by_root_stack(tmp_path: Path) -> None:
    _write_config(
        tmp_path,
        '[intendant]\nversion = "1"\n\n'
        '[[subprojects]]\nname = "core"\npath = "."\nstack = "rust"\n',
    )
    (tmp_path / "Cargo.toml").write_text("[workspace]\n")
    member = tmp_path / "crates" / "foo"
    member.mkdir(parents=True)
    (member / "Cargo.toml").write_text("[package]\n")
    result = LO004NestedStackCoverage().check(Repo(path=tmp_path, stacks=("rust",)))
    assert result.passing is True


def test_lo004_no_config_uses_detected_root_stacks(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text("[project]\n")
    docs = tmp_path / "docs-site"
    docs.mkdir()
    (docs / "package.json").write_text("{}\n")
    result = LO004NestedStackCoverage().check(Repo(path=tmp_path, stacks=("python",)))
    assert result.passing is False
    assert "docs-site" in result.evidence


def test_lo004_no_config_same_stack_nested_is_covered(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text("[project]\n")
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "pyproject.toml").write_text("[project]\n")
    result = LO004NestedStackCoverage().check(Repo(path=tmp_path, stacks=("python",)))
    assert result.passing is True


def test_lo004_pass_no_nested_markers(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text("[project]\n")
    result = LO004NestedStackCoverage().check(Repo(path=tmp_path, stacks=("python",)))
    assert result.passing is True


def test_lo004_metadata() -> None:
    rule = LO004NestedStackCoverage()
    assert rule.id == "LO004"
    assert rule.severity == "recommended"
    assert rule.stacks == ("*",)
