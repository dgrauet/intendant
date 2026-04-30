"""CI transverse rules."""

from __future__ import annotations

from suzerain.core.repo import Repo
from suzerain.core.rule import CheckResult, Rule


class CI001CIWorkflow(Rule):
    id = "CI001"
    title = ".github/workflows/ contains at least one CI workflow"
    severity = "required"
    stacks = ("*",)
    handbook_ref = "docs/handbook/03-ci.md#ci001"
    template_ref = "templates/github/ci.yml"

    def check(self, repo: Repo) -> CheckResult:
        wf_dir = repo.path / ".github" / "workflows"
        if not wf_dir.is_dir():
            return CheckResult(
                passing=False,
                evidence=".github/workflows/ directory not found",
            )
        workflows = list(wf_dir.glob("*.yml")) + list(wf_dir.glob("*.yaml"))
        if not workflows:
            return CheckResult(
                passing=False,
                evidence=".github/workflows/ exists but contains no workflow YAML files",
            )
        return CheckResult(passing=True)
