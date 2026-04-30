# 00 — Charte

## Mission

Suzerain est un framework de gouvernance multi-stack. Il matérialise des
standards de gestion de projet sous une forme à la fois lisible
(handbook + ADRs) et exécutable (CLI d'audit et de scaffolding).

## Périmètre

8 domaines :

1. [Layout](01-layout.md)
2. [Packaging & dépendances](02-packaging.md)
3. [CI](03-ci.md)
4. [Qualité](04-quality.md)
5. [Tests](05-tests.md)
6. [Sanitizing & secrets](06-sanitizing.md)
7. [Releases](07-releases.md)
8. [Docs & gouvernance interne](08-docs-and-agent.md)

## Non-goals

- Pas de remplacement de Make/Just/Taskfile (orchestration).
- Pas d'enforcement d'une architecture applicative (DDD, hexagonal...).
- Pas de revue de code applicatif.

## Niveaux de conformité

Chaque règle a une `severity` :

- `required` : bloque la PR si activée en mode `strict`.
- `recommended` : warning, n'arrête pas le pipeline.
- `optional` : informationnel.

Le mode appliqué est déclaré par repo dans `.suzerain.toml`
(`mode = "strict" | "recommended" | "advisory"`).

## Exemptions

Une règle peut être exemptée par repo via `.suzerain.toml`, avec une
**raison écrite** et optionnellement une **date d'expiration**. L'exemption
n'efface pas le finding : il apparaît `EXEMPT(reason)` dans le rapport.
La dette technique reste visible.
