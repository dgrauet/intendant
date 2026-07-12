# 04 — Quality

## Rules

### PYTHON_QU001 — `ruff` as linter and formatter

**Severity:** required · **Stacks:** python

`ruff` is the single tool for Python linting and formatting. Replaces `black`,
`isort`, `flake8`, and their plugins. Configuration in `[tool.ruff]` of
`pyproject.toml`. Minimum enabled rules: `E`, `F`, `I`, `N`, `UP`,
`B`, `SIM`, `RUF`.

### PYTHON_QU002 — `ty` as type-checker

**Severity:** required · **Stacks:** python · **ADR:** [0003-ty-with-pyright-fallback](../adr/0003-ty-with-pyright-fallback.md)

`ty` (Astral) is invoked via `uvx ty check`. `pyright` remains documented
as a fallback (see ADR-0003).

### PYTHON_QU003 — Strict type annotations

**Severity:** required · **Stacks:** python

All public function and method parameters are typed. All return types are
annotated (except `__init__`). No implicit `Any`. The type-checker's
strict mode is enabled.

### PYTHON_QU004 — `ty check` passes (Python type-checker)

**Severity:** recommended · **Stacks:** python · **ADR:** [0003-ty-with-pyright-fallback](../adr/0003-ty-with-pyright-fallback.md)

Runs `uvx ty check` in the repo. Passes if exit 0; fails with the diagnostic
count summary otherwise. Skipped silently if neither `ty` nor `pyright` is
declared in the project's dev dependencies (avoids forcing type-checking on
projects that haven't opted in).

This rule has no auto-fix — type errors are application logic that requires
human judgment. Use the rule as a CI gate once your codebase is type-clean.

### QU001 — configured quality tools are exercised in CI

**Severity:** recommended · **Stacks:** *

Every quality-tool configuration committed to the repo (`.swiftformat`,
`.swiftlint.yml`, `rustfmt.toml`, `clippy.toml`, `.golangci.yml`,
`deny.toml`, `ruff.toml` / `[tool.ruff]`, `biome.json`, eslint configs)
must correspond to a workflow step that actually runs the tool. A config
nobody executes gives a false sense of enforcement and silently rots —
the champinium `.swiftformat` sat unused while CI only ran `swift build`.
The scan covers the repo root and subdirectories (bounded depth, build
and vendored dirs skipped); universal files like `.editorconfig` are out
of scope to avoid false positives. Skipped when no workflows directory
exists (covered by `CI001`).
