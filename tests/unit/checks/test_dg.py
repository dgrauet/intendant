"""Tests for transverse DG (docs & governance) rules."""

from pathlib import Path

from suzerain.checks.dg import (
    DG001Readme,
    DG002CLAUDEmd,
    DG003ADRDir,
    DG004License,
    DG005SpecsLocalOnly,
)
from suzerain.core.repo import Repo


def _setup_repo(tmp_path: Path) -> Repo:
    return Repo(path=tmp_path, stacks=("python",))


def test_dg001_pass(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("# project\n")
    repo = _setup_repo(tmp_path)
    result = DG001Readme().check(repo)
    assert result.passing is True


def test_dg001_fail(tmp_path: Path) -> None:
    repo = _setup_repo(tmp_path)
    result = DG001Readme().check(repo)
    assert result.passing is False
    assert "README" in result.evidence


def test_dg001_fix_creates_skeleton(tmp_path: Path) -> None:
    repo = _setup_repo(tmp_path)
    rule = DG001Readme()
    result = rule.check(repo)
    patch = rule.fix(repo, result)
    assert patch is not None
    assert patch.kind == "create"
    assert patch.target_path == tmp_path / "README.md"


def test_dg003_pass(tmp_path: Path) -> None:
    (tmp_path / "docs" / "adr").mkdir(parents=True)
    (tmp_path / "docs" / "adr" / "0001-test.md").write_text("# ADR-0001\n")
    repo = _setup_repo(tmp_path)
    assert DG003ADRDir().check(repo).passing is True


def test_dg003_fail_no_dir(tmp_path: Path) -> None:
    repo = _setup_repo(tmp_path)
    result = DG003ADRDir().check(repo)
    assert result.passing is False


def test_dg003_fail_empty_dir(tmp_path: Path) -> None:
    (tmp_path / "docs" / "adr").mkdir(parents=True)
    repo = _setup_repo(tmp_path)
    result = DG003ADRDir().check(repo)
    assert result.passing is False
    assert "no ADRs" in result.evidence.lower() or "empty" in result.evidence.lower()


def test_dg004_pass(tmp_path: Path) -> None:
    (tmp_path / "LICENSE").write_text("MIT\n")
    repo = _setup_repo(tmp_path)
    assert DG004License().check(repo).passing is True


def test_dg004_fail(tmp_path: Path) -> None:
    repo = _setup_repo(tmp_path)
    result = DG004License().check(repo)
    assert result.passing is False


def test_dg005_pass_when_no_specs_dir(tmp_path: Path) -> None:
    repo = _setup_repo(tmp_path)
    assert DG005SpecsLocalOnly().check(repo).passing is True


def test_dg005_pass_when_both_protect(tmp_path: Path) -> None:
    (tmp_path / "docs" / "superpowers").mkdir(parents=True)
    (tmp_path / ".gitignore").write_text("docs/superpowers/\n")
    (tmp_path / ".gitattributes").write_text("docs/superpowers/ export-ignore\n")
    repo = _setup_repo(tmp_path)
    assert DG005SpecsLocalOnly().check(repo).passing is True


def test_dg005_fail_when_specs_present_without_protection(tmp_path: Path) -> None:
    (tmp_path / "docs" / "superpowers" / "specs").mkdir(parents=True)
    repo = _setup_repo(tmp_path)
    result = DG005SpecsLocalOnly().check(repo)
    assert result.passing is False
    assert ".gitignore" in result.evidence
    assert ".gitattributes" in result.evidence


def test_dg005_fix_writes_gitignore_first(tmp_path: Path) -> None:
    (tmp_path / "docs" / "superpowers").mkdir(parents=True)
    repo = _setup_repo(tmp_path)
    rule = DG005SpecsLocalOnly()
    patch = rule.fix(repo, rule.check(repo))
    assert patch is not None
    assert patch.target_path == tmp_path / ".gitignore"


def test_dg005_fail_when_only_gitignore_protects(tmp_path: Path) -> None:
    (tmp_path / "docs" / "superpowers").mkdir(parents=True)
    (tmp_path / ".gitignore").write_text("docs/superpowers/\n")
    repo = _setup_repo(tmp_path)
    result = DG005SpecsLocalOnly().check(repo)
    assert result.passing is False
    assert ".gitattributes" in result.evidence
    assert ".gitignore" not in result.evidence


def test_dg005_fail_when_only_gitattributes_protects(tmp_path: Path) -> None:
    (tmp_path / "docs" / "superpowers").mkdir(parents=True)
    (tmp_path / ".gitattributes").write_text("docs/superpowers/ export-ignore\n")
    repo = _setup_repo(tmp_path)
    result = DG005SpecsLocalOnly().check(repo)
    assert result.passing is False
    assert ".gitignore" in result.evidence
    assert ".gitattributes" not in result.evidence


def test_dg005_fix_second_pass_writes_gitattributes(tmp_path: Path) -> None:
    (tmp_path / "docs" / "superpowers").mkdir(parents=True)
    # .gitignore already protects; second pass should fix .gitattributes
    (tmp_path / ".gitignore").write_text("docs/superpowers/\n")
    repo = _setup_repo(tmp_path)
    rule = DG005SpecsLocalOnly()
    patch = rule.fix(repo, rule.check(repo))
    assert patch is not None
    assert patch.target_path == tmp_path / ".gitattributes"


def test_dg005_fix_returns_none_when_both_protect(tmp_path: Path) -> None:
    (tmp_path / "docs" / "superpowers").mkdir(parents=True)
    (tmp_path / ".gitignore").write_text("docs/superpowers/\n")
    (tmp_path / ".gitattributes").write_text("docs/superpowers/ export-ignore\n")
    repo = _setup_repo(tmp_path)
    rule = DG005SpecsLocalOnly()
    patch = rule.fix(repo, rule.check(repo))
    assert patch is None


def test_dg005_fix_idempotent_when_gitignore_already_has_substring(tmp_path: Path) -> None:
    (tmp_path / "docs" / "superpowers").mkdir(parents=True)
    # .gitignore already contains docs/superpowers/ in some context
    (tmp_path / ".gitignore").write_text("# already excluded\ndocs/superpowers/something-else\n")
    (tmp_path / ".gitattributes").write_text("docs/superpowers/ export-ignore\n")
    repo = _setup_repo(tmp_path)
    rule = DG005SpecsLocalOnly()
    # Both protect (substring match), so fix should return None
    patch = rule.fix(repo, rule.check(repo))
    assert patch is None


# ---------------------------------------------------------------------------
# DG002CLAUDEmd
# ---------------------------------------------------------------------------


def test_dg002_pass(tmp_path: Path) -> None:
    (tmp_path / "CLAUDE.md").write_text("# CLAUDE.md\n")
    repo = _setup_repo(tmp_path)
    assert DG002CLAUDEmd().check(repo).passing is True


def test_dg002_fail(tmp_path: Path) -> None:
    repo = _setup_repo(tmp_path)
    result = DG002CLAUDEmd().check(repo)
    assert result.passing is False
    assert "CLAUDE.md" in result.evidence


def test_dg002_metadata(tmp_path: Path) -> None:
    rule = DG002CLAUDEmd()
    assert rule.id == "DG002"
    assert rule.severity == "recommended"
    assert "*" in rule.stacks
