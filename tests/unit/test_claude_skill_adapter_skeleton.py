"""Smoke test that the skill adapter package imports cleanly."""

from suzerain.adapters.claude_skill import RULES


def test_claude_skill_adapter_exports_rules_list() -> None:
    assert isinstance(RULES, list)
    assert len(RULES) == 7
