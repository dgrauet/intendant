# 09 — Skill (Claude Skill repositories)

Convention de gouvernance pour les repos contenant un Claude Skill standalone.
Le skill adapter détecte ces repos par la présence d'un fichier `SKILL.md`
à profondeur ≤ 2 (au format Anthropic, frontmatter YAML).

## Règles

### SK001 — SKILL.md présent

**Severity:** required · **Stacks:** skill

Le repo doit contenir au moins un fichier `SKILL.md` à profondeur 1 ou 2
(typiquement `<repo>/<skill-name>/SKILL.md`). Sans ce fichier, Claude ne
peut pas charger le skill.

### SK002 — Frontmatter valide

**Severity:** required · **Stacks:** skill

Le `SKILL.md` doit commencer par un bloc YAML `---` contenant au minimum
les champs `name` et `description`, tous deux non-vides. Un frontmatter
cassé empêche Claude de charger le skill.

### SK003 — Qualité de la description

**Severity:** recommended · **Stacks:** skill

Le champ `description` doit faire entre 10 et 1024 caractères. Trop court
indique un placeholder oublié ; trop long est tronqué dans le listing
de skills exposé à l'utilisateur.

### SK004 — `name` correspond au dossier

**Severity:** recommended · **Stacks:** skill

Le champ `name` du frontmatter doit être identique au nom du dossier
parent du `SKILL.md`. Convention forte attendue par la communauté ;
non enforcée par Claude mais utile pour la lisibilité.

### SK005 — `evals/` non-vide

**Severity:** recommended · **Stacks:** skill

Un dossier `evals/` à côté du `SKILL.md` doit exister et contenir au
moins un fichier d'eval (`.md`/`.json`/`.yaml`/`.txt`). Les evals
documentent les comportements attendus et permettent les régressions.

### SK006 — Dossiers référencés existants

**Severity:** recommended · **Stacks:** skill

Si le `SKILL.md` mentionne `references/` ou `scripts/` dans son corps
(hors blocs de code), ces dossiers doivent exister à côté du
`SKILL.md`. Empêche la doc rot où le texte promet des fichiers absents.

### SK007 — README documente le chemin d'installation

**Severity:** recommended · **Stacks:** skill

Le `README.md` racine doit mentionner soit `~/.claude/skills/` soit
`claude/plugins/` pour aider l'utilisateur à installer le skill. Un
fix automatique peut appendre le bloc d'installation standard. Si
`README.md` est absent, la règle est `skip` (DG003 couvre l'absence).
