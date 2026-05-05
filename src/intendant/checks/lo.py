"""LO (layout) transverse rules."""

from __future__ import annotations

from intendant.core.repo import Repo
from intendant.core.rule import CheckResult, Rule


class LO003DocsDirectory(Rule):
    id = "LO003"
    title = "Documentation in docs/"
    severity = "recommended"
    stacks = ("*",)
    handbook_ref = "docs/handbook/01-layout.md#lo003"

    def check(self, repo: Repo) -> CheckResult:
        if (repo.path / "docs").is_dir():
            return CheckResult(passing=True)
        return CheckResult(passing=False, evidence="docs/ directory not found at repo root")
