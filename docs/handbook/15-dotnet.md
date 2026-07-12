# 15 — .NET

Governance convention for .NET / C# projects. The dotnet adapter
detects repos with a `*.csproj` or `*.sln` at the root. The rules cover
the bare minimum for a reproducible .NET workflow: declared project,
committed NuGet lockfile, nullable reference types enabled, style made
explicit via `.editorconfig`, tests present, complete CI, and build
artifacts ignored by the VCS.

## Rules

### DOTNET_PK001 — at least one .csproj declaring a TargetFramework

**Severity:** required · **Stacks:** dotnet

The repository must contain at least one `.csproj` (searched recursively,
build output excluded) declaring a `<TargetFramework>` or
`<TargetFrameworks>`. Without it, the .NET SDK cannot restore or build
the project deterministically.

### DOTNET_PK002 — NuGet lockfile (packages.lock.json) committed next to each project

**Severity:** recommended · **Stacks:** dotnet

Each project should opt into `<RestorePackagesWithLockFile>` and commit
the generated `packages.lock.json` next to its `.csproj` for reproducible
restores across contributors and CI.

### DOTNET_QU001 — nullable reference types enabled in every project

**Severity:** required · **Stacks:** dotnet

Every `.csproj` must enable `<Nullable>enable</Nullable>`, either directly
or through a `Directory.Build.props` up to the repo root. Nullable
reference types surface entire classes of `NullReferenceException` bugs
at compile time.

### DOTNET_QU002 — .editorconfig present (dotnet format / analyzers style source of truth)

**Severity:** recommended · **Stacks:** dotnet

An `.editorconfig` at the repo root makes formatting and analyzer
configuration explicit and reproducible — it is the configuration source
read by `dotnet format` and Roslyn analyzers. The rule checks for the
file's presence, not the content.

### DOTNET_TS001 — at least one test project (xunit / NUnit / MSTest)

**Severity:** recommended · **Stacks:** dotnet

The repository must contain at least one `.csproj` referencing a test
framework (`Microsoft.NET.Test.Sdk`, `xunit`, `NUnit`, or
`MSTest.TestFramework`). The rule signals that tests exist; it does not
enforce coverage levels.

### DOTNET_CI001 — CI workflow runs dotnet format, dotnet build, and dotnet test

**Severity:** required · **Stacks:** dotnet

The CI workflow(s) under `.github/workflows/` must invoke `dotnet format`
(with `--verify-no-changes`), `dotnet build`, and `dotnet test`. Skipped
when no workflows directory exists (covered by transverse `CI001`).

### DOTNET_SA001 — .NET .gitignore baseline (bin/, obj/)

**Severity:** required · **Stacks:** dotnet

The root `.gitignore` must include `bin/` and `obj/` (build output),
either plain or in `[Bb]in/`-style bracket form. Skipped when
`.gitignore` does not exist (covered by transverse `SA004`).
