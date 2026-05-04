# 06 — Sanitizing & secrets

## Rules

### SA001 — `pre-commit` configured and installed

**Severity:** required · **Stacks:** *

A `.pre-commit-config.yaml` file at the root defines at minimum:
`trailing-whitespace`, `end-of-file-fixer`, `check-yaml`, `check-toml`,
`detect-private-key`, and the language linter (ruff on the Python side).

### SA002 — Secret detection (gitleaks)

**Severity:** required · **Stacks:** *

`gitleaks` is included in pre-commit hooks. Prevents accidental
commits of API keys, tokens, and passwords.

### SA003 — `.env.example` without secrets

**Severity:** required · **Stacks:** *

If the project uses environment variables, a `.env.example` file
at the root documents the expected variable names with empty or
dummy values. The real `.env` is in `.gitignore`.

### SA004 — `.gitignore` generic baseline

**Severity:** required · **Stacks:** *

The root `.gitignore` must contain `.DS_Store`. This is the universal
baseline applicable to all stacks. Stack-specific patterns are enforced
by the stack adapter rules below.

### PYTHON_SA001 — Python `.gitignore` baseline

**Severity:** required · **Stacks:** python

The root `.gitignore` must contain the Python-specific baseline patterns:
`__pycache__/` and `.venv/`. Skipped when `.gitignore` does not exist
(covered by SA004).

### NODE_SA001 — Node `.gitignore` baseline

**Severity:** required · **Stacks:** node

The root `.gitignore` must contain the Node-specific baseline patterns:
`node_modules/` and `dist/`. Skipped when `.gitignore` does not exist
(covered by SA004).
