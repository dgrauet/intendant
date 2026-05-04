"""Tests for Swift adapter SWIFT_QU/TS/SA rules."""

from __future__ import annotations

from pathlib import Path

from suzerain.adapters.swift.qu import SwiftLinter
from suzerain.adapters.swift.sa import SWIFT_SA001GitignoreBaseline
from suzerain.adapters.swift.ts import SwiftTestFiles
from suzerain.core.repo import Repo


def _repo(path: Path) -> Repo:
    return Repo(path=path, stack="swift")


def test_qu001_pass_swiftlint(tmp_path: Path) -> None:
    (tmp_path / ".swiftlint.yml").write_text("disabled_rules:\n  - line_length\n")
    result = SwiftLinter().check(_repo(tmp_path))
    assert result.passing is True
    assert ".swiftlint.yml" in result.evidence


def test_qu001_pass_swiftformat(tmp_path: Path) -> None:
    (tmp_path / ".swiftformat").write_text("--swiftversion 5.9\n")
    assert SwiftLinter().check(_repo(tmp_path)).passing is True


def test_qu001_fail(tmp_path: Path) -> None:
    result = SwiftLinter().check(_repo(tmp_path))
    assert result.passing is False
    assert "swiftlint" in result.evidence


def test_qu001_metadata() -> None:
    rule = SwiftLinter()
    assert rule.id == "SWIFT_QU001"
    assert rule.severity == "recommended"


def test_ts001_pass(tmp_path: Path) -> None:
    test_dir = tmp_path / "Tests" / "MyLibTests"
    test_dir.mkdir(parents=True)
    (test_dir / "MyLibTests.swift").write_text("class T: XCTestCase { func testFoo() {} }\n")
    result = SwiftTestFiles().check(_repo(tmp_path))
    assert result.passing is True


def test_ts001_fail(tmp_path: Path) -> None:
    result = SwiftTestFiles().check(_repo(tmp_path))
    assert result.passing is False


def test_ts001_metadata() -> None:
    rule = SwiftTestFiles()
    assert rule.id == "SWIFT_TS001"
    assert rule.severity == "recommended"


def test_sa001_pass(tmp_path: Path) -> None:
    (tmp_path / ".gitignore").write_text(".build/\nxcuserdata/\n")
    assert SWIFT_SA001GitignoreBaseline().check(_repo(tmp_path)).passing is True


def test_sa001_fail_missing_pattern(tmp_path: Path) -> None:
    (tmp_path / ".gitignore").write_text(".build/\n")
    result = SWIFT_SA001GitignoreBaseline().check(_repo(tmp_path))
    assert result.passing is False
    assert "xcuserdata" in result.evidence


def test_sa001_skipped_when_no_gitignore(tmp_path: Path) -> None:
    result = SWIFT_SA001GitignoreBaseline().check(_repo(tmp_path))
    assert result.skipped is True


def test_sa001_metadata() -> None:
    rule = SWIFT_SA001GitignoreBaseline()
    assert rule.id == "SWIFT_SA001"
    assert rule.severity == "required"
