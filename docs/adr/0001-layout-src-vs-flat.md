# ADR-0001 : Layout `src/` over flat layout

- **Statut** : accepted
- **Date** : 2026-04-30
- **Stacks concernées** : python

## Contexte

Les projets Python peuvent organiser leur code soit en flat layout
(`mypackage/__init__.py` à la racine), soit en src layout
(`src/mypackage/__init__.py`). Le flat layout est historiquement répandu
mais cause des erreurs subtiles : pytest peut importer le code source
plutôt que le package installé, masquant des bugs de packaging.

## Décision

Tous les projets Python neufs ou refactorés utilisent le **src layout**.
Les fichiers de tests vivent à la racine dans `tests/`.

```
project/
├── src/
│   └── package_name/
│       └── __init__.py
└── tests/
    └── test_*.py
```

## Conséquences

- `pyproject.toml` doit déclarer `[tool.hatch.build.targets.wheel] packages = ["src/package_name"]`
  (ou équivalent selon le build backend).
- `[tool.pytest.ini_options] pythonpath = ["src"]` permet l'import en test
  sans installation.
- Les imports d'application sont toujours absolus (`from package_name.module import x`).

## Alternatives considérées

- Flat layout : abandonné pour les raisons listées en Contexte.
- src/ avec namespace packages PEP 420 : surcomplique sans bénéfice pour
  des projets non-monorepo.

## Porte de sortie / révision

- Pour les forks de projets upstream à layout flat (ex. `Hunyuan3D-2.1-mlx`),
  exempter via `.suzerain.toml` avec justification, jusqu'à un éventuel
  refactor.
