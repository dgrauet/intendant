# Suzerain

> Multi-stack project governance framework — handbook + auditor + scaffolder.

Suzerain matérialise des standards de gestion de projet (workflows, CI, releases, qualité, sanitizing, architecture) sous une forme à la fois lisible (handbook + ADRs) et exécutable (CLI).

## Statut

✅ **v0.1.1** — paliers 1 et 2 livrés. CLI opérationnel : `init`, `explain`, `audit`, `doctor`. 16 règles (8 transverses + 8 Python adapter), score de conformité pondéré, frontière safe/proposed sur les fixes auto-applicables.

## Installation

```bash
uv tool install --editable /path/to/suzerain
```

(Distribution non-editable : à venir.)

## Quickstart

```bash
# Adopter suzerain sur un repo
cd /path/to/your/repo
suzerain init

# Auditer un ou plusieurs repos
suzerain audit .                              # rapport human (défaut)
suzerain audit . --format=json                # pour pipelines CI
suzerain audit . --format=md                  # pour commentaire de PR
suzerain audit . --severity=required          # exit 1 si une règle required échoue

# Appliquer les fixes auto-applicables (artefacts gouvernance uniquement)
suzerain audit . --fix --dry-run              # preview
suzerain audit . --fix                        # apply

# Comprendre une règle
suzerain explain LO001

# Vérifier l'install
suzerain doctor
```

## Domaines couverts (30 règles, 16 implémentées)

| Préfixe | Domaine | Règles V1 |
|---|---|---|
| `LO` | Layout | LO001 src/ layout, LO002 tests/ at root |
| `PK` | Packaging & deps | PK001 pyproject, PK002 uv.lock, PK003 .python-version |
| `CI` | CI | CI001 workflow présent |
| `QU` | Qualité | QU001 ruff, QU002 ty (pyright fallback) |
| `TS` | Tests | TS001 pytest configured |
| `SA` | Sanitizing | SA001 pre-commit baseline |
| `RL` | Releases | RL001 CHANGELOG, RL002 conv. commits |
| `DG` | Docs & gouvernance | DG001 README, DG003 ADRs, DG004 LICENSE, DG005 specs local-only |

Les autres règles documentées dans le handbook s'ajouteront en palier 2.5.

## Documentation

- [Charte](docs/handbook/00-charter.md) — mission, périmètre, niveaux de conformité.
- [Handbook](docs/handbook/) — 8 domaines × 30 règles.
- [ADRs](docs/adr/) — décisions d'architecture justifiées.

## Roadmap

- ✅ **Palier 1** — handbook + ADRs + commandes `init` / `explain`.
- ✅ **Palier 2** — auditeur (`audit`, `audit --fix`, `doctor`) avec frontière safe/proposed.
- ⏳ **Palier 3** — scaffolder (`suzerain new <name> --stack=...`).

## Licence

MIT — voir [LICENSE](LICENSE).
