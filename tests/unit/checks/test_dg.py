"""Tests for transverse DG (docs & governance) rules."""

from pathlib import Path

from intendant.checks.dg import (
    DG001Readme,
    DG002CLAUDEmd,
    DG003ADRDir,
    DG004License,
    DG005SpecsLocalOnly,
    DG006VersionClaimsFresh,
)
from intendant.core.repo import Repo


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


# --- DG006: doc version claims match the release manifest ---


def _manifest(path: Path, version: str) -> None:
    (path / ".release-please-manifest.json").write_text(f'{{\n  ".": "{version}"\n}}\n')


def test_dg006_fail_stale_claude_md_claim(tmp_path: Path) -> None:
    """The champinium case: CLAUDE.md claims an old release."""
    _manifest(tmp_path, "0.6.0")
    (tmp_path / "CLAUDE.md").write_text("**Dernière release : v0.2.0** (release-please)\n")
    result = DG006VersionClaimsFresh().check(Repo(path=tmp_path, stacks=("rust",)))
    assert result.passing is False
    assert "v0.2.0" in result.evidence
    assert "0.6.0" in result.evidence


def test_dg006_fail_stale_readme_status_line(tmp_path: Path) -> None:
    """The intendant case: README status line pins an old version."""
    _manifest(tmp_path, "4.0.3")
    (tmp_path / "README.md").write_text("## Status\n\nv4.0.0 — stable. 83 rules.\n")
    result = DG006VersionClaimsFresh().check(Repo(path=tmp_path, stacks=("python",)))
    assert result.passing is False
    assert "v4.0.0" in result.evidence


def test_dg006_pass_matching_claim(tmp_path: Path) -> None:
    _manifest(tmp_path, "1.2.3")
    (tmp_path / "README.md").write_text("Last release v1.2.3.\n")
    assert DG006VersionClaimsFresh().check(Repo(path=tmp_path, stacks=("python",))).passing is True


def test_dg006_pass_no_claims(tmp_path: Path) -> None:
    _manifest(tmp_path, "1.2.3")
    (tmp_path / "README.md").write_text("A project. Uses libp2p 0.53.1 and uniffi v0.28.3.\n")
    assert DG006VersionClaimsFresh().check(Repo(path=tmp_path, stacks=("python",))).passing is True


def test_dg006_ignores_dependency_mentions(tmp_path: Path) -> None:
    """Bare `vX.Y.Z` tokens without a release/version/status context are not claims."""
    _manifest(tmp_path, "2.0.0")
    (tmp_path / "README.md").write_text("Pin actions like actions/checkout@abc  # v4.3.1\n")
    assert DG006VersionClaimsFresh().check(Repo(path=tmp_path, stacks=("python",))).passing is True


def test_dg006_skipped_without_manifest(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("Last release v1.0.0\n")
    result = DG006VersionClaimsFresh().check(Repo(path=tmp_path, stacks=("python",)))
    assert result.skipped is True


def test_dg006_metadata() -> None:
    rule = DG006VersionClaimsFresh()
    assert rule.id == "DG006"
    assert rule.severity == "optional"
    assert rule.stacks == ("*",)
