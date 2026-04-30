# ADR-0002 : `uv` as the Python dependency manager

- **Statut** : accepted
- **Date** : 2026-04-30
- **Stacks concernées** : python

## Contexte

L'écosystème Python a longtemps souffert d'une fragmentation des outils de
packaging (`pip`, `pipenv`, `poetry`, `pdm`, `hatch`, `rye`...). Chacun a
ses forces, mais maintenir une cohérence cross-projet exige un choix
unique. `uv` (Astral, Rust) consolide création de venv + résolution + lock
+ install en un binaire unique, considérablement plus rapide que les
alternatives, avec un format `pyproject.toml` standard.

## Décision

`uv` est l'outil canonique pour :

- Créer et synchroniser le venv (`uv sync`).
- Locker les dépendances (`uv.lock`, **commité au repo**, obligatoire).
- Exécuter les commandes locales (`uv run <cmd>`).
- Installer suzerain et les outils CLI (`uv tool install`).

`pip` n'est plus utilisé en local pour les projets régis par suzerain.
`requirements.txt` peut être généré (`uv export`) pour interop avec des
systèmes legacy.

## Conséquences

- Tous les projets ont un `uv.lock` versionné.
- Les CI installent `uv` puis font `uv sync` (workflow type au palier 1
  livré dans `templates/github/ci.yml`).
- `pyproject.toml` utilise `[dependency-groups]` (PEP 735) plutôt que
  `[project.optional-dependencies]` pour les deps dev.

## Alternatives considérées

- `poetry` : mature mais lent ; format `pyproject.toml` moins standard
  (`tool.poetry` au lieu de `project`).
- `pdm` : bon mais moins de momentum communautaire.
- `pip + pip-tools` : pas de venv intégré, deux outils à coordonner.

## Porte de sortie / révision

- Si `uv` cesse d'être maintenu ou si Astral pivote, basculer vers `pdm`
  (le plus proche en philosophie) avec un script de migration `uv export`
  + `pdm import`.
