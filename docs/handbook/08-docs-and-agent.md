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

Files under `docs/superpowers/` are never pushed to public remotes.
When the directory exists, two complementary protections are required:
a `docs/superpowers/` line in `.gitignore` (prevents accidental `git add`
day-to-day) and a `docs/superpowers/ export-ignore` line in `.gitattributes`
(excludes the directory from `git archive` release tarballs).

The auto-fix (`suzerain fix`) applies the two protections in order via a
2-pass approach: the first call patches `.gitignore`; the second call patches
`.gitattributes`. Run `--fix` twice to fully resolve a fresh violation.
