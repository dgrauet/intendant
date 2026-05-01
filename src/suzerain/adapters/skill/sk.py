"""Skill adapter SK rules (SK001-SK007)."""

from __future__ import annotations

import re

from suzerain.adapters.skill.inspectors import find_skill_md
from suzerain.core.repo import Repo
from suzerain.core.rule import CheckResult, Rule

# Used by SK002 (raw-text frontmatter detection) and SK006 (strip frontmatter from body).
_FRONTMATTER_BLOCK_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)


class SK001SkillMdExists(Rule):
    id = "SK001"
    title = "SKILL.md exists at depth <= 2"
    severity = "required"
    stacks = ("skill",)
    handbook_ref = "docs/handbook/09-skill.md#sk001"

    def check(self, repo: Repo) -> CheckResult:
        skill_md = find_skill_md(repo.path)
        if skill_md is None:
            return CheckResult(
                passing=False,
                evidence=(
                    "no SKILL.md found at depth <= 2 (excluding .git, node_modules, "
                    "__pycache__, .venv, .tox, dist, build)"
                ),
            )
        rel = skill_md.relative_to(repo.path)
        return CheckResult(passing=True, evidence=f"skill detected at {rel}")
