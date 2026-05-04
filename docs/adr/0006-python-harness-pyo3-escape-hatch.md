# ADR-0006 : Python harness for the suzerain CLI, PyO3 escape hatch

- **Status** : accepted
- **Date** : 2026-04-30
- **Stacks** : * (impacts suzerain source code)

## Context

The suzerain CLI could be written in Rust to benefit from raw speed
(consistency with `uv`, `ruff`, `ty`). But the auditor's profile is
dominated by I/O and subprocess invocations to third-party tools
(themselves written in Rust). The real bottleneck is not the CPU: it is the
cost of evolving rules, which will be frequent in tier 2.

## Decision

The CLI is written in **Python**. Justifications:

- Rapid iteration on rules (each rule ≈ 10–20 lines of Python).
- Adapters (Python, Node, Go, Rust to come) live in Python sub-modules:
  adding a stack = creating a folder, not recompiling.
- Simple distribution: `uv tool install suzerain`.
- Python ecosystem mastery is a prerequisite for contribution.

**Explicit exit hatch**: if a portfolio-wide `suzerain report <root>` durably exceeds
30 s cold (measured over 3 consecutive runs), profile with
`py-spy` or `cProfile`. If an individual rule is responsible, rewrite it
as a Rust extension via PyO3 (local integration, not a global rewrite).

## Consequences

- The entire stack: Python ≥ 3.13, strict type hints (ADR-0003), pytest
  tests.
- No plugin ABI needed for adapters.
- Acknowledged debt: the CLI will be slower than a pure Rust equivalent. Acceptable
  given the usage profile (occasional audit, not a keystroke loop).

## Alternatives considered

- **100% Rust CLI**: marginal gain on total time (dominated by
  subprocess), massive cost on agility.
- **Mixed Python + Rust library from V1**: premature, adds complex
  build overhead without proven benefit.

## Exit hatch / revision

- Profile at each major release and tag rules > 200 ms as
  PyO3 candidates.
- If > 5 rules exceed this threshold, consider a
  `suzerain-rs` sub-project (Rust extension) before pushing the next tier.
