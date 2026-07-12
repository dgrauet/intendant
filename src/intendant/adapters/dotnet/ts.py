""".NET adapter DOTNET_TS (tests) rules."""

from __future__ import annotations

from intendant.adapters.dotnet.inspectors import find_csproj_files, package_references
from intendant.core.repo import Repo
from intendant.core.rule import CheckResult, Rule

_TEST_PACKAGE_MARKERS = ("Microsoft.NET.Test.Sdk", "xunit", "NUnit", "MSTest.TestFramework")


class DotnetTestProject(Rule):
    id = "DOTNET_TS001"
    title = "at least one test project (xunit / NUnit / MSTest)"
    severity = "recommended"
    stacks = ("dotnet",)
    handbook_ref = "docs/handbook/15-dotnet.md#dotnet_ts001"

    def check(self, repo: Repo) -> CheckResult:
        test_projects = [
            p
            for p in find_csproj_files(repo.path)
            if any(
                ref == marker or ref.startswith(marker)
                for ref in package_references(p)
                for marker in _TEST_PACKAGE_MARKERS
            )
        ]
        if test_projects:
            rels = sorted(str(p.relative_to(repo.path)) for p in test_projects[:3])
            return CheckResult(
                passing=True,
                evidence=f"{len(test_projects)} test project(s); sample: {rels}",
            )
        return CheckResult(
            passing=False,
            evidence=(
                "no test project found (looked for a .csproj referencing "
                f"{list(_TEST_PACKAGE_MARKERS)})"
            ),
        )
