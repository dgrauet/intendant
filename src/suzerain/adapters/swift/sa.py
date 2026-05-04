"""Swift adapter SWIFT_SA rules."""

from __future__ import annotations

from suzerain.core.repo import Repo
from suzerain.core.rule import CheckResult, Rule

_SWIFT_GITIGNORE_BASELINE = (".build/", "xcuserdata/")


class SWIFT_SA001GitignoreBaseline(Rule):  # noqa: N801
    id = "SWIFT_SA001"
    title = "Swift .gitignore baseline (.build/, xcuserdata/)"
    severity = "required"
    stacks = ("swift",)
    handbook_ref = "docs/handbook/06-sanitizing.md#swift_sa001"

    def check(self, repo: Repo) -> CheckResult:
        path = repo.path / ".gitignore"
        if not path.is_file():
            return CheckResult(
                passing=True,
                skipped=True,
                evidence=".gitignore not found (covered by SA004)",
            )
        text = path.read_text()
        missing = [p for p in _SWIFT_GITIGNORE_BASELINE if p not in text]
        if missing:
            return CheckResult(
                passing=False,
                evidence=f"missing Swift baseline patterns in .gitignore: {missing}",
            )
        return CheckResult(passing=True, evidence="Swift baseline patterns present")
