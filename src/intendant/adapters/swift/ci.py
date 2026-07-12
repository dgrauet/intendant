"""Swift adapter SWIFT_CI rules."""

from __future__ import annotations

from intendant.core.repo import Repo
from intendant.core.rule import CheckResult, Rule


class SWIFT_CI001MinimumSteps(Rule):  # noqa: N801
    id = "SWIFT_CI001"
    title = "CI workflow runs swift build, swift test, and a linter"
    severity = "required"
    stacks = ("swift",)
    handbook_ref = "docs/handbook/03-ci.md#swift_ci001"

    def check(self, repo: Repo) -> CheckResult:
        contents = repo.workflows_text()
        if contents is None:
            return CheckResult(
                passing=True,
                skipped=True,
                evidence="no .github/workflows/ at the subproject or repo root (covered by CI001)",
            )
        missing: list[str] = []
        if "swift build" not in contents:
            missing.append("build (swift build)")
        if repo.role != "frontend" and "swift test" not in contents:
            missing.append("test (swift test)")
        lint_markers = ("swiftlint", "swiftformat", "swift-format")
        if not any(m in contents for m in lint_markers):
            missing.append("lint (swiftlint / swiftformat / swift-format)")
        if missing:
            return CheckResult(
                passing=False,
                evidence=f"CI workflow(s) missing Swift steps: {missing}",
            )
        return CheckResult(
            passing=True,
            evidence="CI workflow(s) include Swift build+test+lint",
        )
