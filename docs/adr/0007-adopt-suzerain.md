# ADR-0007 : Adopt suzerain

- **Status** : accepted
- **Date** : 2026-04-30
- **Stacks** : * (transverse)

## Context

This repo adopts [suzerain](https://github.com/dgrauet/suzerain) as its
governance framework — handbook, audit (tier 2), scaffolder (tier 3). The
`.suzerain.toml` file at the repo root declares the stack, the applied
compliance mode, and justified exemptions.

## Decision

- Stack detected at adoption: `python`
- Initial mode: `advisory` (findings are reported but nothing is blocked).
- All future ADRs in this repo numbered starting from 0001.

## Consequences

- The auditor (suzerain tier 2) can run on this repo and report
  deviations from the baseline.
- Exemptions must be listed in `.suzerain.toml` with a reason.

## Alternatives considered

- Adopt nothing (keep implicit conventions). Rejected: conventional debt
  accumulates silently.
- Adopt another framework: no equivalent multi-stack framework identified at
  the time of adoption.

## Exit hatch / revision

- If suzerain no longer tracks tool evolution, switch to `mode = advisory`
  permanently and manage the standards manually.
- If a `v2` baseline breaks too many rules: freeze at `version = "1"` and plan
  a targeted migration.
