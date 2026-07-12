"""Go adapter GO_TS (tests) rules."""

from __future__ import annotations

from intendant.adapters.go.inspectors import find_test_files
from intendant.core.repo import Repo
from intendant.core.rule import CheckResult, Rule


class GoTestFiles(Rule):
    id = "GO_TS001"
    title = "at least one *_test.go file with a Test* function"
    severity = "recommended"
    stacks = ("go",)
    skipped_for_roles = ("frontend",)
    handbook_ref = "docs/handbook/12-go.md#go_ts001"

    def check(self, repo: Repo) -> CheckResult:
        hits = find_test_files(repo.path)
        if hits:
            try:
                rels = sorted(str(p.relative_to(repo.path)) for p in hits[:3])
            except ValueError:
                rels = sorted(str(p) for p in hits[:3])
            return CheckResult(
                passing=True,
                evidence=f"{len(hits)} test file(s); sample: {rels}",
            )
        return CheckResult(
            passing=False,
            evidence="no *_test.go file containing `func Test*` found",
        )
