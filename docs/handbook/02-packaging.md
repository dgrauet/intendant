# 02 — Packaging & dependencies

## Rules

### PK001 — `pyproject.toml` at the root (Python)

**Severity:** required · **Stacks:** python · **ADR:** [0002-uv-as-dependency-manager](../adr/0002-uv-as-dependency-manager.md)

A PEP 621-compliant `pyproject.toml` (with a `[project]` section) must exist at
the root. Minimum fields: `name`, `version`, `description`, `requires-python`,
`license`, `dependencies`.

### PK002 — `uv.lock` versioned (Python)

**Severity:** required · **Stacks:** python · **ADR:** [0002-uv-as-dependency-manager](../adr/0002-uv-as-dependency-manager.md)

The `uv.lock` file produced by `uv lock` is committed to the repo. Guarantees
reproducible installs and enables security audits by package hash.

### PK003 — Python version pinned

**Severity:** required · **Stacks:** python

The `.python-version` file at the root pins the Python version used
locally and in CI. The same value appears in `pyproject.toml`
(`requires-python`) and in the CI workflow.

### PK004 — No `requirements.txt`

**Severity:** recommended · **Stacks:** python · **ADR:** [0002-uv-as-dependency-manager](../adr/0002-uv-as-dependency-manager.md)

`requirements.txt` is not the source of truth. If a legacy system
requires it, generate it on the fly via `uv export -o requirements.txt`
(and mark the file in `.gitignore`).
