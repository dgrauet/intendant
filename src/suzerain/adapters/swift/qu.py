"""Swift adapter SWIFT_QU (quality) rules."""

from __future__ import annotations

from suzerain.core.repo import Repo
from suzerain.core.rule import CheckResult, Rule

_LINTER_CONFIGS = (
    ".swiftlint.yml",
    ".swiftlint.yaml",
    ".swiftformat",
)


class SwiftLinter(Rule):
    id = "SWIFT_QU001"
    title = "swiftlint or swiftformat config present"
    severity = "recommended"
    stacks = ("swift",)
    handbook_ref = "docs/handbook/13-swift.md#swift_qu001"

    def check(self, repo: Repo) -> CheckResult:
        present = [name for name in _LINTER_CONFIGS if (repo.path / name).is_file()]
        if present:
            return CheckResult(passing=True, evidence=f"linter config present: {present}")
        return CheckResult(
            passing=False,
            evidence=f"no swiftlint/swiftformat config (looked for {list(_LINTER_CONFIGS)})",
        )
