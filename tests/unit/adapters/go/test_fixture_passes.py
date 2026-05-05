"""Integration: the valid_go_repo fixture must pass every Go rule."""

from __future__ import annotations

from pathlib import Path

from intendant.adapters.go import RULES
from intendant.audit.registry import collect_rules
from intendant.core.repo import Repo

FIXTURE = Path(__file__).resolve().parents[3] / "fixtures" / "valid_go_repo"


def test_fixture_detected_as_go() -> None:
    assert Repo.from_path(FIXTURE).stacks == ("go",)


def test_every_go_rule_passes_on_fixture() -> None:
    repo = Repo(path=FIXTURE, stacks=("go",))
    for rule in RULES:
        result = rule.check(repo)
        assert result.passing, f"{rule.id} failed on valid_go_repo: {result.evidence}"


def test_go_rules_registered_in_registry() -> None:
    rules = collect_rules()
    go_ids = {r.id for r in rules if "go" in r.stacks}
    assert {
        "GO_PK001",
        "GO_PK002",
        "GO_PK003",
        "GO_QU001",
        "GO_TS001",
        "GO_CI001",
        "GO_SA001",
    }.issubset(go_ids)
