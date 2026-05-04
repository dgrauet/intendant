"""Rust adapter RUST_SA rules."""

from __future__ import annotations

from suzerain.core.repo import Repo
from suzerain.core.rule import CheckResult, Rule

_RUST_GITIGNORE_BASELINE = ("target/",)


class RUST_SA001GitignoreBaseline(Rule):  # noqa: N801
    id = "RUST_SA001"
    title = "Rust .gitignore baseline (target/)"
    severity = "required"
    stacks = ("rust",)
    handbook_ref = "docs/handbook/06-sanitizing.md#rust_sa001"

    def check(self, repo: Repo) -> CheckResult:
        path = repo.path / ".gitignore"
        if not path.is_file():
            return CheckResult(
                passing=True,
                skipped=True,
                evidence=".gitignore not found (covered by SA004)",
            )
        text = path.read_text()
        missing = [p for p in _RUST_GITIGNORE_BASELINE if p not in text]
        if missing:
            return CheckResult(
                passing=False,
                evidence=f"missing Rust baseline patterns in .gitignore: {missing}",
            )
        return CheckResult(passing=True, evidence="Rust baseline patterns present")
