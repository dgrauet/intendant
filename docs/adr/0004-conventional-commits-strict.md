# ADR-0004 : Conventional Commits strict (commitizen + commitlint)

- **Statut** : accepted
- **Date** : 2026-04-30
- **Stacks concernées** : * (transverse)

## Contexte

Sans format de commit standardisé, le CHANGELOG ne peut pas être
auto-généré, la sémantique des bumps de version est manuelle et
sujette à erreur, et la lecture de l'historique est plus pénible.
Conventional Commits (`<type>(<scope>): <subject>`) résout ces trois
problèmes mais ne fonctionne que si l'enforcement est strict.

## Décision

- **Format** : Conventional Commits 1.0.0
  (https://www.conventionalcommits.org/).
- **Types acceptés** : `feat`, `fix`, `docs`, `chore`, `refactor`, `test`,
  `ci`, `perf`, `build`, `style`, `revert`.
- **Enforcement à 2 niveaux** :
  1. **Local** : hook `pre-commit` (stage `commit-msg`) avec
     `commitizen-tools/commitizen` (côté Python) ou `commitlint`
     (côté Node).
  2. **CI** : job `commit-lint` qui valide les messages des commits de la
     PR via `cz check --rev-range origin/main..HEAD`.
- **Squash merge sur GitHub** : titre de PR conforme requis (devient le
  message de squash commit).

## Conséquences

- `release-please` (ADR-0005) consomme directement ces commits pour
  générer le CHANGELOG et bumper la version.
- Les contributeurs doivent apprendre le format. Compensé par `cz commit`
  qui guide en interactif.
- Les commits `fix:` bumpent le patch, `feat:` bumpent le minor, et
  `feat!:` ou `BREAKING CHANGE:` dans le footer bumpent le major.

## Alternatives considérées

- Format informel : abandonné, casse l'auto-CHANGELOG.
- Format `gitmoji` : moins standard, mauvaise interop avec release-please.

## Porte de sortie / révision

- Si une équipe collaboratrice rejette la friction, basculer en mode
  "recommandé" (hook local seulement, pas de CI bloquante). Ne pas
  abandonner le format lui-même.
