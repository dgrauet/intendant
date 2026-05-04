# Suzerain

> Multi-stack project governance framework — handbook + auditor + scaffolder + portfolio report.

Suzerain materializes project management standards (workflows, CI, releases, quality,
security, architecture) in a form that is both human-readable (handbook + ADRs) and
machine-executable (CLI). A single `.suzerain.toml` at a repo root tells the auditor
which stack applies and which rules are exempted; the scaffolder bootstraps a fully
compliant repo from scratch.

## Status

v1.0.0 — stable. 62 rules across 5 stacks (python, claude-skill, node, rust, go),
self-audit 100/100, 730 tests. Multi-language sub-projects supported via
`[[subprojects]]` in `.suzerain.toml`. The `suzerain` CLI ships `init`, `audit`,
`explain`, `new`, `report`, `doctor`, and `mcp` (optional MCP server for agents).

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

# Rust crate
suzerain new my-crate --stack=rust --description="..."

# Go module
suzerain new my-svc --stack=go --description="..."

# After scaffolding
cd my-lib
uv sync && uv run pre-commit install
suzerain audit . --severity=required      # should exit 0
```

### Cross-repo portfolio report

```bash
suzerain report <portfolio-root>               # human table
suzerain report <portfolio-root> --format=json # machine-readable
suzerain report <portfolio-root> --save-snapshot
suzerain report <portfolio-root> --diff        # compare to last snapshot
suzerain report <portfolio-root> --against snapshots/2026-04-01.json
```

### Inspect a rule

```bash
suzerain explain PYTHON_LO001       # handbook entry + linked ADR
suzerain explain --all              # table of all 62 rules
```

### Health check

```bash
suzerain doctor     # verify install integrity
```

## Coverage

62 rules total. Transverse rules apply to every stack; adapter rules apply only to
the declared stack.

### Transverse (18 rules)

| Family | Prefix | Count | Examples |
|---|---|---|---|
| Docs & governance | `DG` | 5 | README, CLAUDE.md, ADRs, LICENSE, specs local-only |
| Layout | `LO` | 1 | docs/ directory |
| Releases | `RL` | 4 | CHANGELOG, conventional commits, release-please, SemVer |
| CI | `CI` | 4 | workflow present, minimum steps, commit-msg check, caching |
| Sanitizing | `SA` | 4 | pre-commit baseline, gitleaks, .env.example, .gitignore |
| Tests | `TS` | 1 | regression_tests/ (when applicable) |

### Python adapter (14 rules — prefix `PYTHON_`)

Covers layout (`PYTHON_LO`), packaging (`PYTHON_PK`), quality (`PYTHON_QU`), and
tests (`PYTHON_TS`).

### Claude Skill adapter (8 rules — prefix `CLAUDE_SKILL_`)

Covers SKILL.md presence and frontmatter, evals/, referenced directories, and README
install path.

### Node adapter (8 rules — prefix `NODE_`)

Covers packaging (`NODE_PK`), quality (`NODE_QU`), tests (`NODE_TS`), CI
(`NODE_CI`), and sanitizing (`NODE_SA`).

### Rust adapter (7 rules — prefix `RUST_`)

Covers packaging (`RUST_PK`: Cargo.toml/lock, edition), quality (`RUST_QU`:
toolchain pin), tests (`RUST_TS`: `#[test]` annotations), CI (`RUST_CI`: cargo
fmt/clippy/test), and sanitizing (`RUST_SA`: `target/` in `.gitignore`).

### Go adapter (7 rules — prefix `GO_`)

Covers packaging (`GO_PK`: go.mod/go.sum, go directive), quality (`GO_QU`:
golangci-lint config), tests (`GO_TS`: `*_test.go` with `func Test*`), CI
(`GO_CI`: vet/build + test + lint), and sanitizing (`GO_SA`: `*.test` in
`.gitignore`).

> Rule IDs were renamed in v0.2.0 (e.g. `LO001` → `PYTHON_LO001`).
> See [docs/migrations/0.2.0-rule-prefix-rename.md](docs/migrations/0.2.0-rule-prefix-rename.md)
> to update `.suzerain.toml` exemptions.

## MCP server

Suzerain ships an optional MCP server so any MCP-compatible agent (Claude Code,
Claude Desktop, Cursor, …) can query governance state directly.

Install with the extra:

```bash
uv tool install 'suzerain[mcp]'
```

Then register the server in your MCP client. Example for Claude Desktop
(`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "suzerain": {
      "command": "suzerain",
      "args": ["mcp"]
    }
  }
}
```

Five tools are exposed: `audit_repo`, `explain_rule`, `list_rules`,
`report_portfolio`, `diff_portfolio`. All return JSON-serializable payloads
matching the schemas of the corresponding CLI commands.

## Documentation

- [Handbook](docs/handbook/) — charter + all 62 rules with rationale.
- [ADRs](docs/adr/) — justified architecture decisions.
- [Migrations](docs/migrations/) — upgrade guides between major versions.

## Roadmap

Future paliers: portfolio polish, additional adapters as needed.

## License

MIT — see [LICENSE](LICENSE).
