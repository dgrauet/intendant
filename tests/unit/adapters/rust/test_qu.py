"""Tests for Rust adapter RUST_QU rules."""

from __future__ import annotations

from pathlib import Path

from suzerain.adapters.rust.qu import RustToolchainPin
from suzerain.core.repo import Repo


def _repo(path: Path) -> Repo:
    return Repo(path=path, stack="rust")


def test_qu001_pass_with_toml(tmp_path: Path) -> None:
    (tmp_path / "rust-toolchain.toml").write_text('[toolchain]\nchannel = "stable"\n')
    assert RustToolchainPin().check(_repo(tmp_path)).passing is True


def test_qu001_pass_with_legacy_file(tmp_path: Path) -> None:
    (tmp_path / "rust-toolchain").write_text("stable\n")
    assert RustToolchainPin().check(_repo(tmp_path)).passing is True


def test_qu001_fail_missing(tmp_path: Path) -> None:
    result = RustToolchainPin().check(_repo(tmp_path))
    assert result.passing is False
    assert "rust-toolchain" in result.evidence


def test_qu001_metadata() -> None:
    rule = RustToolchainPin()
    assert rule.id == "RUST_QU001"
    assert rule.severity == "recommended"
