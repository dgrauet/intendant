# 02 — Packaging & dépendances

## Règles

### PK001 — `pyproject.toml` à la racine (Python)

**Severity:** required · **Stacks:** python · **ADR:** [0002-uv-as-dependency-manager](../adr/0002-uv-as-dependency-manager.md)

Un `pyproject.toml` conforme PEP 621 (section `[project]`) doit exister à
la racine. Champs minimum : `name`, `version`, `description`, `requires-python`,
`license`, `dependencies`.

### PK002 — `uv.lock` versionné (Python)

**Severity:** required · **Stacks:** python · **ADR:** [0002-uv-as-dependency-manager](../adr/0002-uv-as-dependency-manager.md)

Le fichier `uv.lock` produit par `uv lock` est commité au repo. Garantit
des installations reproductibles et permet les audits de sécurité par
hash de paquet.

### PK003 — Version Python pinned

**Severity:** required · **Stacks:** python

Le fichier `.python-version` à la racine fige la version Python utilisée
en local et en CI. La même valeur apparaît dans `pyproject.toml`
(`requires-python`) et dans le workflow CI.

### PK004 — Pas de `requirements.txt`

**Severity:** recommended · **Stacks:** python · **ADR:** [0002-uv-as-dependency-manager](../adr/0002-uv-as-dependency-manager.md)

`requirements.txt` n'est pas la source de vérité. Si un système legacy
l'exige, le générer à la volée via `uv export -o requirements.txt`
(et marquer le fichier `.gitignore`).
