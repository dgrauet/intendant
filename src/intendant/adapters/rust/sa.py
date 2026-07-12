"""Rust adapter RUST_SA rules."""

from __future__ import annotations

from intendant.core.repo import Repo
from intendant.core.rule import CheckResult, Rule

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


_SCAN_CI_MARKERS = (
    "cargo deny",
    "cargo-deny",
    "cargo audit",
    "cargo-audit",
    "rustsec/audit-check",
    "EmbarkStudios/cargo-deny-action",
)


class RUST_SA002CargoDenyAudit(Rule):  # noqa: N801
    id = "RUST_SA002"
    title = "dependency vulnerability/license scanning (cargo-deny or cargo-audit)"
    severity = "recommended"
    stacks = ("rust",)
    handbook_ref = "docs/handbook/11-rust.md#rust_sa002"

    def check(self, repo: Repo) -> CheckResult:
        if (repo.path / "deny.toml").is_file():
            return CheckResult(passing=True, evidence="deny.toml present (cargo-deny)")
        if (repo.path / ".cargo" / "audit.toml").is_file():
            return CheckResult(passing=True, evidence=".cargo/audit.toml present (cargo-audit)")
        wf_dir = repo.path / ".github" / "workflows"
        if wf_dir.is_dir():
            contents = "\n".join(
                p.read_text(errors="replace")
                for pattern in ("*.yml", "*.yaml")
                for p in wf_dir.glob(pattern)
            )
            found = [m for m in _SCAN_CI_MARKERS if m in contents]
            if found:
                return CheckResult(passing=True, evidence=f"scan step in CI: {found}")
        return CheckResult(
            passing=False,
            evidence=(
                "no dependency scanning found (looked for deny.toml, .cargo/audit.toml, "
                "or a cargo-deny / cargo-audit step in CI)"
            ),
        )
