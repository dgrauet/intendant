"""Skill adapter — Claude Skill repository rules."""

from __future__ import annotations

from suzerain.adapters.claude_skill.ci import CLAUDE_SKILL_CI001MinimumSteps
from suzerain.adapters.claude_skill.sk import (
    SK001SkillMdExists,
    SK002FrontmatterValid,
    SK003DescriptionQuality,
    SK004NameMatchesDir,
    SK005EvalsNonEmpty,
    SK006ReferencedDirsExist,
    SK007ReadmeInstallPath,
)
from suzerain.core.rule import Rule

RULES: list[Rule] = [
    SK001SkillMdExists(),
    SK002FrontmatterValid(),
    SK003DescriptionQuality(),
    SK004NameMatchesDir(),
    SK005EvalsNonEmpty(),
    SK006ReferencedDirsExist(),
    SK007ReadmeInstallPath(),
    CLAUDE_SKILL_CI001MinimumSteps(),
]
