"""Helpers shared by Swift rule check methods."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

_TOOLS_VERSION_RE = re.compile(
    r"^//\s*swift-tools-version\s*[:=]?\s*(\d+\.\d+(?:\.\d+)?)",
    re.MULTILINE,
)
_NAME_RE = re.compile(r"name\s*:\s*\"([^\"]+)\"")
_TEST_FUNC_RE = re.compile(r"^\s*(?:func\s+test[A-Z_]\w*\s*\(|@Test\b)", re.MULTILINE)
_XCTESTCASE_RE = re.compile(r"\bXCTestCase\b")


@dataclass(frozen=True)
class SwiftPackage:
    name: str | None
    tools_version: str | None


def has_package_swift(repo_path: Path) -> bool:
    return (repo_path / "Package.swift").is_file()


def load_package_swift(repo_path: Path) -> SwiftPackage | None:
    """Parse Package.swift for `swift-tools-version` and the first `name:` literal.

    Returns None when the file is missing or unreadable. The `name:` regex
    matches the first quoted name encountered after the `Package(` constructor;
    it intentionally trades strict accuracy for zero external dependencies.
    """
    path = repo_path / "Package.swift"
    if not path.is_file():
        return None
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return None
    tools_match = _TOOLS_VERSION_RE.search(text)
    package_idx = text.find("Package(")
    name_match = _NAME_RE.search(text, pos=package_idx) if package_idx != -1 else None
    return SwiftPackage(
        name=name_match.group(1) if name_match else None,
        tools_version=tools_match.group(1) if tools_match else None,
    )


def find_test_files(repo_path: Path) -> list[Path]:
    """Return Swift test files under ``Tests/`` containing a recognisable test.

    A test is any file with a ``func test*(`` declaration, an ``XCTestCase``
    reference, or a Swift Testing ``@Test`` annotation. Walks the standard
    SwiftPM ``Tests/`` directory only — Xcode-only test targets live elsewhere
    and are out of scope. Skips ``.build/``, hidden directories, and packages
    vendored under ``Packages/``.
    """
    tests_dir = repo_path / "Tests"
    if not tests_dir.is_dir():
        return []
    hits: list[Path] = []
    skip_parts = {".build", ".swiftpm", "Packages"}
    for swift_file in tests_dir.rglob("*.swift"):
        rel_parts = swift_file.relative_to(repo_path).parts[:-1]
        if any(p in skip_parts or p.startswith(".") for p in rel_parts):
            continue
        try:
            text = swift_file.read_text(errors="replace")
        except OSError:
            continue
        if _TEST_FUNC_RE.search(text) or _XCTESTCASE_RE.search(text):
            hits.append(swift_file)
    return hits
