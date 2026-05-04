"""Tests for Rust adapter RUST_SA rules."""

from __future__ import annotations

from pathlib import Path

from suzerain.adapters.rust.sa import RUST_SA001GitignoreBaseline
from suzerain.core.repo import Repo


def _repo(path: Path) -> Repo:
    return Repo(path=path, stack="rust")


def test_sa001_pass(tmp_path: Path) -> None:
    (tmp_path / ".gitignore").write_text("target/\n.DS_Store\n")
    assert RUST_SA001GitignoreBaseline().check(_repo(tmp_path)).passing is True


def test_sa001_fail_missing_target(tmp_path: Path) -> None:
    (tmp_path / ".gitignore").write_text(".DS_Store\n")
    result = RUST_SA001GitignoreBaseline().check(_repo(tmp_path))
    assert result.passing is False
    assert "target/" in result.evidence


def test_sa001_skipped_when_gitignore_missing(tmp_path: Path) -> None:
    result = RUST_SA001GitignoreBaseline().check(_repo(tmp_path))
    assert result.skipped is True


def test_sa001_metadata() -> None:
    rule = RUST_SA001GitignoreBaseline()
    assert rule.id == "RUST_SA001"
    assert rule.severity == "required"
