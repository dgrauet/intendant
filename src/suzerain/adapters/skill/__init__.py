"""Skill adapter — Claude Skill repository rules."""

from __future__ import annotations

from suzerain.adapters.skill.sk import SK001SkillMdExists, SK002FrontmatterValid
from suzerain.core.rule import Rule

RULES: list[Rule] = [
    SK001SkillMdExists(),
    SK002FrontmatterValid(),
]
