""".NET adapter DOTNET_PK (packaging) rules."""

from __future__ import annotations

from intendant.adapters.dotnet.inspectors import find_csproj_files, target_frameworks
from intendant.core.repo import Repo
from intendant.core.rule import CheckResult, Rule


class DotnetProject(Rule):
    id = "DOTNET_PK001"
    title = "at least one .csproj declaring a TargetFramework"
    severity = "required"
    stacks = ("dotnet",)
    handbook_ref = "docs/handbook/15-dotnet.md#dotnet_pk001"

    def check(self, repo: Repo) -> CheckResult:
        projects = find_csproj_files(repo.path)
        if not projects:
            return CheckResult(passing=False, evidence="no .csproj file found in the repo")
        frameworks = sorted({fw for p in projects for fw in target_frameworks(p)})
        if not frameworks:
            return CheckResult(
                passing=False,
                evidence=f"{len(projects)} .csproj file(s) but none declares <TargetFramework>",
            )
        return CheckResult(
            passing=True,
            evidence=f"{len(projects)} project(s); target frameworks: {frameworks}",
        )


class DotnetLockfile(Rule):
    id = "DOTNET_PK002"
    title = "NuGet lockfile (packages.lock.json) committed next to each project"
    severity = "recommended"
    stacks = ("dotnet",)
    handbook_ref = "docs/handbook/15-dotnet.md#dotnet_pk002"

    def check(self, repo: Repo) -> CheckResult:
        projects = find_csproj_files(repo.path)
        if not projects:
            return CheckResult(
                passing=True,
                skipped=True,
                evidence="no .csproj found (covered by DOTNET_PK001)",
            )
        missing = [p for p in projects if not (p.parent / "packages.lock.json").is_file()]
        if missing:
            rels = sorted(str(p.relative_to(repo.path)) for p in missing[:3])
            return CheckResult(
                passing=False,
                evidence=(
                    f"no packages.lock.json next to {rels} "
                    "(enable RestorePackagesWithLockFile and commit the lockfile)"
                ),
            )
        return CheckResult(passing=True, evidence="packages.lock.json present for every project")
