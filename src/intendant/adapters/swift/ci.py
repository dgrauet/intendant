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
        wf_dir = repo.path / ".github" / "workflows"
        if not wf_dir.is_dir():
            return CheckResult(
                passing=True,
                skipped=True,
                evidence="no .github/workflows/ directory (covered by CI001)",
            )
        contents = "\n".join(p.read_text(errors="replace") for p in wf_dir.glob("*.yml"))
        contents += "\n".join(p.read_text(errors="replace") for p in wf_dir.glob("*.yaml"))
        missing: list[str] = []
        if "swift build" not in contents:
            missing.append("build (swift build)")
        if "swift test" not in contents:
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
