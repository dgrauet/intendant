"""Tests for RL (releases) transverse rules."""

import subprocess
from pathlib import Path

from intendant.checks.rl import (
    RL001Changelog,
    RL002ConventionalCommits,
    RL003ReleasePlease,
    RL004SemverStrict,
)
from intendant.core.repo import Repo


def _git_init(path: Path) -> None:
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=path, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=path, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=path, check=True)


def _git_commit(path: Path, message: str) -> None:
    subprocess.run(["git", "commit", "--allow-empty", "-q", "-m", message], cwd=path, check=True)


def test_rl001_pass(tmp_path: Path) -> None:
    (tmp_path / "CHANGELOG.md").write_text(
        "# Changelog\n\nAll notable changes...\n\n## [Unreleased]\n"
    )
    repo = Repo(path=tmp_path, stacks=("python",))
    assert RL001Changelog().check(repo).passing is True


def test_rl001_fail_no_file(tmp_path: Path) -> None:
    repo = Repo(path=tmp_path, stacks=("python",))
    result = RL001Changelog().check(repo)
    assert result.passing is False


def test_rl001_fail_wrong_format(tmp_path: Path) -> None:
    (tmp_path / "CHANGELOG.md").write_text("Random unstructured changelog\n")
    repo = Repo(path=tmp_path, stacks=("python",))
    result = RL001Changelog().check(repo)
    assert result.passing is False
    assert "format" in result.evidence.lower()


def test_rl001_fix_creates_skeleton(tmp_path: Path) -> None:
    repo = Repo(path=tmp_path, stacks=("python",))
    rule = RL001Changelog()
    patch = rule.fix(repo, rule.check(repo))
    assert patch is not None
    assert "Keep a Changelog" in patch.content


def test_rl002_pass_with_conv_commits(tmp_path: Path) -> None:
    _git_init(tmp_path)
    _git_commit(tmp_path, "feat: add thing")
    _git_commit(tmp_path, "fix: address issue")
    _git_commit(tmp_path, "chore: bump deps")
    repo = Repo(path=tmp_path, stacks=("python",))
    assert RL002ConventionalCommits().check(repo).passing is True


def test_rl002_fail_with_non_conv_commits(tmp_path: Path) -> None:
    _git_init(tmp_path)
    _git_commit(tmp_path, "feat: add thing")
    _git_commit(tmp_path, "did some random stuff")
    repo = Repo(path=tmp_path, stacks=("python",))
    result = RL002ConventionalCommits().check(repo)
    assert result.passing is False
    assert "did some random stuff" in result.evidence


def test_rl002_skip_no_git(tmp_path: Path) -> None:
    """If the repo isn't git-initialized, this rule reports skip-like evidence."""
    repo = Repo(path=tmp_path, stacks=("python",))
    result = RL002ConventionalCommits().check(repo)
    # Not a hard fail; accept passing or fail-with-clear-evidence
    assert "not a git repo" in result.evidence.lower() or "no git" in result.evidence.lower()


def test_rl002_accepts_release_type(tmp_path: Path) -> None:
    """release-please uses `release:` as a commit type — it must pass."""
    _git_init(tmp_path)
    _git_commit(tmp_path, "feat: initial")
    _git_commit(tmp_path, "release: 1.0.0")
    repo = Repo(path=tmp_path, stacks=("python",))
    assert RL002ConventionalCommits().check(repo).passing is True


def test_rl002_accepts_custom_type(tmp_path: Path) -> None:
    """Any lowercase [a-z]+ type is valid CC 1.0."""
    _git_init(tmp_path)
    _git_commit(tmp_path, "feat: initial")
    _git_commit(tmp_path, "deps: bump foo")
    repo = Repo(path=tmp_path, stacks=("python",))
    assert RL002ConventionalCommits().check(repo).passing is True


def test_rl002_still_rejects_garbage(tmp_path: Path) -> None:
    _git_init(tmp_path)
    _git_commit(tmp_path, "feat: initial")
    _git_commit(tmp_path, "Random text without colon")
    repo = Repo(path=tmp_path, stacks=("python",))
    assert RL002ConventionalCommits().check(repo).passing is False


# ---------------------------------------------------------------------------
# RL003ReleasePlease
# ---------------------------------------------------------------------------


def _write_release_please_files(tmp_path: Path) -> None:
    (tmp_path / "release-please-config.json").write_text('{"packages": {".": {}}}\n')
    (tmp_path / ".release-please-manifest.json").write_text('{".": "0.1.0"}\n')


def test_rl003_pass(tmp_path: Path) -> None:
    _write_release_please_files(tmp_path)
    repo = Repo(path=tmp_path, stacks=("python",))
    assert RL003ReleasePlease().check(repo).passing is True


def test_rl003_fail_no_config(tmp_path: Path) -> None:
    (tmp_path / ".release-please-manifest.json").write_text('{".": "0.1.0"}\n')
    repo = Repo(path=tmp_path, stacks=("python",))
    result = RL003ReleasePlease().check(repo)
    assert result.passing is False
    assert "release-please-config.json" in result.evidence


def test_rl003_fail_no_manifest(tmp_path: Path) -> None:
    (tmp_path / "release-please-config.json").write_text('{"packages": {".": {}}}\n')
    repo = Repo(path=tmp_path, stacks=("python",))
    result = RL003ReleasePlease().check(repo)
    assert result.passing is False
    assert ".release-please-manifest.json" in result.evidence


def test_rl003_fail_both_missing(tmp_path: Path) -> None:
    repo = Repo(path=tmp_path, stacks=("python",))
    result = RL003ReleasePlease().check(repo)
    assert result.passing is False


def test_rl003_metadata() -> None:
    rule = RL003ReleasePlease()
    assert rule.id == "RL003"
    assert rule.severity == "required"
    assert "*" in rule.stacks


# ---------------------------------------------------------------------------
# RL003 .fix() tests
# ---------------------------------------------------------------------------


def _write_pyproject(tmp_path: Path, name: str = "my-package", version: str = "1.2.3") -> None:
    (tmp_path / "pyproject.toml").write_text(f'[project]\nname = "{name}"\nversion = "{version}"\n')


def test_rl003_fix_creates_manifest_first(tmp_path: Path) -> None:
    """Neither file exists, pyproject has name+version → fix creates manifest."""
    _write_pyproject(tmp_path, name="my-package", version="1.2.3")
    repo = Repo(path=tmp_path, stacks=("python",))
    rule = RL003ReleasePlease()
    result = rule.check(repo)
    assert result.passing is False
    patch = rule.fix(repo, result)
    assert patch is not None
    assert patch.target_path.name == ".release-please-manifest.json"
    assert patch.kind == "create"
    assert "1.2.3" in patch.content
    assert patch.safe is True


def test_rl003_fix_creates_config_when_manifest_exists(tmp_path: Path) -> None:
    """Manifest exists, config missing → fix creates config with correct package name."""
    _write_pyproject(tmp_path, name="my-package", version="1.2.3")
    (tmp_path / ".release-please-manifest.json").write_text('{".": "1.2.3"}\n')
    repo = Repo(path=tmp_path, stacks=("python",))
    rule = RL003ReleasePlease()
    result = rule.check(repo)
    assert result.passing is False
    patch = rule.fix(repo, result)
    assert patch is not None
    assert patch.target_path.name == "release-please-config.json"
    assert patch.kind == "create"
    assert "my-package" in patch.content
    assert patch.safe is True


def test_rl003_fix_returns_none_without_pyproject(tmp_path: Path) -> None:
    """No pyproject.toml → fix returns None."""
    repo = Repo(path=tmp_path, stacks=("python",))
    rule = RL003ReleasePlease()
    result = rule.check(repo)
    assert result.passing is False
    patch = rule.fix(repo, result)
    assert patch is None


def test_rl003_fix_returns_none_without_project_name(tmp_path: Path) -> None:
    """pyproject.toml without [project].name → fix returns None."""
    (tmp_path / "pyproject.toml").write_text('[build-system]\nrequires = ["setuptools"]\n')
    repo = Repo(path=tmp_path, stacks=("python",))
    rule = RL003ReleasePlease()
    result = rule.check(repo)
    assert result.passing is False
    patch = rule.fix(repo, result)
    assert patch is None


# ---------------------------------------------------------------------------
# RL004SemverStrict
# ---------------------------------------------------------------------------


def test_rl004_skipped_when_no_manifest(tmp_path: Path) -> None:
    repo = Repo(path=tmp_path, stacks=("python",))
    result = RL004SemverStrict().check(repo)
    assert result.passing is True
    assert result.skipped is True


def test_rl004_passes_for_valid_semver_from_pyproject(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "x"\nversion = "1.0.0"\n')
    repo = Repo(path=tmp_path, stacks=("python",))
    result = RL004SemverStrict().check(repo)
    assert result.passing is True
    assert "1.0.0" in result.evidence


def test_rl004_passes_for_semver_with_prerelease_and_build(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "x"\nversion = "1.2.3-beta.1+build.5"\n'
    )
    repo = Repo(path=tmp_path, stacks=("python",))
    assert RL004SemverStrict().check(repo).passing is True


def test_rl004_fails_for_partial_version(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "x"\nversion = "1.0"\n')
    repo = Repo(path=tmp_path, stacks=("python",))
    result = RL004SemverStrict().check(repo)
    assert result.passing is False
    assert "1.0" in result.evidence


def test_rl004_fails_for_v_prefixed_version(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "x"\nversion = "v1.0.0"\n')
    repo = Repo(path=tmp_path, stacks=("python",))
    result = RL004SemverStrict().check(repo)
    assert result.passing is False
    assert "v1.0.0" in result.evidence


def test_rl004_reads_version_from_release_please_manifest(tmp_path: Path) -> None:
    (tmp_path / ".release-please-manifest.json").write_text('{".": "1.2.3"}\n')
    repo = Repo(path=tmp_path, stacks=("claude-skill",))
    result = RL004SemverStrict().check(repo)
    assert result.passing is True
    assert "1.2.3" in result.evidence


def test_rl004_release_please_manifest_invalid_semver_fails(tmp_path: Path) -> None:
    (tmp_path / ".release-please-manifest.json").write_text('{".": "v1.0"}\n')
    repo = Repo(path=tmp_path, stacks=("claude-skill",))
    result = RL004SemverStrict().check(repo)
    assert result.passing is False
    assert "v1.0" in result.evidence
