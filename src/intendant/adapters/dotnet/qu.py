""".NET adapter DOTNET_QU (quality) rules."""

from __future__ import annotations

from intendant.adapters.dotnet.inspectors import find_csproj_files, nullable_enabled
from intendant.core.repo import Repo
from intendant.core.rule import CheckResult, Rule


class DotnetNullable(Rule):
    id = "DOTNET_QU001"
    title = "nullable reference types enabled in every project"
    severity = "required"
    stacks = ("dotnet",)
    handbook_ref = "docs/handbook/15-dotnet.md#dotnet_qu001"

    def check(self, repo: Repo) -> CheckResult:
        projects = find_csproj_files(repo.path)
        if not projects:
            return CheckResult(
                passing=True,
                skipped=True,
                evidence="no .csproj found (covered by DOTNET_PK001)",
            )
        missing = [p for p in projects if not nullable_enabled(p, repo.path)]
        if missing:
            rels = sorted(str(p.relative_to(repo.path)) for p in missing[:3])
            return CheckResult(
                passing=False,
                evidence=(
                    f"<Nullable>enable</Nullable> missing in {rels} "
                    "(set it in the .csproj or a Directory.Build.props)"
                ),
            )
        return CheckResult(passing=True, evidence="Nullable enabled for every project")


class DotnetEditorconfig(Rule):
    id = "DOTNET_QU002"
    title = ".editorconfig present (dotnet format / analyzers style source of truth)"
    severity = "recommended"
    stacks = ("dotnet",)
    handbook_ref = "docs/handbook/15-dotnet.md#dotnet_qu002"

    def check(self, repo: Repo) -> CheckResult:
        if (repo.path / ".editorconfig").is_file():
            return CheckResult(passing=True, evidence=".editorconfig present")
        return CheckResult(
            passing=False,
            evidence=".editorconfig not found at repo root (used by `dotnet format` and analyzers)",
        )
