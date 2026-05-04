"""Swift adapter SWIFT_PK (packaging) rules."""

from __future__ import annotations

from suzerain.adapters.swift.inspectors import has_package_swift, load_package_swift
from suzerain.core.repo import Repo
from suzerain.core.rule import CheckResult, Rule


class SwiftPackage(Rule):
    id = "SWIFT_PK001"
    title = "Package.swift present at repo root with a Package(name:) declaration"
    severity = "required"
    stacks = ("swift",)
    handbook_ref = "docs/handbook/13-swift.md#swift_pk001"

    def check(self, repo: Repo) -> CheckResult:
        if not has_package_swift(repo.path):
            return CheckResult(passing=False, evidence="Package.swift not found at repo root")
        pkg = load_package_swift(repo.path)
        if pkg is None or pkg.name is None:
            return CheckResult(
                passing=False,
                evidence='Package.swift missing `Package(name: "…")` declaration',
            )
        return CheckResult(passing=True, evidence=f"package declared: {pkg.name}")


class SwiftResolved(Rule):
    id = "SWIFT_PK002"
    title = "Package.resolved present at repo root"
    severity = "recommended"
    stacks = ("swift",)
    handbook_ref = "docs/handbook/13-swift.md#swift_pk002"

    def check(self, repo: Repo) -> CheckResult:
        if (repo.path / "Package.resolved").is_file():
            return CheckResult(passing=True, evidence="Package.resolved present")
        return CheckResult(
            passing=False,
            evidence="Package.resolved not found (run `swift package resolve` then commit it)",
        )


class SwiftToolsVersion(Rule):
    id = "SWIFT_PK003"
    title = "swift-tools-version pinned in Package.swift"
    severity = "recommended"
    stacks = ("swift",)
    handbook_ref = "docs/handbook/13-swift.md#swift_pk003"

    def check(self, repo: Repo) -> CheckResult:
        pkg = load_package_swift(repo.path)
        if pkg is None:
            return CheckResult(
                passing=True,
                skipped=True,
                evidence="Package.swift missing or unreadable (covered by SWIFT_PK001)",
            )
        if pkg.tools_version:
            return CheckResult(
                passing=True, evidence=f"swift-tools-version pinned: {pkg.tools_version}"
            )
        return CheckResult(
            passing=False,
            evidence=(
                "no `// swift-tools-version:<X.Y>` directive on the first line of Package.swift"
            ),
        )
