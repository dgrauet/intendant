"""TS (tests) transverse rules."""

from __future__ import annotations

from intendant.core.repo import Repo
from intendant.core.rule import CheckResult, Rule


class TS002RegressionTestsLayout(Rule):
    id = "TS002"
    title = "regression_tests/ at repo root (when used)"
    severity = "recommended"
    stacks = ("*",)
    handbook_ref = "docs/handbook/05-tests.md#ts002"

    def check(self, repo: Repo) -> CheckResult:
        rt_dir = repo.path / "regression_tests"
        if not rt_dir.is_dir():
            return CheckResult(
                passing=True,
                skipped=True,
                evidence="no regression_tests/ directory (rule applies only when present)",
            )
        files = [p for p in rt_dir.iterdir() if p.is_file()]
        if not files:
            return CheckResult(
                passing=False,
                evidence="regression_tests/ exists but is empty",
            )
        return CheckResult(
            passing=True,
            evidence=f"regression_tests/ present with {len(files)} file(s)",
        )
