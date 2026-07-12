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

The auto-fix (`intendant fix`) applies the two protections in order via a
2-pass approach: the first call patches `.gitignore`; the second call patches
`.gitattributes`. Run `--fix` twice to fully resolve a fresh violation.

### DG006 — doc version claims match the release manifest

**Severity:** optional · **Stacks:** *

When `README.md` or `CLAUDE.md` asserts the project's own version — a
"last release vX.Y.Z" statement, a `version: vX.Y.Z` field, or a status
line opening with `vX.Y.Z —` — the claim must match the current version
in `.release-please-manifest.json`. Stale claims mislead agents and
contributors (champinium's CLAUDE.md announced v0.2.0 four releases
late). Bare `vX.Y.Z` tokens without a release/version context (dependency
pins, SHA-pin comments) are not claims. The durable fix is usually to
drop the hardcoded version rather than chase it at every release.
Skipped when no release manifest exists (covered by `RL003`).
