"""Smoke test that the skill adapter package imports cleanly."""

from suzerain.adapters.skill import RULES


def test_skill_adapter_exports_rules_list() -> None:
    assert isinstance(RULES, list)
    assert RULES == []
