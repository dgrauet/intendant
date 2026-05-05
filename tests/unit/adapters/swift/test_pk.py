"""Tests for Swift adapter SWIFT_PK rules."""

from __future__ import annotations

from pathlib import Path

from intendant.adapters.swift.pk import SwiftPackage, SwiftResolved, SwiftToolsVersion
from intendant.core.repo import Repo


def _repo(path: Path) -> Repo:
    return Repo(path=path, stacks=("swift",))


def test_pk001_pass(tmp_path: Path) -> None:
    (tmp_path / "Package.swift").write_text(
        '// swift-tools-version:5.9\nlet package = Package(name: "MyLib")\n'
    )
    result = SwiftPackage().check(_repo(tmp_path))
    assert result.passing is True
    assert "MyLib" in result.evidence


def test_pk001_fail_missing(tmp_path: Path) -> None:
    result = SwiftPackage().check(_repo(tmp_path))
    assert result.passing is False
    assert "Package.swift" in result.evidence


def test_pk001_fail_no_name(tmp_path: Path) -> None:
    (tmp_path / "Package.swift").write_text("// swift-tools-version:5.9\nlet package = Package()\n")
    result = SwiftPackage().check(_repo(tmp_path))
    assert result.passing is False
    assert "name" in result.evidence


def test_pk001_metadata() -> None:
    rule = SwiftPackage()
    assert rule.id == "SWIFT_PK001"
    assert rule.severity == "required"
    assert "swift" in rule.stacks


def test_pk002_pass(tmp_path: Path) -> None:
    (tmp_path / "Package.resolved").write_text("{}\n")
    assert SwiftResolved().check(_repo(tmp_path)).passing is True


def test_pk002_fail(tmp_path: Path) -> None:
    result = SwiftResolved().check(_repo(tmp_path))
    assert result.passing is False
    assert "Package.resolved" in result.evidence


def test_pk002_metadata() -> None:
    rule = SwiftResolved()
    assert rule.id == "SWIFT_PK002"
    assert rule.severity == "recommended"


def test_pk003_pass(tmp_path: Path) -> None:
    (tmp_path / "Package.swift").write_text(
        '// swift-tools-version:5.9\nlet package = Package(name: "X")\n'
    )
    result = SwiftToolsVersion().check(_repo(tmp_path))
    assert result.passing is True
    assert "5.9" in result.evidence


def test_pk003_fail_no_directive(tmp_path: Path) -> None:
    (tmp_path / "Package.swift").write_text('let package = Package(name: "X")\n')
    result = SwiftToolsVersion().check(_repo(tmp_path))
    assert result.passing is False


def test_pk003_skipped_when_package_swift_missing(tmp_path: Path) -> None:
    result = SwiftToolsVersion().check(_repo(tmp_path))
    assert result.skipped is True


def test_pk003_metadata() -> None:
    rule = SwiftToolsVersion()
    assert rule.id == "SWIFT_PK003"
    assert rule.severity == "recommended"
