# CLAUDE.md — suzerain

Contexte agent pour le repo suzerain.

## Quoi

Framework de gouvernance multi-stack. Ce repo définit, héberge et exécute les standards qui régissent les autres projets de `~/Work/`.

## Règles maison

- **Specs et plans local-only** : `docs/superpowers/specs/` et `docs/superpowers/plans/` ne sont JAMAIS poussés sur le remote public. Rebase la branche sur `origin/main` avant push.
- **TDD strict** sur le code Python du CLI (`src/suzerain/`). Tout nouveau composant moteur arrive avec son test rouge d'abord.
- **Conventional commits strict**. Le hook `commit-msg` rejette les commits non conformes.
- **Suzerain mange sa propre nourriture** : suzerain est gouverné par son propre `.suzerain.toml` (`mode = "strict"`).
- **Type-checker** : `ty` (Astral) en V1. `pyright` documenté en porte de sortie (ADR-0003).

## Stack

- Python 3.13, uv (deps + lockfile mandatory)
- ruff (lint+format), ty (type-check), pytest (tests)
- pre-commit, commitizen, release-please

## Tests

```bash
uv run pytest                  # tous les tests
uv run pytest tests/unit -v    # unit only
uv run pytest --cov            # avec couverture
```

## Lint & type

```bash
uv run ruff check .
uv run ruff format --check .
uvx ty check                   # ou: uv run ty check (selon installation)
```

## Référence design

- Spec : `docs/superpowers/specs/2026-04-30-suzerain-design.md`
- Plan palier 1 : `docs/superpowers/plans/2026-04-30-suzerain-palier1.md`
