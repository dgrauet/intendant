# Suzerain

> Multi-stack project governance framework — handbook + auditor + scaffolder + portfolio dashboard.

Suzerain materializes project management standards (workflows, CI, releases, quality,
security, architecture) in a form that is both human-readable (handbook + ADRs) and
machine-executable (CLI). A single `.suzerain.toml` at a repo root tells the auditor
which stack applies and which rules are exempted; the scaffolder bootstraps a fully
compliant repo from scratch.

## Status

v0.2.1 — 44 rules across 3 stacks (python, claude-skill, node), self-audit 100/100,
510 tests. The `suzerain` CLI ships `init`, `audit`, `explain`, `new`, `dashboard`, and
`doctor`.

## Installation

```bash
# PyPI / uv tool (recommended)
uv tool install suzerain

# Editable from source
uv tool install --editable <path-to-clone>
```

## Quickstart

### Adopt suzerain on an existing repo

```bash
cd <your-repo>
suzerain init           # writes .suzerain.toml and docs skeleton
suzerain audit .        # human report
```

### Audit a single repo

```bash
suzerain audit .                          # full report, human-readable
suzerain audit . --severity=required      # exit 1 on required failures
suzerain audit . --format=json            # for CI or scripting
suzerain audit . --format=md              # for PR comments
suzerain audit . --fix --dry-run          # preview auto-fixes
suzerain audit . --fix                    # apply auto-fixes
```

### Bootstrap a new project

```bash
# Python package
suzerain new my-lib --stack=python --description="..." --author="..."

# Claude Code skill
suzerain new my-skill --stack=claude-skill --description="..."

# Node package
suzerain new my-pkg --stack=node --description="..."

# After scaffolding
cd my-lib
uv sync && uv run pre-commit install
suzerain audit . --severity=required      # should exit 0
```

### Cross-repo portfolio dashboard

```bash
suzerain dashboard <portfolio-root>               # human table
suzerain dashboard <portfolio-root> --format=json # machine-readable
suzerain dashboard <portfolio-root> --save-snapshot
suzerain dashboard <portfolio-root> --diff        # compare to last snapshot
suzerain dashboard <portfolio-root> --against snapshots/2026-04-01.json
```

### Inspect a rule

```bash
suzerain explain PYTHON_LO001       # handbook entry + linked ADR
suzerain explain --all              # table of all 44 rules
```

### Health check

```bash
suzerain doctor     # verify install integrity
```

## Coverage

44 rules total. Transverse rules apply to every stack; adapter rules apply only to
the declared stack.

### Transverse (19 rules)

| Family | Prefix | Count | Examples |
|---|---|---|---|
| Docs & governance | `DG` | 5 | README, CLAUDE.md, ADRs, LICENSE, specs local-only |
| Layout | `LO` | 1 | docs/ directory |
| Releases | `RL` | 4 | CHANGELOG, conventional commits, release-please, SemVer |
| CI | `CI` | 4 | workflow present, minimum steps, commit-msg check, caching |
| Sanitizing | `SA` | 4 | pre-commit baseline, gitleaks, .env.example, .gitignore |
| Tests | `TS` | 1 | regression_tests/ (when applicable) |

### Python adapter (12 rules — prefix `PYTHON_`)

Covers layout (`PYTHON_LO`), packaging (`PYTHON_PK`), quality (`PYTHON_QU`), and
tests (`PYTHON_TS`).

### Claude Skill adapter (7 rules — prefix `CLAUDE_SKILL_SK`)

Covers SKILL.md presence and frontmatter, evals/, referenced directories, and README
install path.

### Node adapter (6 rules — prefix `NODE_`)

Covers packaging (`NODE_PK`), quality (`NODE_QU`), and tests (`NODE_TS`).

> Rule IDs were renamed in v0.2.0 (e.g. `LO001` → `PYTHON_LO001`).
> See [docs/migrations/0.2.0-rule-prefix-rename.md](docs/migrations/0.2.0-rule-prefix-rename.md)
> to update `.suzerain.toml` exemptions.

## Documentation

- [Handbook](docs/handbook/) — charter + all 44 rules with rationale.
- [ADRs](docs/adr/) — justified architecture decisions.
- [Migrations](docs/migrations/) — upgrade guides between major versions.

## Roadmap

Future paliers: MCP server for agent-driven governance queries, HTML dashboard
export, multi-language adapters (Go, Rust).

## License

MIT — see [LICENSE](LICENSE).
