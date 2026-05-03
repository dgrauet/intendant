# 01 — Layout

Folder structure convention for projects governed by suzerain.

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
