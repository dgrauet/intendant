# Suzerain

> Multi-stack project governance framework — handbook + auditor + scaffolder.

Suzerain materializes project management standards (workflows, CI, releases, quality, sanitizing, architecture) in a form that is both human-readable (handbook + ADRs) and executable (CLI).

## Status

✅ **Tiers 1, 2, 3 delivered** — Complete CLI: `init`, `explain`, `audit`, `doctor`, `new`. 16 rules (8 transverse + 8 Python adapter). The scaffolder produces a project that passes `audit --severity=required` at 100% (modulo `uv lock` post-scaffold, automatically exempted with a note).

## Installation

```bash
uv tool install --editable /path/to/suzerain
```

(Non-editable distribution: coming soon.)

## Quickstart

```bash
# Adopt suzerain on a repo
cd /path/to/your/repo
suzerain init

# Audit one or more repos
suzerain audit .                              # human report (default)
suzerain audit . --format=json                # for CI pipelines
suzerain audit . --format=md                  # for PR comments
suzerain audit . --severity=required          # exit 1 if a required rule fails

# Apply auto-applicable fixes (governance artifacts only)
suzerain audit . --fix --dry-run              # preview
suzerain audit . --fix                        # apply

# Understand a rule
suzerain explain LO001

# Check the install
suzerain doctor

# Scaffold a new compliant project
suzerain new my-project --stack=python --description="..." --author="..."
cd my-project
uv sync && uv run pre-commit install
suzerain audit . --severity=required   # exit 0 if all is well
```

## Domains covered (30 rules, 16 implemented)

| Prefix | Domain | V1 Rules |
|---|---|---|
| `LO` | Layout | LO001 src/ layout, LO002 tests/ at root |
| `PK` | Packaging & deps | PK001 pyproject, PK002 uv.lock, PK003 .python-version |
| `CI` | CI | CI001 workflow present |
| `QU` | Quality | QU001 ruff, QU002 ty (pyright fallback) |
| `TS` | Tests | TS001 pytest configured |
| `SA` | Sanitizing | SA001 pre-commit baseline |
| `RL` | Releases | RL001 CHANGELOG, RL002 conv. commits |
| `DG` | Docs & governance | DG001 README, DG003 ADRs, DG004 LICENSE, DG005 specs local-only |

The remaining rules documented in the handbook will be added in tier 2.5.

## Documentation

- [Charter](docs/handbook/00-charter.md) — mission, scope, compliance levels.
- [Handbook](docs/handbook/) — 8 domains × 30 rules.
- [ADRs](docs/adr/) — justified architecture decisions.

## Roadmap

- ✅ **Tier 1** — handbook + ADRs + `init` / `explain` commands.
- ✅ **Tier 2** — auditor (`audit`, `audit --fix`, `doctor`) with safe/proposed boundary.
- ✅ **Tier 3** — scaffolder (`suzerain new <name> --stack=python`).

## License

MIT — see [LICENSE](LICENSE).
