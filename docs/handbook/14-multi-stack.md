# 14 — Multi-stack repositories

Référence de la déclaration multi-langage dans `.intendant.toml`. Cette
page n'introduit aucune règle : elle documente comment la composition
de stacks d'un repo est résolue, et comment déclarer plusieurs
sous-projets cohabitant dans un même dépôt.

## Resolution model

À l'audit, intendant construit une composition de stacks par repo selon
trois modes, dans l'ordre :

1. **Manual top-level pin** — `[intendant] stack = "<name>"` épingle un
   seul stack pour tout le repo. `mode = "manual"`.
2. **Manual subprojects** — un ou plusieurs `[[subprojects]]` déclarent
   explicitement chaque sous-projet avec son chemin et son stack.
   `mode = "manual"`.
3. **Auto-detection** — si ni `stack` ni `[[subprojects]]` ne sont
   présents (ou si `stack = "auto"`, sentinelle legacy), intendant
   parcourt la racine et détecte chaque stack via ses marqueurs
   (`pyproject.toml`, `package.json`, `Cargo.toml`, `go.mod`,
   `Package.swift`, et un walk pour `SKILL.md`). `mode = "auto"`.

Top-level `stack` et `[[subprojects]]` sont mutuellement exclusifs en
intention : si les deux sont déclarés, `[[subprojects]]` prime pour le
routage des règles par chemin, et `stack` retombe à un rôle informatif.
Préférez l'un ou l'autre.

## Single-stack repo

Cas le plus courant : un seul langage, à la racine. Deux options.

**Auto-detection (recommandé)** — laisser intendant détecter :

```toml
[intendant]
version = "1"
enforcement = "strict"
```

**Manual pin** — utile pour figer le stack quand l'auto-détection est
ambiguë (ex. un `pyproject.toml` présent uniquement pour la config de
tooling) :

```toml
[intendant]
version = "1"
stack = "python"
enforcement = "strict"
```

## Multi-stack repo

Quand un repo héberge plusieurs sous-projets dans des langages
différents (ex. backend Python + frontend Node + skill Claude),
déclarez chaque sous-projet via `[[subprojects]]` :

```toml
[intendant]
version = "1"
enforcement = "strict"

[[subprojects]]
name = "backend"
path = "services/api"
stack = "python"

[[subprojects]]
name = "frontend"
path = "apps/web"
stack = "node"

[[subprojects]]
name = "agent-skill"
path = "skills/triage"
stack = "claude-skill"
```

Chaque sous-projet est audité indépendamment : seules les règles
transverses (`DG`, `LO003`, `RL`, `CI`, `SA`, `TS`) et les règles de
son stack lui sont appliquées.

### Subproject fields

| Champ   | Requis    | Description                                                        |
| ------- | --------- | ------------------------------------------------------------------ |
| `path`  | oui       | Chemin relatif depuis la racine du repo. `"."` désigne la racine.  |
| `stack` | oui       | Un des stacks supportés : `python`, `node`, `claude-skill`, `rust`, `go`, `swift`. |
| `name`  | optionnel | Identifiant du sous-projet. Défaut : `basename(path)`, ou `"root"` si `path = "."`. |

### Constraints

Le parser rejette toute config qui ne respecte pas ces invariants :

- `path` doit être relatif (pas de chemin absolu) et ne pas contenir
  `..`.
- `name` doit matcher `[a-zA-Z0-9_-]+`.
- Les `name` doivent être uniques au sein du repo.
- Les `path` doivent être uniques au sein du repo.
- `path` et `stack` sont obligatoires ; leur absence fait échouer
  `intendant audit` avec une erreur explicite.

### Root as one subproject among others

`path = "."` est valide et permet d'inclure la racine comme un
sous-projet normal à côté d'autres :

```toml
[[subprojects]]
path = "."
stack = "python"

[[subprojects]]
path = "skills/triage"
stack = "claude-skill"
```

Le sous-projet racine prend `name = "root"` par défaut.

## Scoped exemptions

Les exemptions peuvent être déclarées au niveau global ou scopées à un
sous-projet précis via `[exemptions.<subproject_name>]`. La résolution
suit l'ordre : **scoped d'abord, puis global**.

```toml
# Exemption globale : s'applique à tous les sous-projets
[exemptions]
DG004 = { reason = "License pending legal review", until = "2026-06-30" }

# Exemption scopée : ne s'applique qu'au sous-projet `backend`
[exemptions.backend]
PYTHON_QU002 = "Ruff config inherited from monorepo root, not duplicated here"

# Exemption scopée : ne s'applique qu'à `frontend`
[exemptions.frontend]
NODE_TS001 = { reason = "Tests live in a sibling repo for now", until = "2026-09-01" }
```

Chaque exemption peut être :

- une **chaîne** — équivaut à `{ reason = "<chaîne>" }`, sans date
  d'expiration ;
- une **table** avec `reason` (obligatoire) et `until` (optionnel,
  format ISO `YYYY-MM-DD`).

Une exemption n'efface pas le finding : il apparaît comme
`EXEMPT(reason)` dans le rapport. La dette technique reste visible.

## Reports and CI

- Le rapport `intendant audit` rend chaque sous-projet sous sa propre
  section ; le format JSON renvoie un champ `subprojects[]` avec un
  bloc par sous-projet.
- `enforcement` (`strict`/`recommended`/`advisory`) reste défini une
  seule fois au top-level et s'applique uniformément à tous les
  sous-projets.
- Le portfolio report (`intendant report`) liste les stacks détectés
  par repo ; un repo multi-stack apparaît avec sa composition réelle,
  sans sentinelle `"multi"`.

## See also

- [00 — Charter](00-charter.md) — modèle d'exemption et niveaux de
  conformité.
- ADR-0006 — *Python harness, PyO3 escape hatch* : pourquoi
  l'architecture rend l'ajout d'un stack équivalent à la création d'un
  dossier d'adaptateur.
