"""Claude Skill adapter CI rules."""

from __future__ import annotations

from intendant.core.repo import Repo
from intendant.core.rule import CheckResult, Rule


class CLAUDE_SKILL_CI001MinimumSteps(Rule):  # noqa: N801
    id = "CLAUDE_SKILL_CI001"
    title = "CI workflow runs intendant audit"
    severity = "required"
    stacks = ("claude-skill",)
    handbook_ref = "docs/handbook/03-ci.md#claude_skill_ci001"

    def check(self, repo: Repo) -> CheckResult:
        contents = repo.workflows_text()
        if contents is None:
            return CheckResult(
                passing=True,
                skipped=True,
                evidence="no .github/workflows/ at the subproject or repo root (covered by CI001)",
            )
        if "intendant audit" not in contents:
            return CheckResult(
                passing=False,
                evidence="no `intendant audit` step found in CI workflows",
            )
        return CheckResult(
            passing=True,
            evidence="`intendant audit` step found in CI",
        )
