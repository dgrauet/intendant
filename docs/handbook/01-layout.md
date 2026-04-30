# 01 — Layout

Convention de structure de dossiers pour les projets régis par suzerain.

## Règles

### LO001 — `src/` layout obligatoire (Python)

**Severity:** required · **Stacks:** python · **ADR:** [0001-layout-src-vs-flat](../adr/0001-layout-src-vs-flat.md)

Le code source vit dans `src/<package_name>/`, jamais à la racine. Les
tests vivent dans `tests/` à la racine. Cf. ADR-0001 pour la rationale.

### LO002 — Tests dans `tests/` à la racine

**Severity:** required · **Stacks:** python · **ADR:** [0001-layout-src-vs-flat](../adr/0001-layout-src-vs-flat.md)

Les tests vivent dans un dossier `tests/` à la racine du repo. Pas de
co-location avec le code source. Permet une séparation claire et
empêche que les tests soient packagés involontairement.

### LO003 — Documentation dans `docs/`

**Severity:** recommended · **Stacks:** *

Toute la documentation longue (handbook, ADRs, specs, tutorials) vit dans
`docs/`. Le `README.md` racine reste un point d'entrée court qui pointe
vers `docs/`.
