"""Rust adapter RUST_QU (quality) rules."""

from __future__ import annotations

from intendant.core.repo import Repo
from intendant.core.rule import CheckResult, Rule


class RustToolchainPin(Rule):
    id = "RUST_QU001"
    title = "rust-toolchain.toml pins the toolchain"
    severity = "recommended"
    stacks = ("rust",)
    handbook_ref = "docs/handbook/11-rust.md#rust_qu001"

    def check(self, repo: Repo) -> CheckResult:
        for name in ("rust-toolchain.toml", "rust-toolchain"):
            if (repo.path / name).is_file():
                return CheckResult(passing=True, evidence=f"{name} present")
        return CheckResult(
            passing=False,
            evidence="no rust-toolchain.toml — contributors may use mismatched compilers",
        )
