"""Tests for the Swift adapter inspectors."""

from __future__ import annotations

from pathlib import Path

from suzerain.adapters.swift.inspectors import (
    find_test_files,
    has_package_swift,
    load_package_swift,
)


def test_has_package_swift_true(tmp_path: Path) -> None:
    (tmp_path / "Package.swift").write_text("// swift-tools-version:5.9\n")
    assert has_package_swift(tmp_path) is True


def test_has_package_swift_false(tmp_path: Path) -> None:
    assert has_package_swift(tmp_path) is False


def test_load_package_swift_full(tmp_path: Path) -> None:
    (tmp_path / "Package.swift").write_text(
        "// swift-tools-version:5.9\n"
        "import PackageDescription\n"
        'let package = Package(name: "MyLib", products: [])\n'
    )
    pkg = load_package_swift(tmp_path)
    assert pkg is not None
    assert pkg.name == "MyLib"
    assert pkg.tools_version == "5.9"


def test_load_package_swift_only_tools_version(tmp_path: Path) -> None:
    (tmp_path / "Package.swift").write_text("// swift-tools-version:5.10\n")
    pkg = load_package_swift(tmp_path)
    assert pkg is not None
    assert pkg.tools_version == "5.10"
    assert pkg.name is None


def test_load_package_swift_missing_returns_none(tmp_path: Path) -> None:
    assert load_package_swift(tmp_path) is None


def test_load_package_swift_ignores_name_outside_package_call(tmp_path: Path) -> None:
    """A `name:` literal appearing before `Package(` must not be picked up."""
    (tmp_path / "Package.swift").write_text(
        "// swift-tools-version:5.9\n"
        'let target = Target(name: "Other")\n'
        "let package = Package(\n"
        '    name: "Real",\n'
        "    products: []\n"
        ")\n"
    )
    pkg = load_package_swift(tmp_path)
    assert pkg is not None
    assert pkg.name == "Real"


def test_find_test_files_xctestcase(tmp_path: Path) -> None:
    test_dir = tmp_path / "Tests" / "MyLibTests"
    test_dir.mkdir(parents=True)
    (test_dir / "MyLibTests.swift").write_text(
        "import XCTest\nfinal class MyLibTests: XCTestCase {\n    func testExample() {}\n}\n"
    )
    hits = find_test_files(tmp_path)
    assert len(hits) == 1


def test_find_test_files_swift_testing_macro(tmp_path: Path) -> None:
    test_dir = tmp_path / "Tests" / "MyLibTests"
    test_dir.mkdir(parents=True)
    (test_dir / "MyTests.swift").write_text("import Testing\n@Test func example() {}\n")
    hits = find_test_files(tmp_path)
    assert len(hits) == 1


def test_find_test_files_skips_dot_build_and_swiftpm(tmp_path: Path) -> None:
    for buried in (".build", ".swiftpm"):
        d = tmp_path / "Tests" / buried / "Inner"
        d.mkdir(parents=True)
        (d / "Buried.swift").write_text("class X: XCTestCase {}\n")
    assert find_test_files(tmp_path) == []


def test_find_test_files_no_tests_dir(tmp_path: Path) -> None:
    assert find_test_files(tmp_path) == []


def test_find_test_files_non_test_swift_ignored(tmp_path: Path) -> None:
    test_dir = tmp_path / "Tests" / "MyLibTests"
    test_dir.mkdir(parents=True)
    (test_dir / "Helpers.swift").write_text("struct Helper {}\n")
    assert find_test_files(tmp_path) == []
