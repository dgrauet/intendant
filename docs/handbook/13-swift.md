# 13 — Swift

Convention de gouvernance pour les projets Swift / SwiftPM. Le Swift
adapter détecte les repos contenant un `Package.swift` à la racine. Les
règles couvrent le strict nécessaire pour un workflow Swift reproductible :
package déclaré, lockfile commité, version d'outillage pinnée, linter
configuré, tests présents, CI complète, et artefacts de build ignorés du
VCS.

## Rules

### SWIFT_PK001 — Package.swift present at repo root with a Package(name:) declaration

**Severity:** required · **Stacks:** swift

The repository must declare a `Package.swift` at its root containing a
`Package(name: "...")` constructor call. Without it, SwiftPM cannot
resolve dependencies or build the project.

### SWIFT_PK002 — Package.resolved present at repo root

**Severity:** recommended · **Stacks:** swift

`Package.resolved` should be committed at the repo root for reproducible
builds across contributors. For pure libraries with zero transitive
dependencies, this file may be empty but should still exist.

### SWIFT_PK003 — swift-tools-version pinned in Package.swift

**Severity:** recommended · **Stacks:** swift

The first line of `Package.swift` must declare a
`// swift-tools-version:<X.Y>` directive (e.g. `// swift-tools-version:5.9`).
Without it, SwiftPM falls back to a permissive default that can mask
compatibility issues across contributor environments.

### SWIFT_QU001 — swiftlint or swiftformat config present

**Severity:** recommended · **Stacks:** swift

A `.swiftlint.yml` (or `.swiftlint.yaml`/`.swiftformat`) at the repo root
makes the formatter/linter configuration explicit and reproducible. The
rule checks for the file's presence, not the content.

### SWIFT_TS001 — at least one Tests/**/*.swift file with a Test* function or @Test

**Severity:** recommended · **Stacks:** swift

The repository must contain at least one Swift file under `Tests/`
declaring a recognisable test: a `func test*(...)`, an `XCTestCase`
subclass, or a Swift Testing `@Test` annotation. The rule signals that
tests exist; it does not enforce coverage levels.

### SWIFT_CI001 — CI workflow runs swift build, swift test, and a linter

**Severity:** required · **Stacks:** swift

The CI workflow(s) under `.github/workflows/` must invoke `swift build`,
`swift test`, and a linter (`swiftlint`, `swiftformat`, or
`swift-format`). Skipped when no workflows directory exists (covered by
transverse `CI001`).

### SWIFT_SA001 — Swift .gitignore baseline (.build/, xcuserdata/)

**Severity:** required · **Stacks:** swift

The root `.gitignore` must include `.build/` (SwiftPM build artefacts)
and `xcuserdata/` (Xcode per-user state). Skipped when `.gitignore`
does not exist (covered by transverse `SA004`).
