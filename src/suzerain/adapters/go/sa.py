"""Go adapter GO_SA rules."""

from __future__ import annotations

from suzerain.core.repo import Repo
from suzerain.core.rule import CheckResult, Rule

_GO_GITIGNORE_BASELINE = ("*.test",)


class GO_SA001GitignoreBaseline(Rule):  # noqa: N801
    id = "GO_SA001"
    title = "Go .gitignore baseline (*.test)"
    severity = "required"
    stacks = ("go",)
    handbook_ref = "docs/handbook/06-sanitizing.md#go_sa001"

    def check(self, repo: Repo) -> CheckResult:
        path = repo.path / ".gitignore"
        if not path.is_file():
            return CheckResult(
                passing=True,
                skipped=True,
                evidence=".gitignore not found (covered by SA004)",
            )
        text = path.read_text()
        missing = [p for p in _GO_GITIGNORE_BASELINE if p not in text]
        if missing:
            return CheckResult(
                passing=False,
                evidence=f"missing Go baseline patterns in .gitignore: {missing}",
            )
        return CheckResult(passing=True, evidence="Go baseline patterns present")
