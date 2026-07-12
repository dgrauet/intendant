"""Integration: the valid_dotnet_repo fixture must pass every .NET rule."""

from __future__ import annotations

from pathlib import Path

from intendant.adapters.dotnet import RULES
from intendant.audit.registry import collect_rules
from intendant.core.repo import Repo

FIXTURE = Path(__file__).resolve().parents[3] / "fixtures" / "valid_dotnet_repo"


def test_fixture_detected_as_dotnet() -> None:
    assert Repo.from_path(FIXTURE).stacks == ("dotnet",)


def test_every_dotnet_rule_passes_on_fixture() -> None:
    repo = Repo(path=FIXTURE, stacks=("dotnet",))
    for rule in RULES:
        result = rule.check(repo)
        assert result.passing, f"{rule.id} failed on valid_dotnet_repo: {result.evidence}"


def test_dotnet_rules_registered_in_registry() -> None:
    rules = collect_rules()
    dotnet_ids = {r.id for r in rules if "dotnet" in r.stacks}
    assert {
        "DOTNET_PK001",
        "DOTNET_PK002",
        "DOTNET_QU001",
        "DOTNET_QU002",
        "DOTNET_TS001",
        "DOTNET_CI001",
        "DOTNET_SA001",
    }.issubset(dotnet_ids)
