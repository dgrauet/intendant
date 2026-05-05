"""Tests for Rust adapter RUST_PK rules."""

from __future__ import annotations

from pathlib import Path

from intendant.adapters.rust.pk import RustCargoLock, RustCargoToml, RustEdition
from intendant.core.repo import Repo


def _repo(path: Path) -> Repo:
    return Repo(path=path, stacks=("rust",))


def test_pk001_pass_with_package(tmp_path: Path) -> None:
    (tmp_path / "Cargo.toml").write_text('[package]\nname = "x"\nversion = "0.1.0"\n')
    assert RustCargoToml().check(_repo(tmp_path)).passing is True


def test_pk001_pass_with_workspace(tmp_path: Path) -> None:
    (tmp_path / "Cargo.toml").write_text('[workspace]\nmembers = ["a"]\n')
    assert RustCargoToml().check(_repo(tmp_path)).passing is True


def test_pk001_fail_missing(tmp_path: Path) -> None:
    result = RustCargoToml().check(_repo(tmp_path))
    assert result.passing is False
    assert "Cargo.toml" in result.evidence


def test_pk001_fail_no_package_or_workspace(tmp_path: Path) -> None:
    (tmp_path / "Cargo.toml").write_text("# orphan\n[dependencies]\n")
    result = RustCargoToml().check(_repo(tmp_path))
    assert result.passing is False
    assert "package" in result.evidence and "workspace" in result.evidence


def test_pk001_fail_unparseable(tmp_path: Path) -> None:
    (tmp_path / "Cargo.toml").write_text("not valid toml { [")
    result = RustCargoToml().check(_repo(tmp_path))
    assert result.passing is False
    assert "unparseable" in result.evidence


def test_pk001_metadata() -> None:
    rule = RustCargoToml()
    assert rule.id == "RUST_PK001"
    assert rule.severity == "required"
    assert "rust" in rule.stacks


def test_pk002_pass(tmp_path: Path) -> None:
    (tmp_path / "Cargo.lock").write_text("# generated\n")
    assert RustCargoLock().check(_repo(tmp_path)).passing is True


def test_pk002_fail_missing(tmp_path: Path) -> None:
    result = RustCargoLock().check(_repo(tmp_path))
    assert result.passing is False
    assert "Cargo.lock" in result.evidence


def test_pk003_pass(tmp_path: Path) -> None:
    (tmp_path / "Cargo.toml").write_text('[package]\nname = "x"\nedition = "2021"\n')
    result = RustEdition().check(_repo(tmp_path))
    assert result.passing is True
    assert "2021" in result.evidence


def test_pk003_fail_no_edition(tmp_path: Path) -> None:
    (tmp_path / "Cargo.toml").write_text('[package]\nname = "x"\nversion = "0.1.0"\n')
    result = RustEdition().check(_repo(tmp_path))
    assert result.passing is False
    assert "edition" in result.evidence


def test_pk003_skipped_when_cargo_missing(tmp_path: Path) -> None:
    result = RustEdition().check(_repo(tmp_path))
    assert result.skipped is True


def test_pk003_skipped_when_no_package_section(tmp_path: Path) -> None:
    (tmp_path / "Cargo.toml").write_text("[workspace]\nmembers = []\n")
    result = RustEdition().check(_repo(tmp_path))
    assert result.skipped is True


def test_pk003_metadata() -> None:
    rule = RustEdition()
    assert rule.id == "RUST_PK003"
    assert rule.severity == "recommended"
