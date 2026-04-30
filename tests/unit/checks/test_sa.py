"""Tests for SA (sanitizing) transverse rules."""

from pathlib import Path

from suzerain.checks.sa import SA001PreCommit
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
