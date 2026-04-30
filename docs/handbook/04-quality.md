# 04 — Qualité

## Règles

### QU001 — `ruff` comme linter et formatter

**Severity:** required · **Stacks:** python

`ruff` est l'outil unique pour lint et format Python. Remplace `black`,
`isort`, `flake8`, et leurs plugins. Configuration dans `[tool.ruff]` du
`pyproject.toml`. Règles minimales activées : `E`, `F`, `I`, `N`, `UP`,
`B`, `SIM`, `RUF`.

### QU002 — `ty` comme type-checker

**Severity:** required · **Stacks:** python · **ADR:** [0003-ty-with-pyright-fallback](../adr/0003-ty-with-pyright-fallback.md)

`ty` (Astral) est invoqué via `uvx ty check`. `pyright` reste documenté
en porte de sortie (cf. ADR-0003).

### QU003 — Annotations de type strictes

**Severity:** required · **Stacks:** python

Tous les paramètres de fonctions et méthodes publiques sont typés. Tous
les retours sont typés (sauf `__init__`). Pas d'`Any` implicite. Le mode
strict du type-checker est activé.
