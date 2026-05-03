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

### SA004 — `.gitignore` baseline

**Severity:** required · **Stacks:** *

The root `.gitignore` must contain the baseline patterns appropriate for
the stack:

- **python**: `__pycache__/`, `.DS_Store`, `.venv/`.
- **node**: `node_modules/`, `.DS_Store`, `dist/`.
- **other** (claude-skill, auto, generic): `.DS_Store` only.
