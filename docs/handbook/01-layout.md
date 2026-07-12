# 01 — Layout

Folder structure convention for projects governed by intendant.

## Rules

### PYTHON_LO001 — `src/` layout required (Python)

**Severity:** required · **Stacks:** python · **ADR:** [0001-layout-src-vs-flat](../adr/0001-layout-src-vs-flat.md)

Source code lives in `src/<package_name>/`, never at the root. Tests
live in `tests/` at the root. See ADR-0001 for the rationale.

### PYTHON_LO002 — Tests in `tests/` at the root

**Severity:** required · **Stacks:** python · **ADR:** [0001-layout-src-vs-flat](../adr/0001-layout-src-vs-flat.md)

Tests live in a `tests/` folder at the repo root. No co-location
with the source code. Enables a clear separation and prevents tests
from being accidentally packaged.

### LO003 — Documentation in `docs/`

**Severity:** recommended · **Stacks:** *

All long-form documentation (handbook, ADRs, specs, tutorials) lives in
`docs/`. The root `README.md` remains a short entry point that links
to `docs/`.

### LO004 — nested stack roots covered by declared governance

**Severity:** recommended · **Stacks:** *

Every nested directory holding a stack marker (`pyproject.toml`,
`package.json`, `Cargo.toml`, `go.mod`, `Package.swift`, `*.csproj`/`*.sln`)
must be covered by a declared stack at that directory or one of its
ancestors: a `[[subprojects]]` entry, the top-level `stack` pin, or the
auto-detected root composition. An uncovered ("orphan") stack root is a
sub-project that silently escapes governance — declare it or exempt the
rule with a reason. The scan is bounded (5 levels) and skips build output
and vendored dependencies (`target/`, `node_modules/`, `bin/`, `obj/`, …).
