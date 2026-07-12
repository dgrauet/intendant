"""Node adapter CI rules."""

from __future__ import annotations

from intendant.core.repo import Repo
from intendant.core.rule import CheckResult, Rule


class NODE_CI001MinimumSteps(Rule):  # noqa: N801
    id = "NODE_CI001"
    title = "CI workflow runs eslint/biome + tsc + test framework"
    severity = "required"
    stacks = ("node",)
    handbook_ref = "docs/handbook/03-ci.md#node_ci001"

    def check(self, repo: Repo) -> CheckResult:
        contents = repo.workflows_text()
        if contents is None:
            return CheckResult(
                passing=True,
                skipped=True,
                evidence="no .github/workflows/ at the subproject or repo root (covered by CI001)",
            )
        missing: list[str] = []
        lint_markers = ("eslint", "@biomejs/biome", "biome check", "biome lint", "npm run lint")
        if not any(m in contents for m in lint_markers):
            missing.append("lint (eslint or biome)")
        type_markers = ("tsc", "typecheck", "pyright")
        if not any(m in contents for m in type_markers):
            missing.append("type (tsc / npm run typecheck)")
        test_markers = ("vitest", "jest", "mocha", "ava", "bun test", "npm test", "npm run test")
        if repo.role != "frontend" and not any(m in contents for m in test_markers):
            missing.append("test (vitest/jest/mocha/ava/bun test)")
        if missing:
            return CheckResult(
                passing=False,
                evidence=f"CI workflow(s) missing Node steps: {missing}",
            )
        return CheckResult(
            passing=True,
            evidence="CI workflow(s) include Node lint+type+test",
        )
