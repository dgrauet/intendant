# Intendant

> Multi-stack project governance framework — handbook + auditor + scaffolder + portfolio report.

Intendant materializes project management standards (workflows, CI, releases, quality,
security, architecture) in a form that is both human-readable (handbook + ADRs) and
machine-executable (CLI). A single `.intendant.toml` at a repo root tells the auditor
which stack applies and which rules are exempted; the scaffolder bootstraps a fully
compliant repo from scratch.

## Status

v1.0.0 — stable. 70 rules across 6 stacks (python, claude-skill, node, rust, go, swift),
self-audit 100/100, 730 tests. Multi-language sub-projects supported via
`[[subprojects]]` in `.intendant.toml` (see [Multi-stack repositories](#multi-stack-repositories)).
The `intendant` CLI ships `init`, `audit`, `explain`, `new`, `report`, `doctor`, and
`mcp` (optional MCP server for agents).

## Installation

```bash
# PyPI / uv tool (recommended)
uv tool install intendant

# Editable from source
uv tool install --editable <path-to-clone>
```

## Quickstart

### Adopt intendant on an existing repo

```bash
cd <your-repo>
intendant init           # writes .intendant.toml and docs skeleton
intendant audit .        # human report
```

### Audit a single repo

```bash
intendant audit .                          # full report, human-readable
intendant audit . --severity=required      # exit 1 on required failures
intendant audit . --format=json            # for CI or scripting
intendant audit . --format=md              # for PR comments
intendant audit . --fix --dry-run          # preview auto-fixes
intendant audit . --fix                    # apply auto-fixes
```

### Bootstrap a new project

```bash
# Python package
intendant new my-lib --stack=python --description="..." --author="..."

# Claude Code skill
intendant new my-skill --stack=claude-skill --description="..."

# Node package
intendant new my-pkg --stack=node --description="..."

# Rust crate
intendant new my-crate --stack=rust --description="..."

# Go module
intendant new my-svc --stack=go --description="..."

# Swift (SwiftPM library, package + Sources + Tests + swiftlint + CI)
intendant new my-pkg --stack=swift --description="..."

# After scaffolding
cd my-lib
uv sync && uv run pre-commit install
intendant audit . --severity=required      # should exit 0
```

### Multi-stack repositories

A repo can host several sub-projects in different languages. Declare each one via
`[[subprojects]]` in `.intendant.toml`:

```toml
[intendant]
version = "1"
enforcement = "strict"

[[subprojects]]
name = "backend"
path = "services/api"
stack = "python"

[[subprojects]]
name = "frontend"
path = "apps/web"
stack = "node"

[[subprojects]]
name = "agent-skill"
path = "skills/triage"
stack = "claude-skill"
```

Each sub-project is audited independently — only transverse rules and its own
stack's rules apply. Exemptions can be scoped to a single sub-project with
`[exemptions.<name>]`:

```toml
[exemptions.backend]
PYTHON_QU002 = "Ruff config inherited from monorepo root, not duplicated here"
```

For single-stack repos, prefer auto-detection (omit `stack`) or pin once with
`[intendant] stack = "<name>"`. See the [Multi-stack handbook
page](docs/handbook/14-multi-stack.md) for the resolution model, field
constraints, and scoped-exemption semantics.

### Cross-repo portfolio report

```bash
intendant report <portfolio-root>               # human table
intendant report <portfolio-root> --format=json # machine-readable
intendant report <portfolio-root> --save-snapshot
intendant report <portfolio-root> --diff        # compare to last snapshot
intendant report <portfolio-root> --against snapshots/2026-04-01.json
```

### Inspect a rule

```bash
intendant explain PYTHON_LO001       # handbook entry + linked ADR
intendant explain --all              # table of all 70 rules
```

### Health check

```bash
intendant doctor     # verify install integrity
```

## Coverage

70 rules total. Transverse rules apply to every stack; adapter rules apply only to
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

### Swift adapter (7 rules — prefix `SWIFT_`)

Covers packaging (`SWIFT_PK`: Package.swift/.resolved, swift-tools-version),
quality (`SWIFT_QU`: swiftlint/swiftformat config), tests (`SWIFT_TS`:
`Tests/**/*.swift` with `func test*`/`XCTestCase`/`@Test`), CI (`SWIFT_CI`:
swift build/test + lint), and sanitizing (`SWIFT_SA`: `.build/` and
`xcuserdata/` in `.gitignore`).

> Rule IDs were renamed in v0.2.0 (e.g. `LO001` → `PYTHON_LO001`).
> See [docs/migrations/0.2.0-rule-prefix-rename.md](docs/migrations/0.2.0-rule-prefix-rename.md)
> to update `.intendant.toml` exemptions.

## MCP server

Intendant ships an optional MCP server so any MCP-compatible agent (Claude Code,
Claude Desktop, Cursor, …) can query governance state directly.

Install with the extra:

```bash
uv tool install 'intendant[mcp]'
```

Then register the server in your MCP client. Example for Claude Desktop
(`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "intendant": {
      "command": "intendant",
      "args": ["mcp"]
    }
  }
}
```

Five tools are exposed: `audit_repo`, `explain_rule`, `list_rules`,
`report_portfolio`, `diff_portfolio`. All return JSON-serializable payloads
matching the schemas of the corresponding CLI commands.

## Documentation

- [Handbook](docs/handbook/) — charter + all 70 rules with rationale.
- [Multi-stack repositories](docs/handbook/14-multi-stack.md) — `[[subprojects]]` syntax and scoped exemptions.
- [ADRs](docs/adr/) — justified architecture decisions.
- [Migrations](docs/migrations/) — upgrade guides between major versions.

## Roadmap

Future paliers: portfolio polish, additional adapters as needed.

## License

MIT — see [LICENSE](LICENSE).
