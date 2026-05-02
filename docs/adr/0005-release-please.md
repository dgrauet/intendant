# ADR-0005 : `release-please` for versioning + CHANGELOG + GitHub release

- **Status** : accepted
- **Date** : 2026-04-30
- **Stacks** : * (transverse, natively multi-stack)

## Context

The release cycle involves: bumping the version, updating the
CHANGELOG, creating a git tag, creating a GitHub release, optionally
publishing the package. Doing this manually multiplies errors (missing
versions, inconsistent CHANGELOG, forgotten tag).

Three main candidates to automate it:

| Tool | Strengths | Weaknesses |
|---|---|---|
| `semantic-release` | Mature, rich JS ecosystem | Node-centric, pulls a Node toolchain into Python repos |
| `git-cliff` | Rust, fast, generates CHANGELOG | Does not handle version bumping or tagging — manual workflow needed |
| `release-please` | Multi-stack (Python, Node, Go, Rust...), native GH Action, opens an auditable release PR | Coupled to GitHub |

## Decision

`release-please` is the canonical tool. Per-repo configuration:
`release-please-config.json` + `.release-please-manifest.json`. GH Actions
workflow delivered in `templates/github/release-please.yml`.

Release workflow:

1. Commits to `main` in Conventional Commits format (ADR-0004).
2. `release-please` opens a **release PR** that bumps the version and updates
   the CHANGELOG.
3. The release PR is merged → tag created, GitHub release created.

## Consequences

- `CHANGELOG.md` in Keep-a-Changelog format; `release-please` writes
  the `[X.Y.Z] - YYYY-MM-DD` sections.
- The version lives in the manifest and is synchronized with
  `pyproject.toml` (option `release-type: python`).
- No manual version bumping. Always via the release PR.

## Alternatives considered

See table in Context.

## Exit hatch / revision

- If suzerain or a managed repo leaves GitHub, migrate to `git-cliff`
  + a custom bump script. Document the migration procedure.
