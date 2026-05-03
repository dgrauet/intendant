"""Skill adapter SK rules (SK001-SK007)."""

from __future__ import annotations

import re

import yaml

from suzerain.adapters.claude_skill.inspectors import find_skill_md, parse_frontmatter
from suzerain.core.patch import Patch
from suzerain.core.repo import Repo
from suzerain.core.rule import CheckResult, Rule

# Used by SK002 (raw-text frontmatter detection) and SK006 (strip frontmatter from body).
_FRONTMATTER_BLOCK_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)


class SK001SkillMdExists(Rule):
    id = "CLAUDE_SKILL_SK001"
    title = "SKILL.md exists at depth <= 2"
    severity = "required"
    stacks = ("claude-skill",)
    handbook_ref = "docs/handbook/09-claude-skill.md#claude_skill_sk001"

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
    id = "CLAUDE_SKILL_SK002"
    title = "SKILL.md frontmatter valid (name + description present and non-empty)"
    severity = "required"
    stacks = ("claude-skill",)
    handbook_ref = "docs/handbook/09-claude-skill.md#claude_skill_sk002"

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
    id = "CLAUDE_SKILL_SK003"
    title = "SKILL.md description length within 10-1024 chars"
    severity = "recommended"
    stacks = ("claude-skill",)
    handbook_ref = "docs/handbook/09-claude-skill.md#claude_skill_sk003"

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
    id = "CLAUDE_SKILL_SK004"
    title = "frontmatter name matches parent directory name"
    severity = "recommended"
    stacks = ("claude-skill",)
    handbook_ref = "docs/handbook/09-claude-skill.md#claude_skill_sk004"

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
    id = "CLAUDE_SKILL_SK005"
    title = "evals/ directory present and non-empty"
    severity = "recommended"
    stacks = ("claude-skill",)
    handbook_ref = "docs/handbook/09-claude-skill.md#claude_skill_sk005"

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


_DIR_REF_RE = re.compile(r"(?<!\S)(references|scripts)/[\w/.-]+")
_FENCED_BLOCK_RE = re.compile(r"```.*?```", re.DOTALL)


def _strip_frontmatter_and_codeblocks(text: str) -> str:
    """Return the SKILL.md body with frontmatter and fenced code blocks removed."""
    body = _FRONTMATTER_BLOCK_RE.sub("", text, count=1)
    body = _FENCED_BLOCK_RE.sub("", body)
    return body


class SK006ReferencedDirsExist(Rule):
    id = "CLAUDE_SKILL_SK006"
    title = "referenced top-level dirs (references/, scripts/) exist when mentioned"
    severity = "recommended"
    stacks = ("claude-skill",)
    handbook_ref = "docs/handbook/09-claude-skill.md#claude_skill_sk006"

    def check(self, repo: Repo) -> CheckResult:
        skill_md = find_skill_md(repo.path)
        if skill_md is None:
            return CheckResult(
                passing=True,
                skipped=True,
                evidence="no SKILL.md found (covered by SK001)",
            )
        text = skill_md.read_text(encoding="utf-8", errors="replace")
        if text.startswith("﻿"):
            text = text[1:]
        body = _strip_frontmatter_and_codeblocks(text)
        mentioned_top_levels = {m.group(1) for m in _DIR_REF_RE.finditer(body)}
        if not mentioned_top_levels:
            return CheckResult(
                passing=True,
                evidence="no references/ or scripts/ mentioned",
            )
        skill_dir = skill_md.parent
        missing = sorted(d for d in mentioned_top_levels if not (skill_dir / d).is_dir())
        if missing:
            return CheckResult(
                passing=False,
                evidence=f"SKILL.md references missing dirs: {missing}",
            )
        return CheckResult(passing=True, evidence="all referenced dirs present")


_INSTALL_BLOCK_TEMPLATE = """

## Installation

Clone into your local Claude skills directory:

```bash
git clone <repo-url> ~/.claude/skills/{skill_name}
```
"""


class SK007ReadmeInstallPath(Rule):
    id = "CLAUDE_SKILL_SK007"
    title = "README mentions skill install path (~/.claude/skills/ or claude/plugins/)"
    severity = "recommended"
    stacks = ("claude-skill",)
    handbook_ref = "docs/handbook/09-claude-skill.md#claude_skill_sk007"

    def check(self, repo: Repo) -> CheckResult:
        readme = repo.path / "README.md"
        if not readme.is_file():
            return CheckResult(
                passing=True,
                skipped=True,
                evidence="README.md not found at repo root (covered by DG003)",
            )
        text = readme.read_text(encoding="utf-8", errors="replace")
        if "~/.claude/skills/" in text or "claude/plugins/" in text:
            return CheckResult(passing=True, evidence="install path documented in README.md")
        return CheckResult(
            passing=False,
            evidence="README.md does not mention skill install path "
            "(~/.claude/skills/ or claude/plugins/)",
        )

    def fix(self, repo: Repo, result: CheckResult) -> Patch | None:
        # Re-check before patching: never patch when skipped (no README) or already passing.
        if result.skipped or result.passing:
            return None
        readme = repo.path / "README.md"
        if not readme.is_file():
            return None
        text = readme.read_text(encoding="utf-8", errors="replace")
        # Idempotency: if path is now present (race or stale result), no-op.
        if "~/.claude/skills/" in text or "claude/plugins/" in text:
            return None
        skill_md = find_skill_md(repo.path)
        skill_name = skill_md.parent.name if skill_md else "skill-name"
        addition = _INSTALL_BLOCK_TEMPLATE.format(skill_name=skill_name)
        new_content = text.rstrip() + addition
        return Patch(
            target_path=readme,
            kind="overwrite",
            content=new_content,
            diff=(f"--- a/README.md\n+++ b/README.md\n@@ +N @@\n{addition}"),
            safe=True,
        )
