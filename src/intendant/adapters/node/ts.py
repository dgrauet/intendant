"""Node adapter NODE_TS (tests) rules."""

from __future__ import annotations

from intendant.adapters.node.inspectors import collect_dep_names, load_package_json
from intendant.core.repo import Repo
from intendant.core.rule import CheckResult, Rule

_TEST_FRAMEWORKS = frozenset({"vitest", "jest", "mocha", "ava"})


class NodeTestFramework(Rule):
    id = "NODE_TS001"
    title = "test framework declared OR test script in package.json"
    severity = "required"
    stacks = ("node",)
    skipped_for_roles = ("frontend",)
    handbook_ref = "docs/handbook/10-node.md#node_ts001"

    def check(self, repo: Repo) -> CheckResult:
        pkg = load_package_json(repo.path)
        if pkg is None:
            return CheckResult(
                passing=True,
                skipped=True,
                evidence="package.json missing or unparseable (covered by NODE_PK001)",
            )
        deps = collect_dep_names(pkg)
        present_frameworks = sorted(d for d in deps if d in _TEST_FRAMEWORKS)
        if present_frameworks:
            return CheckResult(
                passing=True,
                evidence=f"test framework(s) declared: {present_frameworks}",
            )
        scripts = pkg.get("scripts", {})
        if isinstance(scripts, dict) and "test" in scripts:
            return CheckResult(
                passing=True,
                evidence=f"test script in package.json: {scripts['test']!r}",
            )
        return CheckResult(
            passing=False,
            evidence=(
                f"no test framework ({sorted(_TEST_FRAMEWORKS)}) and "
                f"no 'test' script in package.json"
            ),
        )
