"""Go adapter GO_QU (quality) rules."""

from __future__ import annotations

from suzerain.core.repo import Repo
from suzerain.core.rule import CheckResult, Rule

_GOLANGCI_CONFIGS = (
    ".golangci.yml",
    ".golangci.yaml",
    ".golangci.toml",
    ".golangci.json",
)


class GoLinter(Rule):
    id = "GO_QU001"
    title = "golangci-lint config present"
    severity = "recommended"
    stacks = ("go",)
    handbook_ref = "docs/handbook/12-go.md#go_qu001"

    def check(self, repo: Repo) -> CheckResult:
        present = [name for name in _GOLANGCI_CONFIGS if (repo.path / name).is_file()]
        if present:
            return CheckResult(passing=True, evidence=f"linter config present: {present}")
        return CheckResult(
            passing=False,
            evidence=f"no golangci-lint config (looked for {list(_GOLANGCI_CONFIGS)})",
        )
