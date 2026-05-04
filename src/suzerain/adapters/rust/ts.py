"""Rust adapter RUST_TS (tests) rules."""

from __future__ import annotations

from suzerain.adapters.rust.inspectors import find_test_annotations
from suzerain.core.repo import Repo
from suzerain.core.rule import CheckResult, Rule


class RustTestAnnotations(Rule):
    id = "RUST_TS001"
    title = "at least one #[test] annotation under src/ or tests/"
    severity = "recommended"
    stacks = ("rust",)
    handbook_ref = "docs/handbook/11-rust.md#rust_ts001"

    def check(self, repo: Repo) -> CheckResult:
        hits = find_test_annotations(repo.path)
        if hits:
            try:
                rels = sorted(str(p.relative_to(repo.path)) for p in hits[:3])
            except ValueError:
                rels = sorted(str(p) for p in hits[:3])
            return CheckResult(
                passing=True,
                evidence=f"#[test] found in {len(hits)} file(s); sample: {rels}",
            )
        return CheckResult(
            passing=False,
            evidence="no #[test] annotation found under src/ or tests/",
        )
