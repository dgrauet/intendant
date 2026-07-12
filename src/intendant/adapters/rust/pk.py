"""Rust adapter RUST_PK (packaging) rules."""

from __future__ import annotations

from intendant.adapters.rust.inspectors import (
    has_cargo_toml,
    load_cargo_toml,
    workspace_member_manifests,
)
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
    title = "edition pinned in every crate ([package] or workspace inheritance)"
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
        workspace = cargo.get("workspace")
        if not isinstance(package, dict) and not isinstance(workspace, dict):
            return CheckResult(
                passing=True,
                skipped=True,
                evidence="neither [package] nor [workspace] section (covered by RUST_PK001)",
            )
        ws_package = workspace.get("package") if isinstance(workspace, dict) else None
        ws_edition = ws_package.get("edition") if isinstance(ws_package, dict) else None

        crates: list[tuple[str, dict]] = []
        if isinstance(package, dict):
            crates.append((".", package))
        for rel, manifest in workspace_member_manifests(repo.path):
            member_pkg = manifest.get("package")
            if isinstance(member_pkg, dict):
                crates.append((rel, member_pkg))
        if not crates:
            return CheckResult(passing=True, evidence="workspace declares no member crates")

        editions: set[str] = set()
        offenders: list[str] = []
        for rel, pkg in crates:
            edition = pkg.get("edition")
            if isinstance(edition, str) and edition:
                editions.add(edition)
            elif (
                isinstance(edition, dict)
                and edition.get("workspace") is True
                and isinstance(ws_edition, str)
            ):
                editions.add(ws_edition)
            else:
                offenders.append(rel)
        if offenders:
            return CheckResult(
                passing=False,
                evidence=(
                    f"crate(s) without a pinned edition (defaults silently to 2015): "
                    f"{offenders[:5]} — set `edition` in [package] or inherit via "
                    "`edition.workspace = true` + [workspace.package] edition"
                ),
            )
        return CheckResult(passing=True, evidence=f"edition pinned: {sorted(editions)}")
