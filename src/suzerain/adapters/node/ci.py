"""Node adapter CI rules."""

from __future__ import annotations

from suzerain.core.repo import Repo
from suzerain.core.rule import CheckResult, Rule


class NODE_CI001MinimumSteps(Rule):  # noqa: N801
    id = "NODE_CI001"
    title = "CI workflow runs eslint/biome + tsc + test framework"
    severity = "required"
    stacks = ("node",)
    handbook_ref = "docs/handbook/03-ci.md#node_ci001"

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
        lint_markers = ("eslint", "@biomejs/biome", "biome check", "biome lint", "npm run lint")
        if not any(m in contents for m in lint_markers):
            missing.append("lint (eslint or biome)")
        type_markers = ("tsc", "typecheck", "pyright")
        if not any(m in contents for m in type_markers):
            missing.append("type (tsc / npm run typecheck)")
        test_markers = ("vitest", "jest", "mocha", "ava", "bun test", "npm test", "npm run test")
        if not any(m in contents for m in test_markers):
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
