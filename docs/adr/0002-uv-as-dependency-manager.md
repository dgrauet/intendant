# ADR-0002 : `uv` as the Python dependency manager

- **Status** : accepted
- **Date** : 2026-04-30
- **Stacks** : python

## Context

The Python ecosystem has long suffered from fragmentation in packaging tools
(`pip`, `pipenv`, `poetry`, `pdm`, `hatch`, `rye`...). Each has its
strengths, but maintaining cross-project consistency requires a single choice.
`uv` (Astral, Rust) consolidates venv creation + resolution + locking
+ installation into a single binary, considerably faster than alternatives,
with a standard `pyproject.toml` format.

## Decision

`uv` is the canonical tool for:

- Creating and synchronizing the venv (`uv sync`).
- Locking dependencies (`uv.lock`, **committed to the repo**, required).
- Running local commands (`uv run <cmd>`).
- Installing suzerain and CLI tools (`uv tool install`).

`pip` is no longer used locally for projects governed by suzerain.
`requirements.txt` can be generated (`uv export`) for interop with
legacy systems.

## Consequences

- All projects have a versioned `uv.lock`.
- CI installs `uv` then runs `uv sync` (template workflow for tier 1
  delivered in `templates/github/ci.yml`).
- `pyproject.toml` uses `[dependency-groups]` (PEP 735) rather than
  `[project.optional-dependencies]` for dev deps.

## Alternatives considered

- `poetry`: mature but slow; `pyproject.toml` format less standard
  (`tool.poetry` instead of `project`).
- `pdm`: good but less community momentum.
- `pip + pip-tools`: no integrated venv, two tools to coordinate.

## Exit hatch / revision

- If `uv` stops being maintained or Astral pivots, switch to `pdm`
  (closest in philosophy) with a migration script `uv export`
  + `pdm import`.
