# 05 — Tests

## Rules

### PYTHON_TS001 — `pytest` as test runner

**Severity:** required · **Stacks:** python

`pytest` is the canonical test runner. Configuration in
`[tool.pytest.ini_options]` of `pyproject.toml`. No `unittest`
discovery or `nose`.

### TS002 — Tests in `tests/`, regression in `regression_tests/`

**Severity:** recommended · **Stacks:** *

Unit and integration tests live in `tests/`. Regression tests
(snapshots, numerical parity) live in `regression_tests/`
at the root. Allows running only `tests/` quickly in CI and
reserving `regression_tests/` for nightly runs.

### PYTHON_TS003 — Coverage measured

**Severity:** recommended · **Stacks:** python

`pytest-cov` configured (section `[tool.coverage.run]`). No strict
threshold imposed: intendant measures and reports, the user sets the threshold
that makes sense for their project.
