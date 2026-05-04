"""Tests for Rust adapter RUST_TS rules."""

from __future__ import annotations

from pathlib import Path

from suzerain.adapters.rust.ts import RustTestAnnotations
from suzerain.core.repo import Repo


def _repo(path: Path) -> Repo:
    return Repo(path=path, stack="rust")


def test_ts001_pass_with_inline_test(tmp_path: Path) -> None:
    src = tmp_path / "src"
    src.mkdir()
    (src / "lib.rs").write_text("#[test]\nfn it_works() {}\n")
    result = RustTestAnnotations().check(_repo(tmp_path))
    assert result.passing is True
    assert "lib.rs" in result.evidence


def test_ts001_pass_with_integration_test(tmp_path: Path) -> None:
    tests = tmp_path / "tests"
    tests.mkdir()
    (tests / "integration.rs").write_text("#[test]\nfn smoke() {}\n")
    assert RustTestAnnotations().check(_repo(tmp_path)).passing is True


def test_ts001_fail_no_tests(tmp_path: Path) -> None:
    src = tmp_path / "src"
    src.mkdir()
    (src / "lib.rs").write_text("pub fn add(a: i32, b: i32) -> i32 { a + b }\n")
    result = RustTestAnnotations().check(_repo(tmp_path))
    assert result.passing is False


def test_ts001_fail_when_no_dirs(tmp_path: Path) -> None:
    assert RustTestAnnotations().check(_repo(tmp_path)).passing is False


def test_ts001_metadata() -> None:
    rule = RustTestAnnotations()
    assert rule.id == "RUST_TS001"
    assert rule.severity == "recommended"
