"""Node adapter SA rules."""

from __future__ import annotations

from intendant.core.repo import Repo
from intendant.core.rule import CheckResult, Rule

_NODE_GITIGNORE_BASELINE = ("node_modules/", "dist/")


class NODE_SA001GitignoreBaseline(Rule):  # noqa: N801
    id = "NODE_SA001"
    title = "Node .gitignore baseline (node_modules/, dist/)"
    severity = "required"
    stacks = ("node",)
    handbook_ref = "docs/handbook/06-sanitizing.md#node_sa001"

    def check(self, repo: Repo) -> CheckResult:
        path = repo.path / ".gitignore"
        if not path.is_file():
            return CheckResult(
                passing=True,
                skipped=True,
                evidence=".gitignore not found (covered by SA004)",
            )
        text = path.read_text()
        missing = [p for p in _NODE_GITIGNORE_BASELINE if p not in text]
        if missing:
            return CheckResult(
                passing=False,
                evidence=f"missing Node baseline patterns in .gitignore: {missing}",
            )
        return CheckResult(passing=True, evidence="Node baseline patterns present")
