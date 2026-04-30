# 06 — Sanitizing & secrets

## Règles

### SA001 — `pre-commit` configuré et installé

**Severity:** required · **Stacks:** *

Un fichier `.pre-commit-config.yaml` à la racine définit au minimum :
`trailing-whitespace`, `end-of-file-fixer`, `check-yaml`, `check-toml`,
`detect-private-key`, et le linter du langage (ruff côté Python).

### SA002 — Détection de secrets (gitleaks)

**Severity:** required · **Stacks:** *

`gitleaks` est inclus dans les hooks pre-commit. Empêche le commit
accidentel de clés API, tokens, mots de passe.

### SA003 — `.env.example` sans secret

**Severity:** required · **Stacks:** *

Si le projet utilise des variables d'environnement, un fichier
`.env.example` à la racine documente les noms attendus avec des
valeurs vides ou bidons. Le vrai `.env` est dans `.gitignore`.

### SA004 — `.gitignore` baseline

**Severity:** required · **Stacks:** *

Le `.gitignore` à la racine ignore au minimum :
- Le venv (`.venv/`, `venv/`).
- Les caches (`__pycache__/`, `.pytest_cache/`, `.ruff_cache/`,
  `.ty_cache/`, `.mypy_cache/`).
- Les artefacts de build (`dist/`, `build/`, `*.egg-info/`).
- Les fichiers OS (`.DS_Store`, `Thumbs.db`).
