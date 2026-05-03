# 10 — Node / TypeScript

Convention de gouvernance pour les projets Node.js et TypeScript. Le Node
adapter détecte les repos contenant un `package.json` à la racine. Les règles
sont volontairement agnostiques quant aux outils — elles vérifient la présence
d'un linter / framework de tests / lockfile sans imposer un choix particulier
(npm vs pnpm vs yarn vs bun ; eslint vs biome ; vitest vs jest etc.).

## Rules

### NODE_PK001 — package.json present

**Severity:** required · **Stacks:** node

The repository must declare a `package.json` at its root. Absence means
the project is not a Node project (rule does not enforce stack detection;
only that, if classified as Node, the manifest exists).

### NODE_PK002 — lockfile present

**Severity:** required · **Stacks:** node

A lockfile pinning transitive dependencies must exist at the root. Any
of `package-lock.json` (npm), `pnpm-lock.yaml` (pnpm), `yarn.lock`
(yarn), or `bun.lockb` (bun) satisfies the rule.

### NODE_PK003 — engines.node declared

**Severity:** recommended · **Stacks:** node

`package.json` should declare an `engines.node` field documenting the
required Node.js version range. Avoids subtle runtime errors when team
members or CI use mismatched Node versions.

### NODE_QU001 — linter declared

**Severity:** required · **Stacks:** node

A linter must be declared in `devDependencies` (or any deps section).
Acceptable: `eslint`, `@biomejs/biome`, `prettier`. The rule verifies
the package is declared, not that it is configured or wired into CI.

### NODE_QU002 — TypeScript present

**Severity:** recommended · **Stacks:** node

A TypeScript-related signal should be present: either `typescript` in
deps OR `tsconfig.json` at the repo root. Recommended because pure
JavaScript projects exist and are valid; the rule nudges toward TS
adoption without forcing it.

### NODE_TS001 — test framework or test script

**Severity:** required · **Stacks:** node

Either a recognized test framework (`vitest`, `jest`, `mocha`, `ava`)
must be declared in deps, OR `package.json` must define a `test` script
under `[scripts]`. Allows custom test runners (e.g., `bun test`) to
satisfy the rule via the script.
