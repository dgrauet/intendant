# 07 — Releases

## Rules

### RL001 — `CHANGELOG.md` in Keep-a-Changelog format

**Severity:** required · **Stacks:** * · **ADR:** [0005-release-please](../adr/0005-release-please.md)

A `CHANGELOG.md` at the root, in
[Keep-a-Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/) format.
Entries are added by `release-please` from conventional commits.

### RL002 — Conventional Commits strict

**Severity:** required · **Stacks:** * · **ADR:** [0004-conventional-commits-strict](../adr/0004-conventional-commits-strict.md)

All commits follow
[Conventional Commits 1.0.0](https://www.conventionalcommits.org/).
Validated locally by `commitizen` (the `commit-msg` hook) and in CI by
`cz check`.

### RL003 — `release-please` configured

**Severity:** required · **Stacks:** * · **ADR:** [0005-release-please](../adr/0005-release-please.md)

The files `release-please-config.json` and
`.release-please-manifest.json` at the root, plus the workflow
`.github/workflows/release-please.yml`, automate versioning,
CHANGELOG, and git tagging.

### RL004 — Strict semantic versioning

**Severity:** required · **Stacks:** *

[SemVer 2.0.0](https://semver.org). `release-please` interprets
conventional commits: `fix:` → patch, `feat:` → minor, `feat!:` or
`BREAKING CHANGE:` → major.

The version is read from the first file found: `pyproject.toml`,
`package.json`, `Cargo.toml`, or `.release-please-manifest.json`
(`{".": "0.1.0"}` format). The manifest fallback enables RL004 to
apply to stacks without a primary language manifest (e.g. `claude-skill`).
If none of these files is present, the rule is skipped.

### RL005 — main branch protected on GitHub

**Severity:** recommended · **Stacks:** *

When the repo has a GitHub remote, the `main` branch must be
protected so direct pushes are blocked and changes go through
PR + CI. Concretely the rule verifies, via the local `gh` CLI:

- `required_pull_request_reviews` is set (PR required)
- `allow_force_pushes.enabled = false`
- `allow_deletions.enabled = false`
- `enforce_admins.enabled = true` (admins included in the rules)

The rule **skips silently** when:
- the repo is not a git repo
- there is no `origin` remote
- the remote is not on github.com
- `gh` is not installed
- `gh` returns 401/403 (not authenticated, no access)

The rule does NOT enforce protection itself — branch protection is
configured server-side via the GitHub API or repo settings UI. RL005
just audits that it is in place.

### RL006 — release-please câblé via une GitHub App

**Severity:** recommended · **Stacks:** * · **ADR:** [0005-release-please](../adr/0005-release-please.md)

Quand le repo utilise `release-please`, le workflow doit minter et utiliser
un token de **GitHub App** (`actions/create-github-app-token`) plutôt que le
`GITHUB_TOKEN` par défaut. Une PR de release créée avec le token par défaut ne
déclenche pas les autres workflows (prévention de boucle GitHub), laissant les
checks requis non exécutés et la PR non-mergeable.

La règle vérifie, dans le seul workflow utilisant `googleapis/release-please-action` :

- une étape `actions/create-github-app-token` est présente ;
- le `token:` de l'action référence la sortie de cette étape (`...outputs.token`) ;
- aucun token par défaut (`secrets.GITHUB_TOKEN` / `github.token`) n'est utilisé ;
- les inputs `config-file:` et `manifest-file:` sont renseignés.

Cette vérification est **statique** (lecture du YAML, pas de réseau).

La règle **skip silencieusement** quand il n'y a pas de `.github/workflows/`
(couvert par CI001) ou qu'aucun workflow n'utilise release-please (la présence
des fichiers JSON est couverte par RL003).
