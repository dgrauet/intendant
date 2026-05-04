# 11 — Rust

Convention de gouvernance pour les projets Rust. Le Rust adapter détecte les
repos contenant un `Cargo.toml` à la racine. Les règles couvrent le strict
nécessaire pour un workflow Cargo reproductible : manifeste valide, lockfile
commité, edition pinnée, toolchain pinnée, tests présents, CI complète, et
`target/` ignoré du VCS.

## Rules

### RUST_PK001 — Cargo.toml present at repo root with [package] section

**Severity:** required · **Stacks:** rust

The repository must declare a `Cargo.toml` at its root containing either a
`[package]` section (binary or library crate) or a `[workspace]` section
(workspace root). Workspace roots are accepted because their member crates
have their own `Cargo.toml` files.

### RUST_PK002 — Cargo.lock present at repo root

**Severity:** required · **Stacks:** rust

`Cargo.lock` must be committed at the repo root for reproducible builds.
For pure library crates published to crates.io, this rule may be exempted
in `.suzerain.toml` with a documented reason — but most modern guidance
recommends committing the lockfile even for libraries to surface upstream
breakage in CI.

### RUST_PK003 — edition pinned in Cargo.toml [package]

**Severity:** recommended · **Stacks:** rust

The `[package]` table should declare an explicit `edition` field
(e.g. `edition = "2021"`). Without it, Cargo silently defaults to the
2015 edition, which lacks most modern syntax improvements.

### RUST_QU001 — rust-toolchain.toml pins the toolchain

**Severity:** recommended · **Stacks:** rust

A `rust-toolchain.toml` (or legacy `rust-toolchain`) at the repo root
pins the channel and components used to build the project. Avoids subtle
"works on my machine" issues when contributors use mismatched compilers
or are missing `rustfmt` / `clippy`.

### RUST_TS001 — at least one #[test] annotation under src/ or tests/

**Severity:** recommended · **Stacks:** rust

The crate must contain at least one `#[test]` annotation in either an
inline `#[cfg(test)]` module under `src/` or an integration test file
under `tests/`. The rule signals that tests exist; it does not enforce
coverage levels.

### RUST_CI001 — CI workflow runs cargo fmt, clippy, and test

**Severity:** required · **Stacks:** rust

The CI workflow(s) under `.github/workflows/` must invoke `cargo fmt`
(or `rustfmt`), `cargo clippy`, and `cargo test` (or `cargo nextest`).
Skipped when no workflows directory exists (covered by transverse
`CI001`).

### RUST_SA001 — Rust .gitignore baseline (target/)

**Severity:** required · **Stacks:** rust

The root `.gitignore` must contain `target/` to exclude Cargo's build
artifacts from version control. Skipped when `.gitignore` does not exist
(covered by transverse `SA004`).
