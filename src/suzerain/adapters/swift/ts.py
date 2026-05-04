"""Swift adapter SWIFT_TS (tests) rules."""

from __future__ import annotations

from suzerain.adapters.swift.inspectors import find_test_files
from suzerain.core.repo import Repo
from suzerain.core.rule import CheckResult, Rule


class SwiftTestFiles(Rule):
    id = "SWIFT_TS001"
    title = "at least one Tests/**/*.swift file with a Test* function or @Test"
    severity = "recommended"
    stacks = ("swift",)
    handbook_ref = "docs/handbook/13-swift.md#swift_ts001"

    def check(self, repo: Repo) -> CheckResult:
        hits = find_test_files(repo.path)
        if hits:
            try:
                rels = sorted(str(p.relative_to(repo.path)) for p in hits[:3])
            except ValueError:
                rels = sorted(str(p) for p in hits[:3])
            return CheckResult(
                passing=True,
                evidence=f"{len(hits)} test file(s); sample: {rels}",
            )
        return CheckResult(
            passing=False,
            evidence=(
                "no Swift test file (looked for `func test*`, "
                "`XCTestCase`, or `@Test` under Tests/)"
            ),
        )
