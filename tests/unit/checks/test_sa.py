"""Tests for SA (sanitizing) transverse rules."""

from pathlib import Path

from suzerain.checks.sa import (
    SA001PreCommit,
    SA002Gitleaks,
    SA003EnvExample,
    SA004GitignoreBaseline,
)
from suzerain.core.repo import Repo


def _write_minimal_precommit(tmp_path: Path) -> None:
    (tmp_path / ".pre-commit-config.yaml").write_text(
        "repos:\n"
        "  - repo: https://github.com/pre-commit/pre-commit-hooks\n"
        "    rev: v5.0.0\n"
        "    hooks:\n"
        "      - id: trailing-whitespace\n"
        "      - id: end-of-file-fixer\n"
        "      - id: check-yaml\n"
    )


def test_sa001_pass(tmp_path: Path) -> None:
    _write_minimal_precommit(tmp_path)
    repo = Repo(path=tmp_path, stack="python")
    assert SA001PreCommit().check(repo).passing is True


def test_sa001_fail_no_config(tmp_path: Path) -> None:
    repo = Repo(path=tmp_path, stack="python")
    result = SA001PreCommit().check(repo)
    assert result.passing is False


def test_sa001_fail_missing_minimum_hooks(tmp_path: Path) -> None:
    (tmp_path / ".pre-commit-config.yaml").write_text(
        "repos:\n"
        "  - repo: https://github.com/pre-commit/pre-commit-hooks\n"
        "    rev: v5.0.0\n"
        "    hooks:\n"
        "      - id: trailing-whitespace\n"
        # missing end-of-file-fixer and check-yaml
    )
    repo = Repo(path=tmp_path, stack="python")
    result = SA001PreCommit().check(repo)
    assert result.passing is False
    assert "end-of-file-fixer" in result.evidence or "check-yaml" in result.evidence


# ---------------------------------------------------------------------------
# SA002Gitleaks
# ---------------------------------------------------------------------------


def _write_precommit_with_gitleaks(tmp_path: Path) -> None:
    (tmp_path / ".pre-commit-config.yaml").write_text(
        "repos:\n"
        "  - repo: https://github.com/gitleaks/gitleaks\n"
        "    rev: v8.21.0\n"
        "    hooks:\n"
        "      - id: gitleaks\n"
    )


def test_sa002_pass(tmp_path: Path) -> None:
    _write_precommit_with_gitleaks(tmp_path)
    repo = Repo(path=tmp_path, stack="python")
    assert SA002Gitleaks().check(repo).passing is True


def test_sa002_fail_no_config(tmp_path: Path) -> None:
    repo = Repo(path=tmp_path, stack="python")
    result = SA002Gitleaks().check(repo)
    assert result.passing is False
    assert "pre-commit-config.yaml" in result.evidence


def test_sa002_fail_no_gitleaks(tmp_path: Path) -> None:
    (tmp_path / ".pre-commit-config.yaml").write_text(
        "repos:\n"
        "  - repo: https://github.com/pre-commit/pre-commit-hooks\n"
        "    rev: v5.0.0\n"
        "    hooks:\n"
        "      - id: trailing-whitespace\n"
    )
    repo = Repo(path=tmp_path, stack="python")
    result = SA002Gitleaks().check(repo)
    assert result.passing is False
    assert "gitleaks" in result.evidence.lower()


def test_sa002_metadata() -> None:
    rule = SA002Gitleaks()
    assert rule.id == "SA002"
    assert rule.severity == "required"
    assert "*" in rule.stacks


# ---------------------------------------------------------------------------
# SA004GitignoreBaseline
# ---------------------------------------------------------------------------


_BASELINE_CONTENT = "__pycache__/\n.DS_Store\n.venv/\n"


def test_sa004_pass(tmp_path: Path) -> None:
    (tmp_path / ".gitignore").write_text(_BASELINE_CONTENT)
    repo = Repo(path=tmp_path, stack="python")
    assert SA004GitignoreBaseline().check(repo).passing is True


def test_sa004_fail_no_gitignore(tmp_path: Path) -> None:
    repo = Repo(path=tmp_path, stack="python")
    result = SA004GitignoreBaseline().check(repo)
    assert result.passing is False
    assert ".gitignore" in result.evidence


def test_sa004_fail_missing_pycache(tmp_path: Path) -> None:
    (tmp_path / ".gitignore").write_text(".DS_Store\n.venv/\n")
    repo = Repo(path=tmp_path, stack="python")
    result = SA004GitignoreBaseline().check(repo)
    assert result.passing is False
    assert "__pycache__/" in result.evidence


def test_sa004_fail_missing_ds_store(tmp_path: Path) -> None:
    (tmp_path / ".gitignore").write_text("__pycache__/\n.venv/\n")
    repo = Repo(path=tmp_path, stack="python")
    result = SA004GitignoreBaseline().check(repo)
    assert result.passing is False
    assert ".DS_Store" in result.evidence


def test_sa004_fail_missing_venv(tmp_path: Path) -> None:
    (tmp_path / ".gitignore").write_text("__pycache__/\n.DS_Store\n")
    repo = Repo(path=tmp_path, stack="python")
    result = SA004GitignoreBaseline().check(repo)
    assert result.passing is False
    assert ".venv/" in result.evidence


def test_sa004_metadata() -> None:
    rule = SA004GitignoreBaseline()
    assert rule.id == "SA004"
    assert rule.severity == "required"
    assert "*" in rule.stacks


# ---------------------------------------------------------------------------
# SA001 .fix() tests
# ---------------------------------------------------------------------------


def test_sa001_fix_creates_file_when_missing(tmp_path: Path) -> None:
    repo = Repo(path=tmp_path, stack="python")
    rule = SA001PreCommit()
    result = rule.check(repo)
    assert result.passing is False
    patch = rule.fix(repo, result)
    assert patch is not None
    assert patch.kind == "create"
    assert "trailing-whitespace" in patch.content
    assert "end-of-file-fixer" in patch.content
    assert "check-yaml" in patch.content
    assert patch.safe is True


def test_sa001_fix_appends_when_no_pre_commit_hooks_repo(tmp_path: Path) -> None:
    (tmp_path / ".pre-commit-config.yaml").write_text(
        "repos:\n"
        "  - repo: https://github.com/astral-sh/ruff-pre-commit\n"
        "    rev: v0.9.0\n"
        "    hooks:\n"
        "      - id: ruff\n"
    )
    repo = Repo(path=tmp_path, stack="python")
    rule = SA001PreCommit()
    result = rule.check(repo)
    assert result.passing is False
    patch = rule.fix(repo, result)
    assert patch is not None
    assert patch.kind == "overwrite"
    assert "pre-commit/pre-commit-hooks" in patch.content
    assert "trailing-whitespace" in patch.content
    assert patch.safe is True


def test_sa001_fix_returns_none_when_pre_commit_hooks_partially_declared(tmp_path: Path) -> None:
    # pre-commit-hooks repo is declared but missing some baseline hooks — too risky to merge
    (tmp_path / ".pre-commit-config.yaml").write_text(
        "repos:\n"
        "  - repo: https://github.com/pre-commit/pre-commit-hooks\n"
        "    rev: v5.0.0\n"
        "    hooks:\n"
        "      - id: trailing-whitespace\n"
        # missing end-of-file-fixer and check-yaml
    )
    repo = Repo(path=tmp_path, stack="python")
    rule = SA001PreCommit()
    result = rule.check(repo)
    assert result.passing is False
    patch = rule.fix(repo, result)
    assert patch is None


# ---------------------------------------------------------------------------
# SA002 .fix() tests
# ---------------------------------------------------------------------------


def test_sa002_fix_creates_file_when_missing(tmp_path: Path) -> None:
    repo = Repo(path=tmp_path, stack="python")
    rule = SA002Gitleaks()
    result = rule.check(repo)
    assert result.passing is False
    patch = rule.fix(repo, result)
    assert patch is not None
    assert patch.kind == "create"
    assert "gitleaks" in patch.content
    assert patch.safe is True


def test_sa002_fix_appends_when_no_gitleaks_repo(tmp_path: Path) -> None:
    (tmp_path / ".pre-commit-config.yaml").write_text(
        "repos:\n"
        "  - repo: https://github.com/pre-commit/pre-commit-hooks\n"
        "    rev: v5.0.0\n"
        "    hooks:\n"
        "      - id: trailing-whitespace\n"
    )
    repo = Repo(path=tmp_path, stack="python")
    rule = SA002Gitleaks()
    result = rule.check(repo)
    assert result.passing is False
    patch = rule.fix(repo, result)
    assert patch is not None
    assert patch.kind == "overwrite"
    assert "gitleaks" in patch.content
    assert patch.safe is True


# ---------------------------------------------------------------------------
# SA003EnvExample
# ---------------------------------------------------------------------------


def test_sa003_skipped_when_no_env_artifact(tmp_path: Path) -> None:
    repo = Repo(path=tmp_path, stack="python")
    result = SA003EnvExample().check(repo)
    assert result.passing is True
    assert result.skipped is True


def test_sa003_fails_when_env_present_and_example_missing(tmp_path: Path) -> None:
    (tmp_path / ".env").write_text("SECRET=hunter2\n")
    repo = Repo(path=tmp_path, stack="python")
    result = SA003EnvExample().check(repo)
    assert result.passing is False
    assert ".env.example" in result.evidence


def test_sa003_passes_when_both_env_and_example_present(tmp_path: Path) -> None:
    (tmp_path / ".env").write_text("SECRET=hunter2\n")
    (tmp_path / ".env.example").write_text("SECRET=\n")
    repo = Repo(path=tmp_path, stack="python")
    result = SA003EnvExample().check(repo)
    assert result.passing is True


def test_sa003_fails_when_dotenv_dep_and_example_missing(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "x"\ndependencies = ["python-dotenv>=1.0"]\n'
    )
    repo = Repo(path=tmp_path, stack="python")
    result = SA003EnvExample().check(repo)
    assert result.passing is False
    assert ".env.example" in result.evidence


def test_sa003_fix_creates_env_example(tmp_path: Path) -> None:
    (tmp_path / ".env").write_text("SECRET=hunter2\n")
    repo = Repo(path=tmp_path, stack="python")
    rule = SA003EnvExample()
    result = rule.check(repo)
    assert result.passing is False
    patch = rule.fix(repo, result)
    assert patch is not None
    assert patch.kind == "create"
    assert patch.target_path == tmp_path / ".env.example"
    assert patch.safe is True
    assert "Document expected" in patch.content


def test_sa003_fix_returns_none_when_already_present(tmp_path: Path) -> None:
    (tmp_path / ".env").write_text("SECRET=hunter2\n")
    (tmp_path / ".env.example").write_text("SECRET=\n")
    repo = Repo(path=tmp_path, stack="python")
    rule = SA003EnvExample()
    result = rule.check(repo)
    assert result.passing is True
    patch = rule.fix(repo, result)
    assert patch is None
