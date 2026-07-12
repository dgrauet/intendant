"""Rust adapter RUST_CI rules."""

from __future__ import annotations

from intendant.core.repo import Repo
from intendant.core.rule import CheckResult, Rule


class RUST_CI001MinimumSteps(Rule):  # noqa: N801
    id = "RUST_CI001"
    title = "CI workflow runs cargo fmt, clippy, and test"
    severity = "required"
    stacks = ("rust",)
    handbook_ref = "docs/handbook/03-ci.md#rust_ci001"

    def check(self, repo: Repo) -> CheckResult:
        contents = repo.workflows_text()
        if contents is None:
            return CheckResult(
                passing=True,
                skipped=True,
                evidence="no .github/workflows/ at the subproject or repo root (covered by CI001)",
            )
        missing: list[str] = []
        if not any(m in contents for m in ("cargo fmt", "rustfmt")):
            missing.append("fmt (cargo fmt)")
        if "cargo clippy" not in contents:
            missing.append("lint (cargo clippy)")
        if repo.role != "frontend" and (
            "cargo test" not in contents and "cargo nextest" not in contents
        ):
            missing.append("test (cargo test / nextest)")
        if missing:
            return CheckResult(
                passing=False,
                evidence=f"CI workflow(s) missing Rust steps: {missing}",
            )
        return CheckResult(
            passing=True,
            evidence="CI workflow(s) include Rust fmt+clippy+test",
        )
