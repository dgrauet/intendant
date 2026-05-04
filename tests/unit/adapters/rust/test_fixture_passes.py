"""Integration: the valid_rust_repo fixture must pass every Rust rule."""

from __future__ import annotations

from pathlib import Path

from suzerain.adapters.rust import RULES
from suzerain.audit.registry import collect_rules
from suzerain.core.repo import Repo

FIXTURE = Path(__file__).resolve().parents[3] / "fixtures" / "valid_rust_repo"


def test_fixture_detected_as_rust() -> None:
    assert Repo.from_path(FIXTURE).stacks == ("rust",)


def test_every_rust_rule_passes_on_fixture() -> None:
    repo = Repo(path=FIXTURE, stacks=("rust",))
    for rule in RULES:
        result = rule.check(repo)
        assert result.passing, f"{rule.id} failed on valid_rust_repo: {result.evidence}"


def test_rust_rules_registered_in_registry() -> None:
    rules = collect_rules()
    rust_ids = {r.id for r in rules if "rust" in r.stacks}
    assert {
        "RUST_PK001",
        "RUST_PK002",
        "RUST_PK003",
        "RUST_QU001",
        "RUST_TS001",
        "RUST_CI001",
        "RUST_SA001",
    }.issubset(rust_ids)
