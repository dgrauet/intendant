# 07 — Releases

## Règles

### RL001 — `CHANGELOG.md` au format Keep-a-Changelog

**Severity:** required · **Stacks:** * · **ADR:** [0005-release-please](../adr/0005-release-please.md)

Un `CHANGELOG.md` à la racine, format
[Keep-a-Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/).
Les entrées sont ajoutées par `release-please` à partir des conventional
commits.

### RL002 — Conventional Commits strict

**Severity:** required · **Stacks:** * · **ADR:** [0004-conventional-commits-strict](../adr/0004-conventional-commits-strict.md)

Tous les commits suivent
[Conventional Commits 1.0.0](https://www.conventionalcommits.org/).
Validé en local par `commitizen` (hook `commit-msg`) et en CI par
`cz check`.

### RL003 — `release-please` configuré

**Severity:** required · **Stacks:** * · **ADR:** [0005-release-please](../adr/0005-release-please.md)

Les fichiers `release-please-config.json` et
`.release-please-manifest.json` à la racine, plus le workflow
`.github/workflows/release-please.yml`, automatisent versionnement,
CHANGELOG et tag git.

### RL004 — Versionnement sémantique strict

**Severity:** required · **Stacks:** *

[SemVer 2.0.0](https://semver.org). `release-please` interprète les
conventional commits : `fix:` → patch, `feat:` → minor, `feat!:` ou
`BREAKING CHANGE:` → major.
