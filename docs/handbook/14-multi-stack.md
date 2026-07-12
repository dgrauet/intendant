# 14 — Multi-stack repositories

Reference for the multi-language declaration in `.intendant.toml`. This
page introduces no rule: it documents how a repo's stack composition is
resolved, and how to declare several sub-projects living in the same
repository.

## Resolution model

At audit time, intendant builds a per-repo stack composition through
three modes, in order:

1. **Manual top-level pin** — `[intendant] stack = "<name>"` pins a
   single stack for the whole repo. `mode = "manual"`.
2. **Manual subprojects** — one or more `[[subprojects]]` entries
   explicitly declare each sub-project with its path and stack.
   `mode = "manual"`.
3. **Auto-detection** — when neither `stack` nor `[[subprojects]]` is
   present (or with `stack = "auto"`, the legacy sentinel), intendant
   scans the root and detects each stack through its markers
   (`pyproject.toml`, `package.json`, `Cargo.toml`, `go.mod`,
   `Package.swift`, `*.csproj`/`*.sln`, plus a walk for `SKILL.md`).
   `mode = "auto"`.

Top-level `stack` and `[[subprojects]]` are mutually exclusive in
intent: when both are declared, `[[subprojects]]` wins for per-path rule
routing and `stack` falls back to an informative role. Prefer one or the
other.

## Single-stack repo

The most common case: a single language, at the root. Two options.

**Auto-detection (recommended)** — let intendant detect:

```toml
[intendant]
version = "1"
enforcement = "strict"
```

**Manual pin** — useful to freeze the stack when auto-detection is
ambiguous (e.g. a `pyproject.toml` present only for tooling config):

```toml
[intendant]
version = "1"
stack = "python"
enforcement = "strict"
```

## Multi-stack repo

When a repo hosts several sub-projects in different languages (e.g. a
Python backend + a Node frontend + a Claude skill), declare each
sub-project through `[[subprojects]]`:

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
role = "frontend"   # presentation-only: test-presence rules auto-skip

[[subprojects]]
name = "agent-skill"
path = "skills/triage"
stack = "claude-skill"
```

Each sub-project is audited independently: only the transverse rules
(`DG`, `LO003`, `RL`, `CI`, `SA`, `TS`) and its own stack's rules apply
to it.

### Subproject fields

| Field   | Required | Description                                                        |
| ------- | -------- | ------------------------------------------------------------------ |
| `path`  | yes      | Path relative to the repo root. `"."` designates the root.         |
| `stack` | yes      | One of the supported stacks: `python`, `node`, `claude-skill`, `rust`, `go`, `swift`, `dotnet`. |
| `name`  | optional | Sub-project identifier. Default: `basename(path)`, or `"root"` when `path = "."`. |
| `role`  | optional | `"frontend"`: presentation-only sub-project (logic tested elsewhere) — test-presence rules (`*_TS*`) automatically *skip*, no exemption to write. |

### Constraints

The parser rejects any config violating these invariants:

- `path` must be relative (no absolute path) and must not contain `..`.
- `name` must match `[a-zA-Z0-9_-]+`.
- `name` values must be unique within the repo.
- `path` values must be unique within the repo.
- `path` and `stack` are mandatory; their absence fails
  `intendant audit` with an explicit error.

### Root as one subproject among others

`path = "."` is valid and lets the root participate as a regular
sub-project next to others:

```toml
[[subprojects]]
path = "."
stack = "python"

[[subprojects]]
path = "skills/triage"
stack = "claude-skill"
```

The root sub-project takes `name = "root"` by default.

## Scoped exemptions

Exemptions can be declared globally or scoped to a specific sub-project
through `[exemptions.<subproject_name>]`. Resolution order: **scoped
first, then global**.

```toml
# Global exemption: applies to every sub-project
[exemptions]
DG004 = { reason = "License pending legal review", until = "2026-06-30" }

# Scoped exemption: only applies to the `backend` sub-project
[exemptions.backend]
PYTHON_QU002 = "Ruff config inherited from monorepo root, not duplicated here"

# Scoped exemption: only applies to `frontend`
[exemptions.frontend]
NODE_TS001 = { reason = "Tests live in a sibling repo for now", until = "2026-09-01" }
```

Each exemption can be:

- a **string** — equivalent to `{ reason = "<string>" }`, with no
  expiry date;
- a **table** with `reason` (mandatory) and `until` (optional, ISO
  format `YYYY-MM-DD`).

An exemption does not erase the finding: it shows up as
`EXEMPT(reason)` in the report. The technical debt stays visible.

## Reports and CI

- The `intendant audit` report renders each sub-project under its own
  section; the JSON format returns a `subprojects[]` field with one
  block per sub-project.
- `enforcement` (`strict`/`recommended`/`advisory`) stays defined once
  at the top level and applies uniformly to every sub-project.
- The portfolio report (`intendant report`) lists the stacks detected
  per repo; a multi-stack repo shows up with its real composition, with
  no `"multi"` sentinel.

## See also

- [00 — Charter](00-charter.md) — exemption model and compliance
  levels.
- ADR-0006 — *Python harness, PyO3 escape hatch*: why the architecture
  makes adding a stack equivalent to creating an adapter folder.
