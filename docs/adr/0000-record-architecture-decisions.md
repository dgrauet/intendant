# ADR-0000 : Record architecture decisions

- **Status** : accepted
- **Date** : 2026-04-30
- **Stacks** : * (transverse)

## Context

Suzerain produces executable rules and human documentation. Every
rule is traceable to an explicit architecture decision. Without ADRs,
the rationale behind the rules is lost, changes become arbitrary, and
governance loses its legitimacy.

## Decision

We adopt the ADR format (Architecture Decision Records, popularized by
Michael Nygard) with a slight extension:

- Sequential `NNNN` numbering with 4 digits, never reused.
- Status: `proposed | accepted | superseded by ADR-MMMM | deprecated`.
- A non-standard section **Exit hatch / revision** documents what would
  make us reconsider the decision.

The canonical template lives in `templates/_common/adr.md`.

## Consequences

- Every new suzerain rule points to an ADR via `RuleSection.adr_ref`.
- The e2e test `tests/unit/test_handbook.py` can verify that each referenced ADR
  exists (to be added in tier 2).
- ADRs are not modified retroactively: they are superseded or deprecated.

## Alternatives considered

- No ADRs: too informal, governance is not auditable.
- ADRs without sequential numbering: breaks chronological order and
  stable citations from rules.

## Exit hatch / revision

- If an alternative format (Y-statements, etc.) emerges as an industry
  standard, migrate all ADRs in bulk.
