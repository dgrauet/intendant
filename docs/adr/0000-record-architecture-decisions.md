# ADR-0000 : Record architecture decisions

- **Statut** : accepted
- **Date** : 2026-04-30
- **Stacks concernées** : * (transverse)

## Contexte

Suzerain produit des règles exécutables et une documentation humaine. Toute
règle est traçable jusqu'à une décision d'architecture explicite. Sans ADRs,
la rationale derrière les règles se perd, les évolutions deviennent
arbitraires et la gouvernance perd sa légitimité.

## Décision

On adopte le format ADR (Architecture Decision Records, popularisé par
Michael Nygard) avec une légère extension :

- Numérotation séquentielle `NNNN` à 4 chiffres, jamais réutilisée.
- Statut : `proposed | accepted | superseded by ADR-MMMM | deprecated`.
- Une rubrique non standard **Porte de sortie / révision** documente ce qui
  ferait reconsidérer la décision.

Le template canonique vit dans `templates/_common/adr.md`.

## Conséquences

- Toute nouvelle règle suzerain pointe vers une ADR via `RuleSection.adr_ref`.
- Le test e2e `tests/unit/test_handbook.py` peut vérifier que chaque ADR
  référencée existe (à ajouter au palier 2).
- Les ADRs ne sont pas modifiées rétroactivement : on les supersede ou
  déprécie.

## Alternatives considérées

- Pas d'ADRs : trop d'informel, gouvernance non auditable.
- ADRs sans numérotation séquentielle : casse l'ordre temporel et la
  citation stable depuis les règles.

## Porte de sortie / révision

- Si un format alternatif (Y-statements, etc.) émerge comme standard
  industriel, migrer toutes les ADRs en bloc.
