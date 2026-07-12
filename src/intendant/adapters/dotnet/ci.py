""".NET adapter DOTNET_CI rules."""

from __future__ import annotations

from intendant.core.repo import Repo
from intendant.core.rule import CheckResult, Rule


class DOTNET_CI001MinimumSteps(Rule):  # noqa: N801
    id = "DOTNET_CI001"
    title = "CI workflow runs dotnet format, dotnet build, and dotnet test"
    severity = "required"
    stacks = ("dotnet",)
    handbook_ref = "docs/handbook/03-ci.md#dotnet_ci001"

    def check(self, repo: Repo) -> CheckResult:
        wf_dir = repo.path / ".github" / "workflows"
        if not wf_dir.is_dir():
            return CheckResult(
                passing=True,
                skipped=True,
                evidence="no .github/workflows/ directory (covered by CI001)",
            )
        contents = "\n".join(p.read_text(errors="replace") for p in wf_dir.glob("*.yml"))
        contents += "\n".join(p.read_text(errors="replace") for p in wf_dir.glob("*.yaml"))
        missing: list[str] = []
        if "dotnet build" not in contents:
            missing.append("build (dotnet build)")
        if "dotnet test" not in contents:
            missing.append("test (dotnet test)")
        if "dotnet format" not in contents:
            missing.append("format (dotnet format --verify-no-changes)")
        if missing:
            return CheckResult(
                passing=False,
                evidence=f"CI workflow(s) missing .NET steps: {missing}",
            )
        return CheckResult(
            passing=True,
            evidence="CI workflow(s) include dotnet format+build+test",
        )
