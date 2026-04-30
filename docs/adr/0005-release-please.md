# ADR-0005 : `release-please` for versioning + CHANGELOG + GitHub release

- **Statut** : accepted
- **Date** : 2026-04-30
- **Stacks concernées** : * (transverse, multi-stack natif)

## Contexte

Le cycle de release implique : bumper la version, mettre à jour le
CHANGELOG, créer un tag git, créer une release GitHub, optionnellement
publier le paquet. Faire cela à la main multiplie les erreurs (versions
manquantes, CHANGELOG incohérent, tag oublié).

Trois candidats principaux pour l'automatiser :

| Outil | Forces | Faiblesses |
|---|---|---|
| `semantic-release` | Mature, écosystème JS riche | Node-centric, pull une toolchain Node dans des repos Python |
| `git-cliff` | Rust, rapide, génère CHANGELOG | Ne gère ni bump version ni tag — workflow manuel à compléter |
| `release-please` | Multi-stack (Python, Node, Go, Rust...), GH Action native, ouvre une release PR auditable | Couplé à GitHub |

## Décision

`release-please` est l'outil canonique. Configuration par repo :
`release-please-config.json` + `.release-please-manifest.json`. Workflow
GH Actions livré dans `templates/github/release-please.yml`.

Workflow par release :

1. Commits sur `main` au format Conventional Commits (ADR-0004).
2. `release-please` ouvre une **release PR** qui bump la version et met
   à jour le CHANGELOG.
3. La release PR est mergée → tag créé, release GitHub créée.

## Conséquences

- `CHANGELOG.md` au format Keep-a-Changelog ; `release-please` y écrit
  les sections `[X.Y.Z] - YYYY-MM-DD`.
- La version vit dans le manifest et est synchronisée avec
  `pyproject.toml` (option `release-type: python`).
- Pas de bump manuel de version. Toujours via la release PR.

## Alternatives considérées

Cf. tableau en Contexte.

## Porte de sortie / révision

- Si suzerain ou un repo géré quitte GitHub, migrer vers `git-cliff`
  + script de bump maison. Documenter la procédure de migration.
