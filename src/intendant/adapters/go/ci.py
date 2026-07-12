"""Go adapter GO_CI rules."""

from __future__ import annotations

from intendant.core.repo import Repo
from intendant.core.rule import CheckResult, Rule


class GO_CI001MinimumSteps(Rule):  # noqa: N801
    id = "GO_CI001"
    title = "CI workflow runs go vet/build, go test, and a linter"
    severity = "required"
    stacks = ("go",)
    handbook_ref = "docs/handbook/03-ci.md#go_ci001"

    def check(self, repo: Repo) -> CheckResult:
        contents = repo.workflows_text()
        if contents is None:
            return CheckResult(
                passing=True,
                skipped=True,
                evidence="no .github/workflows/ at the subproject or repo root (covered by CI001)",
            )
        missing: list[str] = []
        build_markers = ("go vet", "go build")
        if not any(m in contents for m in build_markers):
            missing.append("build (go vet / go build)")
        if repo.role != "frontend" and "go test" not in contents:
            missing.append("test (go test)")
        lint_markers = ("golangci-lint", "gofmt", "staticcheck", "revive")
        if not any(m in contents for m in lint_markers):
            missing.append("lint (golangci-lint / gofmt / staticcheck / revive)")
        if missing:
            return CheckResult(
                passing=False,
                evidence=f"CI workflow(s) missing Go steps: {missing}",
            )
        return CheckResult(
            passing=True,
            evidence="CI workflow(s) include Go build+test+lint",
        )
