"""Python adapter CI rules."""

from __future__ import annotations

from intendant.core.repo import Repo
from intendant.core.rule import CheckResult, Rule


class PYTHON_CI001MinimumSteps(Rule):  # noqa: N801
    id = "PYTHON_CI001"
    title = "CI workflow runs ruff + ty/pyright + pytest"
    severity = "required"
    stacks = ("python",)
    handbook_ref = "docs/handbook/03-ci.md#python_ci001"

    def check(self, repo: Repo) -> CheckResult:
        contents = repo.workflows_text()
        if contents is None:
            return CheckResult(
                passing=True,
                skipped=True,
                evidence="no .github/workflows/ at the subproject or repo root (covered by CI001)",
            )
        missing: list[str] = []
        if "ruff check" not in contents:
            missing.append("lint (ruff check)")
        if "ruff format" not in contents:
            missing.append("format (ruff format)")
        if "ty check" not in contents and "pyright" not in contents:
            missing.append("type (ty check or pyright)")
        if repo.role != "frontend" and "pytest" not in contents and "unittest" not in contents:
            missing.append("test (pytest or unittest)")
        if missing:
            return CheckResult(
                passing=False,
                evidence=f"CI workflow(s) missing Python steps: {missing}",
            )
        return CheckResult(
            passing=True,
            evidence="CI workflow(s) include Python lint+format+type+test",
        )
