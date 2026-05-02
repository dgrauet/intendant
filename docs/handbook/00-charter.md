# 00 — Charter

## Mission

Suzerain is a multi-stack governance framework. It materializes project
management standards in a form that is both human-readable
(handbook + ADRs) and executable (audit and scaffolding CLI).

## Scope

8 domains:

1. [Layout](01-layout.md)
2. [Packaging & dependencies](02-packaging.md)
3. [CI](03-ci.md)
4. [Quality](04-quality.md)
5. [Tests](05-tests.md)
6. [Sanitizing & secrets](06-sanitizing.md)
7. [Releases](07-releases.md)
8. [Docs & internal governance](08-docs-and-agent.md)

## Non-goals

- No replacement for Make/Just/Taskfile (orchestration).
- No enforcement of an application architecture (DDD, hexagonal...).
- No application code review.

## Compliance levels

Each rule has a `severity`:

- `required`: blocks the PR if enabled in `strict` mode.
- `recommended`: warning, does not stop the pipeline.
- `optional`: informational.

The applied mode is declared per repo in `.suzerain.toml`
(`mode = "strict" | "recommended" | "advisory"`).

## Exemptions

A rule can be exempted per repo via `.suzerain.toml`, with a
**written reason** and optionally an **expiration date**. The exemption
does not erase the finding: it appears as `EXEMPT(reason)` in the report.
Technical debt remains visible.
