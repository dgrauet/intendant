"""Skill adapter SK rules (SK001-SK007)."""

from __future__ import annotations

import re

import yaml

from suzerain.adapters.skill.inspectors import find_skill_md, parse_frontmatter
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


class SK002FrontmatterValid(Rule):
    id = "SK002"
    title = "SKILL.md frontmatter valid (name + description present and non-empty)"
    severity = "required"
    stacks = ("skill",)
    handbook_ref = "docs/handbook/09-skill.md#sk002"

    def check(self, repo: Repo) -> CheckResult:
        skill_md = find_skill_md(repo.path)
        if skill_md is None:
            return CheckResult(passing=False, evidence="no SKILL.md found")
        text = skill_md.read_text(encoding="utf-8", errors="replace")
        if text.startswith("﻿"):
            text = text[1:]
        match = _FRONTMATTER_BLOCK_RE.match(text)
        if not match:
            return CheckResult(passing=False, evidence="no frontmatter block found")
        try:
            data = yaml.safe_load(match.group(1))
        except yaml.YAMLError as exc:
            return CheckResult(passing=False, evidence=f"YAML parse error: {exc}")
        if not isinstance(data, dict):
            return CheckResult(
                passing=False,
                evidence="frontmatter root is not a YAML mapping",
            )
        for field in ("name", "description"):
            if field not in data:
                return CheckResult(
                    passing=False,
                    evidence=f"missing required field: {field}",
                )
            value = data[field]
            if value is None or (isinstance(value, str) and value.strip() == ""):
                return CheckResult(
                    passing=False,
                    evidence=f"field {field!r} is empty",
                )
        name = data["name"]
        desc = data["description"]
        return CheckResult(
            passing=True,
            evidence=f"frontmatter valid: name={name!r}, description='{len(str(desc))} chars'",
        )


class SK003DescriptionQuality(Rule):
    id = "SK003"
    title = "SKILL.md description length within 10-1024 chars"
    severity = "recommended"
    stacks = ("skill",)
    handbook_ref = "docs/handbook/09-skill.md#sk003"

    def check(self, repo: Repo) -> CheckResult:
        skill_md = find_skill_md(repo.path)
        if skill_md is None:
            return CheckResult(
                passing=True,
                skipped=True,
                evidence="no SKILL.md found (covered by SK001)",
            )
        data = parse_frontmatter(skill_md)
        if data is None or "description" not in data:
            return CheckResult(
                passing=True,
                skipped=True,
                evidence="frontmatter or description absent (covered by SK002)",
            )
        desc = str(data["description"]).strip()
        n = len(desc)
        if n < 10:
            return CheckResult(
                passing=False,
                evidence=f"description too short: {n} chars (min 10)",
            )
        if n > 1024:
            return CheckResult(
                passing=False,
                evidence=f"description too long: {n} chars (max 1024)",
            )
        return CheckResult(passing=True, evidence=f"description length: {n} chars")


class SK004NameMatchesDir(Rule):
    id = "SK004"
    title = "frontmatter name matches parent directory name"
    severity = "recommended"
    stacks = ("skill",)
    handbook_ref = "docs/handbook/09-skill.md#sk004"

    def check(self, repo: Repo) -> CheckResult:
        skill_md = find_skill_md(repo.path)
        if skill_md is None:
            return CheckResult(
                passing=True,
                skipped=True,
                evidence="no SKILL.md found (covered by SK001)",
            )
        data = parse_frontmatter(skill_md)
        if data is None or "name" not in data:
            return CheckResult(
                passing=True,
                skipped=True,
                evidence="frontmatter or name absent (covered by SK002)",
            )
        frontmatter_name = str(data["name"])
        dir_name = skill_md.parent.name
        if frontmatter_name == dir_name:
            return CheckResult(passing=True, evidence=f"name matches directory: {dir_name!r}")
        return CheckResult(
            passing=False,
            evidence=f"name {frontmatter_name!r} does not match directory {dir_name!r}",
        )


_EVAL_EXTENSIONS = frozenset({".md", ".json", ".yaml", ".yml", ".txt"})


class SK005EvalsNonEmpty(Rule):
    id = "SK005"
    title = "evals/ directory present and non-empty"
    severity = "recommended"
    stacks = ("skill",)
    handbook_ref = "docs/handbook/09-skill.md#sk005"

    def check(self, repo: Repo) -> CheckResult:
        skill_md = find_skill_md(repo.path)
        if skill_md is None:
            return CheckResult(
                passing=True,
                skipped=True,
                evidence="no SKILL.md found (covered by SK001)",
            )
        evals_dir = skill_md.parent / "evals"
        if not evals_dir.is_dir():
            return CheckResult(passing=False, evidence="evals/ directory missing")
        files = [p for p in evals_dir.iterdir() if p.is_file() and p.suffix in _EVAL_EXTENSIONS]
        if not files:
            return CheckResult(
                passing=False,
                evidence="evals/ directory exists but empty (no .md/.json/.yaml/.txt files)",
            )
        return CheckResult(passing=True, evidence=f"evals/ present with {len(files)} file(s)")
