# Suzerain

> Multi-stack project governance framework — handbook + auditor + scaffolder.

Suzerain matérialise des standards de gestion de projet (workflows, CI, releases, qualité, sanitizing, architecture) sous une forme à la fois lisible (handbook + ADRs) et exécutable (CLI).

## Statut

🚧 Palier 1 en cours — handbook + bootstrap. Voir [`docs/superpowers/plans/2026-04-30-suzerain-palier1.md`](docs/superpowers/plans/2026-04-30-suzerain-palier1.md).

## Installation (palier 1, mode dev)

```bash
uv tool install --editable /path/to/suzerain
```

## Usage palier 1

```bash
suzerain init                  # crée .suzerain.toml + ADR d'adoption dans le repo courant
suzerain explain PY001         # affiche la règle PY001 (handbook + ADR liée)
```

## Documentation

- [Handbook](docs/handbook/00-charter.md) — la charte et les 8 domaines couverts.
- [ADRs](docs/adr/) — décisions d'architecture justifiées.

## Roadmap

- ✅ Palier 1 : handbook + ADRs + `init` / `explain`.
- ⏳ Palier 2 : `audit` (read-only puis `--fix` avec garde-fous).
- ⏳ Palier 3 : `new` (scaffolder).

## Licence

MIT — voir [LICENSE](LICENSE).
