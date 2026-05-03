"""Node adapter NODE_QU (quality) rules."""

from __future__ import annotations

from suzerain.adapters.node.inspectors import collect_dep_names, load_package_json
from suzerain.core.repo import Repo
from suzerain.core.rule import CheckResult, Rule

_LINTERS = frozenset({"eslint", "@biomejs/biome", "prettier"})


class NodeLinter(Rule):
    id = "NODE_QU001"
    title = "linter declared in devDependencies (eslint/biome/prettier)"
    severity = "required"
    stacks = ("node",)
    handbook_ref = "docs/handbook/10-node.md#node_qu001"

    def check(self, repo: Repo) -> CheckResult:
        pkg = load_package_json(repo.path)
        if pkg is None:
            return CheckResult(
                passing=True,
                skipped=True,
                evidence="package.json missing or unparseable (covered by NODE_PK001)",
            )
        deps = collect_dep_names(pkg)
        present = sorted(d for d in deps if d in _LINTERS)
        if present:
            return CheckResult(passing=True, evidence=f"linter(s) declared: {present}")
        return CheckResult(
            passing=False,
            evidence=f"no linter declared (looked for {sorted(_LINTERS)})",
        )


class NodeTypeScript(Rule):
    id = "NODE_QU002"
    title = "TypeScript present (typescript dep or tsconfig.json)"
    severity = "recommended"
    stacks = ("node",)
    handbook_ref = "docs/handbook/10-node.md#node_qu002"

    def check(self, repo: Repo) -> CheckResult:
        pkg = load_package_json(repo.path)
        if pkg is None:
            return CheckResult(
                passing=True,
                skipped=True,
                evidence="package.json missing or unparseable (covered by NODE_PK001)",
            )
        deps = collect_dep_names(pkg)
        if "typescript" in deps:
            return CheckResult(passing=True, evidence="typescript declared in deps")
        if (repo.path / "tsconfig.json").is_file():
            return CheckResult(passing=True, evidence="tsconfig.json present")
        return CheckResult(
            passing=False,
            evidence="no TypeScript signal (typescript dep or tsconfig.json)",
        )
