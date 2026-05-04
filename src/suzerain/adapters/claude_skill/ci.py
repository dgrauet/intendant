"""Claude Skill adapter CI rules."""

from __future__ import annotations

from suzerain.core.repo import Repo
from suzerain.core.rule import CheckResult, Rule


class CLAUDE_SKILL_CI001MinimumSteps(Rule):  # noqa: N801
    id = "CLAUDE_SKILL_CI001"
    title = "CI workflow runs suzerain audit"
    severity = "required"
    stacks = ("claude-skill",)
    handbook_ref = "docs/handbook/03-ci.md#claude_skill_ci001"

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
        if "suzerain audit" not in contents:
            return CheckResult(
                passing=False,
                evidence="no `suzerain audit` step found in CI workflows",
            )
        return CheckResult(
            passing=True,
            evidence="`suzerain audit` step found in CI",
        )
