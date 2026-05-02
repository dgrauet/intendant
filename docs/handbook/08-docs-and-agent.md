# 08 — Docs & internal governance

## Rules

### DG001 — Structured `README.md`

**Severity:** required · **Stacks:** *

The root `README.md` contains at minimum: a one-sentence description,
the status, installation instructions, a quickstart, a link to the full
documentation, and the license.

### DG002 — `CLAUDE.md` for agent context

**Severity:** recommended · **Stacks:** *

If the project is explored by Claude Code, a `CLAUDE.md` at the root
describes the stack, house rules, main commands (tests,
lint, build), and non-trivial conventions.

### DG003 — `docs/adr/` for architecture decisions

**Severity:** required · **Stacks:** * · **ADR:** [0000-record-architecture-decisions](../adr/0000-record-architecture-decisions.md)

Every non-trivial architecture decision is documented as an ADR
in `docs/adr/NNNN-<slug>.md`. Format: see ADR-0000 and the template
`templates/_common/adr.md`.

### DG004 — `LICENSE` at the root

**Severity:** required · **Stacks:** *

A `LICENSE` file at the root declares the license. The `license`
field in `pyproject.toml` (or equivalent) must match.

### DG005 — Specs and plans local-only

**Severity:** required · **Stacks:** *

Files under `docs/superpowers/specs/` and `docs/superpowers/plans/`
are never pushed to public remotes. A `pre-push` hook blocks pushes
containing them to `origin/main`. Policy born of an explicit user
preference: these artifacts contain brainstorming and internal plans
that must not leak.
