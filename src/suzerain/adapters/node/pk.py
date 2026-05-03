"""Node adapter NODE_PK (packaging) rules."""

from __future__ import annotations

from suzerain.adapters.node.inspectors import has_package_json, load_package_json
from suzerain.core.repo import Repo
from suzerain.core.rule import CheckResult, Rule

_LOCKFILES = ("package-lock.json", "pnpm-lock.yaml", "yarn.lock", "bun.lockb")


class NodePackageJson(Rule):
    id = "NODE_PK001"
    title = "package.json present at repo root"
    severity = "required"
    stacks = ("node",)
    handbook_ref = "docs/handbook/10-node.md#node_pk001"

    def check(self, repo: Repo) -> CheckResult:
        if has_package_json(repo.path):
            return CheckResult(passing=True, evidence="package.json found")
        return CheckResult(passing=False, evidence="package.json not found at repo root")


class NodeLockfile(Rule):
    id = "NODE_PK002"
    title = "lockfile present (npm/pnpm/yarn/bun)"
    severity = "required"
    stacks = ("node",)
    handbook_ref = "docs/handbook/10-node.md#node_pk002"

    def check(self, repo: Repo) -> CheckResult:
        present = [name for name in _LOCKFILES if (repo.path / name).is_file()]
        if present:
            return CheckResult(passing=True, evidence=f"lockfile(s) present: {present}")
        return CheckResult(
            passing=False,
            evidence=f"no lockfile found (looked for {list(_LOCKFILES)})",
        )


class NodeEnginesNode(Rule):
    id = "NODE_PK003"
    title = "engines.node declared in package.json"
    severity = "recommended"
    stacks = ("node",)
    handbook_ref = "docs/handbook/10-node.md#node_pk003"

    def check(self, repo: Repo) -> CheckResult:
        pkg = load_package_json(repo.path)
        if pkg is None:
            return CheckResult(
                passing=True,
                skipped=True,
                evidence="package.json missing or unparseable (covered by NODE_PK001)",
            )
        engines = pkg.get("engines")
        if not isinstance(engines, dict) or "node" not in engines:
            return CheckResult(
                passing=False,
                evidence="engines.node not declared in package.json",
            )
        return CheckResult(passing=True, evidence=f"engines.node = {engines['node']!r}")
