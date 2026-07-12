"""Tests for Rust adapter RUST_SA rules."""

from __future__ import annotations

from pathlib import Path

from intendant.adapters.rust.sa import RUST_SA001GitignoreBaseline, RUST_SA002CargoDenyAudit
from intendant.core.repo import Repo


def _repo(path: Path) -> Repo:
    return Repo(path=path, stacks=("rust",))


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


# --- RUST_SA002: dependency vulnerability / license scanning ---


def test_sa002_pass_deny_toml(tmp_path: Path) -> None:
    (tmp_path / "deny.toml").write_text("[advisories]\n")
    repo = Repo(path=tmp_path, stacks=("rust",))
    result = RUST_SA002CargoDenyAudit().check(repo)
    assert result.passing is True
    assert "deny.toml" in result.evidence


def test_sa002_pass_cargo_audit_in_ci(tmp_path: Path) -> None:
    wf = tmp_path / ".github" / "workflows"
    wf.mkdir(parents=True)
    (wf / "ci.yml").write_text("jobs:\n  audit:\n    steps:\n      - run: cargo audit\n")
    repo = Repo(path=tmp_path, stacks=("rust",))
    assert RUST_SA002CargoDenyAudit().check(repo).passing is True


def test_sa002_pass_deny_action_in_ci(tmp_path: Path) -> None:
    wf = tmp_path / ".github" / "workflows"
    wf.mkdir(parents=True)
    (wf / "ci.yml").write_text(
        "jobs:\n  deny:\n    steps:\n      - uses: EmbarkStudios/cargo-deny-action@v2\n"
    )
    repo = Repo(path=tmp_path, stacks=("rust",))
    assert RUST_SA002CargoDenyAudit().check(repo).passing is True


def test_sa002_fail(tmp_path: Path) -> None:
    repo = Repo(path=tmp_path, stacks=("rust",))
    result = RUST_SA002CargoDenyAudit().check(repo)
    assert result.passing is False
    assert "cargo-deny" in result.evidence or "cargo-audit" in result.evidence


def test_sa002_metadata() -> None:
    rule = RUST_SA002CargoDenyAudit()
    assert rule.id == "RUST_SA002"
    assert rule.severity == "recommended"
    assert "rust" in rule.stacks
