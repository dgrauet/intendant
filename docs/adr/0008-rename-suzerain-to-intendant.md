# ADR-0008: Rename project from `suzerain` to `intendant`

- **Status:** Accepted
- **Date:** 2026-05-05

## Context

The project was originally published locally under the name `suzerain`. Investigation revealed that the PyPI name `suzerain` is already taken by an unrelated project (Amadeus Woo, *"What kind of AI ruler are you? Analyze your Claude Code governance patterns"*, last release 2026-01-15). The two projects sit in adjacent semantic space (Claude Code governance), making a PEP 541 name dispute non-viable.

Continuing under the same name would prevent ever publishing to PyPI, force ugly namespace prefixes, and create user confusion if both tools coexist in the wild.

## Decision

Rename the project to **`intendant`** — the French royal administrator who oversaw provinces and enforced central rules locally. The semantic match (rule-enforcement, oversight, audit) is preserved while the new name is unique on PyPI and brandable.

**Hard rename, no backwards compatibility.** Configuration filename moves from `.suzerain.toml` to `.intendant.toml` in a single commit. The CLI binary, Python package, MCP server name, and convention file all change at once.

## Consequences

### Breaking
- Every governed repository must rename its `.suzerain.toml` to `.intendant.toml`.
- The CLI is now `intendant` (was `suzerain`). Old `suzerain` invocations break.
- The MCP server registers as `intendant` — Claude Code MCP configuration must be updated.
- The Python import path is `import intendant` (was `import suzerain`).

### Preserved
- Git history is untouched; `Suzerain` references in ADRs, CHANGELOG, and past migration notes remain as historical record.
- Schema version (`schema_version` in audit reports) is unchanged.
- Rule IDs (`DG001`, `RL002`, etc.) are unchanged.

### Migration
At the moment of rename, only one repo (`mlx-arsenal`) was governed externally. Its `.suzerain.toml` was renamed in lockstep with this commit; no in-the-wild deployment exists.

## Alternatives considered

- **Namespace prefix** (`suzerain-cli`, `dgrauet-suzerain`) — rejected as ugly and not solving discoverability.
- **Soft rename with deprecation period** — rejected as unnecessary overhead given the single-repo blast radius.
- **PEP 541 dispute** — rejected; the existing project is active and adjacent in scope.
