# 07 — Releases

## Rules

### RL001 — `CHANGELOG.md` in Keep-a-Changelog format

**Severity:** required · **Stacks:** * · **ADR:** [0005-release-please](../adr/0005-release-please.md)

A `CHANGELOG.md` at the root, in
[Keep-a-Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/) format.
Entries are added by `release-please` from conventional commits.

### RL002 — Conventional Commits strict

**Severity:** required · **Stacks:** * · **ADR:** [0004-conventional-commits-strict](../adr/0004-conventional-commits-strict.md)

All commits follow
[Conventional Commits 1.0.0](https://www.conventionalcommits.org/).
Validated locally by `commitizen` (the `commit-msg` hook) and in CI by
`cz check`.

### RL003 — `release-please` configured

**Severity:** required · **Stacks:** * · **ADR:** [0005-release-please](../adr/0005-release-please.md)

The files `release-please-config.json` and
`.release-please-manifest.json` at the root, plus the workflow
`.github/workflows/release-please.yml`, automate versioning,
CHANGELOG, and git tagging.

### RL004 — Strict semantic versioning

**Severity:** required · **Stacks:** *

[SemVer 2.0.0](https://semver.org). `release-please` interprets
conventional commits: `fix:` → patch, `feat:` → minor, `feat!:` or
`BREAKING CHANGE:` → major.

The version is read from the first file found: `pyproject.toml`,
`package.json`, `Cargo.toml`, or `.release-please-manifest.json`
(`{".": "0.1.0"}` format). The manifest fallback enables RL004 to
apply to stacks without a primary language manifest (e.g. `claude-skill`).
If none of these files is present, the rule is skipped.
