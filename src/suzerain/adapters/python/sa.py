"""Python adapter SA rules."""

from __future__ import annotations

from suzerain.core.repo import Repo
from suzerain.core.rule import CheckResult, Rule

_PYTHON_GITIGNORE_BASELINE = ("__pycache__/", ".venv/")


class PYTHON_SA001GitignoreBaseline(Rule):  # noqa: N801
    id = "PYTHON_SA001"
    title = "Python .gitignore baseline (__pycache__/, .venv/)"
    severity = "required"
    stacks = ("python",)
    handbook_ref = "docs/handbook/06-sanitizing.md#python_sa001"

    def check(self, repo: Repo) -> CheckResult:
        path = repo.path / ".gitignore"
        if not path.is_file():
            return CheckResult(
                passing=True,
                skipped=True,
                evidence=".gitignore not found (covered by SA004)",
            )
        text = path.read_text()
        missing = [p for p in _PYTHON_GITIGNORE_BASELINE if p not in text]
        if missing:
            return CheckResult(
                passing=False,
                evidence=f"missing Python baseline patterns in .gitignore: {missing}",
            )
        return CheckResult(passing=True, evidence="Python baseline patterns present")
