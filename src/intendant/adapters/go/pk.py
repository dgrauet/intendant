"""Go adapter GO_PK (packaging) rules."""

from __future__ import annotations

from intendant.adapters.go.inspectors import has_go_mod, load_go_mod
from intendant.core.repo import Repo
from intendant.core.rule import CheckResult, Rule


class GoMod(Rule):
    id = "GO_PK001"
    title = "go.mod present at repo root with module declaration"
    severity = "required"
    stacks = ("go",)
    handbook_ref = "docs/handbook/12-go.md#go_pk001"

    def check(self, repo: Repo) -> CheckResult:
        if not has_go_mod(repo.path):
            return CheckResult(passing=False, evidence="go.mod not found at repo root")
        mod = load_go_mod(repo.path)
        if mod is None or mod.module is None:
            return CheckResult(
                passing=False,
                evidence="go.mod missing `module <path>` directive",
            )
        return CheckResult(passing=True, evidence=f"module declared: {mod.module}")


class GoSum(Rule):
    id = "GO_PK002"
    title = "go.sum present at repo root"
    severity = "required"
    stacks = ("go",)
    handbook_ref = "docs/handbook/12-go.md#go_pk002"

    def check(self, repo: Repo) -> CheckResult:
        if (repo.path / "go.sum").is_file():
            return CheckResult(passing=True, evidence="go.sum present")
        return CheckResult(
            passing=False,
            evidence="go.sum not found (run `go mod tidy` then commit it)",
        )


class GoVersion(Rule):
    id = "GO_PK003"
    title = "go directive pinned in go.mod"
    severity = "recommended"
    stacks = ("go",)
    handbook_ref = "docs/handbook/12-go.md#go_pk003"

    def check(self, repo: Repo) -> CheckResult:
        mod = load_go_mod(repo.path)
        if mod is None:
            return CheckResult(
                passing=True,
                skipped=True,
                evidence="go.mod missing or unreadable (covered by GO_PK001)",
            )
        if mod.go_version:
            return CheckResult(passing=True, evidence=f"go version pinned: {mod.go_version}")
        return CheckResult(
            passing=False,
            evidence="no `go <version>` directive in go.mod",
        )
