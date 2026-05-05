"""Rust adapter RUST_PK (packaging) rules."""

from __future__ import annotations

from intendant.adapters.rust.inspectors import has_cargo_toml, load_cargo_toml
from intendant.core.repo import Repo
from intendant.core.rule import CheckResult, Rule


class RustCargoToml(Rule):
    id = "RUST_PK001"
    title = "Cargo.toml present at repo root with [package] section"
    severity = "required"
    stacks = ("rust",)
    handbook_ref = "docs/handbook/11-rust.md#rust_pk001"

    def check(self, repo: Repo) -> CheckResult:
        if not has_cargo_toml(repo.path):
            return CheckResult(passing=False, evidence="Cargo.toml not found at repo root")
        cargo = load_cargo_toml(repo.path)
        if cargo is None:
            return CheckResult(passing=False, evidence="Cargo.toml is unparseable")
        if "package" in cargo or "workspace" in cargo:
            kind = "package" if "package" in cargo else "workspace"
            return CheckResult(passing=True, evidence=f"Cargo.toml has [{kind}] section")
        return CheckResult(
            passing=False,
            evidence="Cargo.toml is missing both [package] and [workspace] sections",
        )


class RustCargoLock(Rule):
    id = "RUST_PK002"
    title = "Cargo.lock present at repo root"
    severity = "required"
    stacks = ("rust",)
    handbook_ref = "docs/handbook/11-rust.md#rust_pk002"

    def check(self, repo: Repo) -> CheckResult:
        if (repo.path / "Cargo.lock").is_file():
            return CheckResult(passing=True, evidence="Cargo.lock present")
        return CheckResult(
            passing=False,
            evidence="Cargo.lock not found (commit it for binaries; libraries may exempt)",
        )


class RustEdition(Rule):
    id = "RUST_PK003"
    title = "edition pinned in Cargo.toml [package]"
    severity = "recommended"
    stacks = ("rust",)
    handbook_ref = "docs/handbook/11-rust.md#rust_pk003"

    def check(self, repo: Repo) -> CheckResult:
        cargo = load_cargo_toml(repo.path)
        if cargo is None:
            return CheckResult(
                passing=True,
                skipped=True,
                evidence="Cargo.toml missing or unparseable (covered by RUST_PK001)",
            )
        package = cargo.get("package")
        if not isinstance(package, dict):
            return CheckResult(
                passing=True,
                skipped=True,
                evidence="no [package] section (covered by RUST_PK001)",
            )
        edition = package.get("edition")
        if isinstance(edition, str) and edition:
            return CheckResult(passing=True, evidence=f"edition pinned: {edition!r}")
        return CheckResult(
            passing=False,
            evidence="no `edition` field in [package] (defaults silently to 2015)",
        )
