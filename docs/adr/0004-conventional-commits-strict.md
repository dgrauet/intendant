# ADR-0004 : Conventional Commits strict (commitizen + commitlint)

- **Status** : accepted
- **Date** : 2026-04-30
- **Stacks** : * (transverse)

## Context

Without a standardized commit format, the CHANGELOG cannot be
auto-generated, version bump semantics are manual and error-prone, and
reading the history is more painful.
Conventional Commits (`<type>(<scope>): <subject>`) solves these three
problems but only works if enforcement is strict.

## Decision

- **Format**: Conventional Commits 1.0.0
  (https://www.conventionalcommits.org/).
- **Accepted types**: `feat`, `fix`, `docs`, `chore`, `refactor`, `test`,
  `ci`, `perf`, `build`, `style`, `revert`.
- **Two-level enforcement**:
  1. **Local**: `pre-commit` hook (stage `commit-msg`) with
     `commitizen-tools/commitizen` (Python side) or `commitlint`
     (Node side).
  2. **CI**: `commit-lint` job that validates commit messages in the
     PR via `cz check --rev-range origin/main..HEAD`.
- **Squash merge on GitHub**: PR title must be compliant (becomes the
  squash commit message).

## Consequences

- `release-please` (ADR-0005) consumes these commits directly to
  generate the CHANGELOG and bump the version.
- Contributors must learn the format. Mitigated by `cz commit`
  which guides interactively.
- `fix:` commits bump the patch, `feat:` bump the minor, and
  `feat!:` or `BREAKING CHANGE:` in the footer bump the major.

## Alternatives considered

- Informal format: abandoned, breaks auto-CHANGELOG.
- `gitmoji` format: less standard, poor interop with release-please.

## Exit hatch / revision

- If a collaborating team rejects the friction, switch to "recommended"
  mode (local hook only, no blocking CI). Do not abandon the format itself.
