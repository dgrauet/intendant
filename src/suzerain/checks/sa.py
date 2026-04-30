"""SA (sanitizing) transverse rules."""

from __future__ import annotations

from suzerain.core.repo import Repo
from suzerain.core.rule import CheckResult, Rule

_MINIMUM_HOOK_IDS = {"trailing-whitespace", "end-of-file-fixer", "check-yaml"}


class SA001PreCommit(Rule):
    id = "SA001"
    title = ".pre-commit-config.yaml present with minimum baseline hooks"
    severity = "required"
    stacks = ("*",)
    handbook_ref = "docs/handbook/06-sanitizing.md#sa001"
    template_ref = "templates/python/.pre-commit-config.yaml"

    def check(self, repo: Repo) -> CheckResult:
        path = repo.path / ".pre-commit-config.yaml"
        if not path.is_file():
            return CheckResult(passing=False, evidence=".pre-commit-config.yaml not found")
        text = path.read_text()
        present = {hook for hook in _MINIMUM_HOOK_IDS if f"id: {hook}" in text}
        missing = _MINIMUM_HOOK_IDS - present
        if missing:
            return CheckResult(
                passing=False,
                evidence=f"missing baseline hooks: {sorted(missing)}",
            )
        return CheckResult(passing=True)
