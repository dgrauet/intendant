"""Rust adapter RUST_CI rules."""

from __future__ import annotations

from suzerain.core.repo import Repo
from suzerain.core.rule import CheckResult, Rule


class RUST_CI001MinimumSteps(Rule):  # noqa: N801
    id = "RUST_CI001"
    title = "CI workflow runs cargo fmt, clippy, and test"
    severity = "required"
    stacks = ("rust",)
    handbook_ref = "docs/handbook/03-ci.md#rust_ci001"

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
        if not any(m in contents for m in ("cargo fmt", "rustfmt")):
            missing.append("fmt (cargo fmt)")
        if "cargo clippy" not in contents:
            missing.append("lint (cargo clippy)")
        if "cargo test" not in contents and "cargo nextest" not in contents:
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
