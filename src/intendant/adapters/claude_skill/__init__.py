"""Skill adapter — Claude Skill repository rules."""

from __future__ import annotations

from intendant.adapters.claude_skill.ci import CLAUDE_SKILL_CI001MinimumSteps
from intendant.adapters.claude_skill.sk import (
    SK001SkillMdExists,
    SK002FrontmatterValid,
    SK003DescriptionQuality,
    SK004NameMatchesDir,
    SK005EvalsNonEmpty,
    SK006ReferencedDirsExist,
    SK007ReadmeInstallPath,
)
from intendant.core.rule import Rule

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
