# 08 — Docs & gouvernance interne

## Règles

### DG001 — `README.md` structuré

**Severity:** required · **Stacks:** *

Le `README.md` racine contient au minimum : une description en une
phrase, le statut, l'installation, un quickstart, un lien vers la doc
complète, la licence.

### DG002 — `CLAUDE.md` pour le contexte agent

**Severity:** recommended · **Stacks:** *

Si le projet est exploré par Claude Code, un `CLAUDE.md` à la racine
décrit la stack, les règles maison, les commandes principales (tests,
lint, build), et les conventions non triviales.

### DG003 — `docs/adr/` pour les décisions d'architecture

**Severity:** required · **Stacks:** * · **ADR:** [0000-record-architecture-decisions](../adr/0000-record-architecture-decisions.md)

Toute décision d'architecture non triviale est documentée comme ADR
dans `docs/adr/NNNN-<slug>.md`. Format : cf. ADR-0000 et le template
`templates/_common/adr.md`.

### DG004 — `LICENSE` à la racine

**Severity:** required · **Stacks:** *

Un fichier `LICENSE` à la racine déclare la licence. Le champ `license`
de `pyproject.toml` (ou équivalent) doit correspondre.

### DG005 — Specs et plans local-only

**Severity:** required · **Stacks:** *

Les fichiers sous `docs/superpowers/specs/` et `docs/superpowers/plans/`
ne sont jamais poussés sur les remotes publics. Un hook `pre-push`
bloque les push qui les contiennent vers `origin/main`. Politique née
d'une préférence utilisateur explicite : ces artefacts contiennent du
brainstorming et des plans internes qui ne doivent pas leak.
