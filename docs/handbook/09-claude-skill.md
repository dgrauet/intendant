# 09 — Skill (Claude Skill repositories)

Governance convention for repositories containing a standalone Claude Skill.
The skill adapter detects these repos by the presence of a `SKILL.md` file
at depth ≤ 2 (in Anthropic frontmatter YAML format).

## Rules

### CLAUDE_SKILL_SK001 — SKILL.md present

**Severity:** required · **Stacks:** claude-skill

The repo must contain at least one `SKILL.md` file at depth 1 or 2
(typically `<repo>/<skill-name>/SKILL.md`). Without this file, Claude cannot
load the skill.

### CLAUDE_SKILL_SK002 — Valid frontmatter

**Severity:** required · **Stacks:** claude-skill

The `SKILL.md` must begin with a `---` YAML block containing at minimum
the `name` and `description` fields, both non-empty. A broken frontmatter
prevents Claude from loading the skill.

### CLAUDE_SKILL_SK003 — Description quality

**Severity:** recommended · **Stacks:** claude-skill

The `description` field must be between 10 and 1024 characters. Too short
indicates a forgotten placeholder; too long gets truncated in the skills
listing exposed to the user.

### CLAUDE_SKILL_SK004 — `name` matches the folder

**Severity:** recommended · **Stacks:** claude-skill

The `name` field in the frontmatter must match the name of the parent
folder of the `SKILL.md`. A strong convention expected by the community;
not enforced by Claude but useful for readability.

### CLAUDE_SKILL_SK005 — Non-empty `evals/`

**Severity:** recommended · **Stacks:** claude-skill

An `evals/` folder next to the `SKILL.md` must exist and contain at
least one eval file (`.md`/`.json`/`.yaml`/`.txt`). Evals document
expected behaviors and enable regression detection.

### CLAUDE_SKILL_SK006 — Referenced folders exist

**Severity:** recommended · **Stacks:** claude-skill

If the `SKILL.md` mentions `references/` or `scripts/` in its body
(outside code blocks), those folders must exist next to the
`SKILL.md`. Prevents doc rot where the text promises files that are absent.

### CLAUDE_SKILL_SK007 — README documents the installation path

**Severity:** recommended · **Stacks:** claude-skill

The root `README.md` must mention either `~/.claude/skills/` or
`claude/plugins/` to help the user install the skill. An
auto-fix can append the standard installation block. If
`README.md` is absent, the rule is `skip` (DG003 covers the absence).
