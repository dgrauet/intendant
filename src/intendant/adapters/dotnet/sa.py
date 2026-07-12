""".NET adapter DOTNET_SA rules."""

from __future__ import annotations

from intendant.core.repo import Repo
from intendant.core.rule import CheckResult, Rule

# Each baseline entry lists the accepted spellings (plain or case-bracket style).
_DOTNET_GITIGNORE_BASELINE = (
    ("bin/", "[Bb]in/"),
    ("obj/", "[Oo]bj/"),
)


class DOTNET_SA001GitignoreBaseline(Rule):  # noqa: N801
    id = "DOTNET_SA001"
    title = ".NET .gitignore baseline (bin/, obj/)"
    severity = "required"
    stacks = ("dotnet",)
    handbook_ref = "docs/handbook/06-sanitizing.md#dotnet_sa001"

    def check(self, repo: Repo) -> CheckResult:
        path = repo.path / ".gitignore"
        if not path.is_file():
            return CheckResult(
                passing=True,
                skipped=True,
                evidence=".gitignore not found (covered by SA004)",
            )
        text = path.read_text()
        missing = [
            variants[0]
            for variants in _DOTNET_GITIGNORE_BASELINE
            if not any(v in text for v in variants)
        ]
        if missing:
            return CheckResult(
                passing=False,
                evidence=f"missing .NET baseline patterns in .gitignore: {missing}",
            )
        return CheckResult(passing=True, evidence=".NET baseline patterns present")
