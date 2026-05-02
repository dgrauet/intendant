# ADR-0001 : Layout `src/` over flat layout

- **Status** : accepted
- **Date** : 2026-04-30
- **Stacks** : python

## Context

Python projects can organize their code either with a flat layout
(`mypackage/__init__.py` at the root) or a src layout
(`src/mypackage/__init__.py`). The flat layout is historically widespread
but causes subtle errors: pytest can import the source code
rather than the installed package, masking packaging bugs.

## Decision

All new or refactored Python projects use the **src layout**.
Test files live at the root in `tests/`.

```
project/
├── src/
│   └── package_name/
│       └── __init__.py
└── tests/
    └── test_*.py
```

## Consequences

- `pyproject.toml` must declare `[tool.hatch.build.targets.wheel] packages = ["src/package_name"]`
  (or equivalent depending on the build backend).
- `[tool.pytest.ini_options] pythonpath = ["src"]` enables importing during tests
  without installation.
- Application imports are always absolute (`from package_name.module import x`).

## Alternatives considered

- Flat layout: abandoned for the reasons listed in the Context.
- src/ with PEP 420 namespace packages: over-complicates without benefit for
  non-monorepo projects.

## Exit hatch / revision

- For forks of upstream projects with a flat layout (e.g. `Hunyuan3D-2.1-mlx`),
  exempt via `.suzerain.toml` with justification, until a potential
  refactor.
