# CLAUDE.md — suzerain

Agent context for the suzerain repo.

## What

Multi-stack governance framework. This repo defines, hosts, and enforces the standards
that govern the projects it is configured to scan.

## House rules

- **Specs and plans local-only**: `docs/superpowers/specs/` and `docs/superpowers/plans/` are NEVER pushed to the public remote. Rebase the branch onto `origin/main` before pushing.
- **Strict TDD** on the CLI Python code (`src/suzerain/`). Every new engine component comes with its failing test first.
- **Strict conventional commits**. The `commit-msg` hook rejects non-conformant commits.
- **Suzerain eats its own dog food**: suzerain is governed by its own `.suzerain.toml` (`mode = "strict"`).
- **Type-checker**: `ty` (Astral) in V1. `pyright` documented as fallback (ADR-0003).

## Stack

- Python 3.13, uv (deps + lockfile mandatory)
- ruff (lint+format), ty (type-check), pytest (tests)
- pre-commit, commitizen, release-please

## Tests

```bash
uv run pytest                  # all tests
uv run pytest tests/unit -v    # unit only
uv run pytest --cov            # with coverage
```

## Lint & type

```bash
uv run ruff check .
uv run ruff format --check .
uvx ty check                   # or: uv run ty check (depending on installation)
```

## Design reference

Specs and plans are local-only artifacts archived outside the repo. They
are intentionally not tracked here (per DG005).
