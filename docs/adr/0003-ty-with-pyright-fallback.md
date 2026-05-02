# ADR-0003 : `ty` (Astral) as the Python type-checker, pyright as fallback

- **Status** : accepted
- **Date** : 2026-04-30
- **Stacks** : python

## Context

Python static typing typically relies on `mypy` (mature, slow,
historical) or `pyright` (Microsoft, fast, IDE gold standard).
Astral is developing `ty`, a Rust type-checker in the same
philosophy as `ruff` and `uv`: performance and ecosystem consistency.

At the time of the decision (2026-04), `ty` is pre-1.0 but usable.
The bet is to adopt it now to benefit from the consistency
of the Astral suite and its speed, while keeping `pyright` as a
documented fallback.

## Decision

- **Default type-checker**: `ty` (invoked via `uvx ty check` or
  `uv tool install ty`).
- **Configuration**: `[tool.ty]` in `pyproject.toml`, or a separate `ty.toml`.
- **Documented fallback**: `pyright` in strict mode, configured in
  `pyrightconfig.json` or `[tool.pyright]`. Activate if `ty` introduces
  a major blocker (regression, massive false positives, abandonment).

## Consequences

- CI runs `uvx ty check` (see `templates/github/ci.yml`).
- `pyproject.toml` can declare `ty` in `[dependency-groups] dev`.
- Type annotations are strict (equivalent to `--strict` in mypy
  parlance): all parameters typed, return types typed, no implicit `Any`.

## Alternatives considered

- `mypy`: mature but slow. Losing momentum to pyright/ty.
- `pyright`: very good, but Astral ecosystem consistency wins at the time of
  the decision.

## Exit hatch / revision

Switch to `pyright` if **any one** of the following criteria becomes true:

1. `ty` introduces a blocking regression unresolved within 2 weeks.
2. `ty` is officially abandoned by Astral.
3. False positives > 10% on suzerain's codebase for 3 consecutive versions.

Switch procedure: replace the dep + the CI invocation + the config
section, update this ADR (status `superseded by ADR-NNNN`),
open a new ADR `pyright-after-ty-rollback`.
