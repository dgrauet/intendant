# 05 — Tests

## Règles

### TS001 — `pytest` comme test runner

**Severity:** required · **Stacks:** python

`pytest` est le test runner canonique. Configuration dans
`[tool.pytest.ini_options]` du `pyproject.toml`. Pas de `unittest`
discovery ni `nose`.

### TS002 — Tests dans `tests/`, regression dans `regression_tests/`

**Severity:** recommended · **Stacks:** *

Les tests unitaires et d'intégration vivent dans `tests/`. Les tests de
régression (snapshots, parité numérique) vivent dans `regression_tests/`
à la racine. Permet de ne lancer que `tests/` rapidement en CI et de
réserver `regression_tests/` aux runs nightly.

### TS003 — Couverture mesurée

**Severity:** recommended · **Stacks:** python

`pytest-cov` configuré (section `[tool.coverage.run]`). Pas de seuil
strict imposé : suzerain mesure et reporte, l'utilisateur fixe le seuil
qui a du sens pour son projet.
