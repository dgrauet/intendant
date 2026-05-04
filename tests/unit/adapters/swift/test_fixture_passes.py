"""Integration: the valid_swift_repo fixture must pass every Swift rule."""

from __future__ import annotations

from pathlib import Path

from suzerain.adapters.swift import RULES
from suzerain.audit.registry import collect_rules
from suzerain.core.repo import Repo

FIXTURE = Path(__file__).resolve().parents[3] / "fixtures" / "valid_swift_repo"


def test_fixture_detected_as_swift() -> None:
    assert Repo.from_path(FIXTURE).stack == "swift"


def test_every_swift_rule_passes_on_fixture() -> None:
    repo = Repo(path=FIXTURE, stack="swift")
    for rule in RULES:
        result = rule.check(repo)
        assert result.passing, f"{rule.id} failed on valid_swift_repo: {result.evidence}"


def test_swift_rules_registered_in_registry() -> None:
    rules = collect_rules()
    swift_ids = {r.id for r in rules if "swift" in r.stacks}
    assert {
        "SWIFT_PK001",
        "SWIFT_PK002",
        "SWIFT_PK003",
        "SWIFT_QU001",
        "SWIFT_TS001",
        "SWIFT_CI001",
        "SWIFT_SA001",
    }.issubset(swift_ids)
