"""Tests for SA (sanitizing) transverse rules."""

from pathlib import Path

from suzerain.checks.sa import SA001PreCommit, SA002Gitleaks, SA004GitignoreBaseline
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
