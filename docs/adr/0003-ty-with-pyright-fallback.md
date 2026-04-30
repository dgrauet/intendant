# ADR-0003 : `ty` (Astral) as the Python type-checker, pyright as fallback

- **Statut** : accepted
- **Date** : 2026-04-30
- **Stacks concernées** : python

## Contexte

Le typage statique Python s'appuie typiquement sur `mypy` (mature, lent,
historique) ou `pyright` (Microsoft, rapide, gold standard IDE).
Astral développe `ty`, un type-checker en Rust qui s'inscrit dans la même
philosophie que `ruff` et `uv` : performance et cohérence d'écosystème.

Au moment de la décision (2026-04), `ty` est en pré-1.0 mais utilisable.
Le pari est de l'adopter dès maintenant pour bénéficier de la cohérence
de la suite Astral et de sa vitesse, en gardant `pyright` comme porte de
sortie documentée.

## Décision

- **Type-checker par défaut** : `ty` (invoqué via `uvx ty check` ou
  `uv tool install ty`).
- **Configuration** : `[tool.ty]` dans `pyproject.toml`, ou `ty.toml`
  séparé.
- **Fallback documenté** : `pyright` en version stricte, configuré dans
  `pyrightconfig.json` ou `[tool.pyright]`. À activer si `ty` introduit
  un blocage majeur (régression, faux positifs massifs, abandon).

## Conséquences

- CI roule `uvx ty check` (cf. `templates/github/ci.yml`).
- `pyproject.toml` peut déclarer `ty` en `[dependency-groups] dev`.
- Les annotations de type sont strictes (équivalent `--strict` en mypy
  parlance) : tous les paramètres typés, retours typés, pas d'`Any`
  implicite.

## Alternatives considérées

- `mypy` : mature mais lent. Perte d'élan face à pyright/ty.
- `pyright` : très bon, mais cohérence Astral l'emporte au moment de la
  décision.

## Porte de sortie / révision

Bascule vers `pyright` si **un seul** des critères suivants devient vrai :

1. `ty` introduit une régression bloquante non corrigée sous 2 semaines.
2. `ty` est officiellement abandonné par Astral.
3. Faux positifs > 10 % sur le code de suzerain pendant 3 versions
   consécutives.

Procédure de bascule : remplacer la dep + l'invocation CI + la config
section, mettre à jour cette ADR (statut `superseded by ADR-NNNN`),
ouvrir une nouvelle ADR `pyright-after-ty-rollback`.
