"""CI transverse rules."""

from __future__ import annotations

from suzerain.core.repo import Repo
from suzerain.core.rule import CheckResult, Rule


class CI001CIWorkflow(Rule):
    id = "CI001"
    title = ".github/workflows/ contains at least one CI workflow"
    severity = "required"
    stacks = ("*",)
    handbook_ref = "docs/handbook/03-ci.md#ci001"
    template_ref = "templates/github/ci.yml"

    def check(self, repo: Repo) -> CheckResult:
        wf_dir = repo.path / ".github" / "workflows"
        if not wf_dir.is_dir():
            return CheckResult(
                passing=False,
                evidence=".github/workflows/ directory not found",
            )
        workflows = list(wf_dir.glob("*.yml")) + list(wf_dir.glob("*.yaml"))
        if not workflows:
            return CheckResult(
                passing=False,
                evidence=".github/workflows/ exists but contains no workflow YAML files",
            )
        return CheckResult(passing=True)


class CI002MinimumSteps(Rule):
    id = "CI002"
    title = "CI workflow runs the minimum steps appropriate to the stack"
    severity = "required"
    stacks = ("*",)
    handbook_ref = "docs/handbook/03-ci.md#ci002"

    def check(self, repo: Repo) -> CheckResult:
        wf_dir = repo.path / ".github" / "workflows"
        if not wf_dir.is_dir():
            return CheckResult(
                passing=True,
                skipped=True,
                evidence="no .github/workflows/ directory (covered by CI001)",
            )
        contents = "\n".join(p.read_text(errors="replace") for p in wf_dir.glob("*.yml"))
        contents += "\n".join(p.read_text(errors="replace") for p in wf_dir.glob("*.yaml"))
        missing = self._missing_steps_for_stack(repo.stack, contents)
        if missing:
            return CheckResult(
                passing=False,
                evidence=f"CI workflow(s) missing steps for stack {repo.stack!r}: {missing}",
            )
        return CheckResult(
            passing=True,
            evidence=f"CI workflows include the minimum steps for stack {repo.stack!r}",
        )

    @staticmethod
    def _missing_steps_for_stack(stack: str, contents: str) -> list[str]:
        if stack == "node":
            return CI002MinimumSteps._missing_node(contents)
        if stack == "claude-skill":
            return CI002MinimumSteps._missing_claude_skill(contents)
        # python and any other (auto/generic) → python defaults
        return CI002MinimumSteps._missing_python(contents)

    @staticmethod
    def _missing_python(contents: str) -> list[str]:
        missing: list[str] = []
        if "ruff check" not in contents:
            missing.append("lint (ruff check)")
        if "ruff format" not in contents:
            missing.append("format (ruff format)")
        if "ty check" not in contents and "pyright" not in contents:
            missing.append("type (ty check or pyright)")
        if "pytest" not in contents and "unittest" not in contents:
            missing.append("test (pytest or unittest)")
        return missing

    @staticmethod
    def _missing_node(contents: str) -> list[str]:
        missing: list[str] = []
        lint_markers = ("eslint", "@biomejs/biome", "biome check", "biome lint", "npm run lint")
        if not any(m in contents for m in lint_markers):
            missing.append("lint (eslint or biome)")
        type_markers = ("tsc", "typecheck", "pyright")
        if not any(m in contents for m in type_markers):
            missing.append("type (tsc / npm run typecheck / pyright)")
        test_markers = ("vitest", "jest", "mocha", "ava", "bun test", "npm test", "npm run test")
        if not any(m in contents for m in test_markers):
            missing.append("test (vitest/jest/mocha/ava/bun test)")
        return missing

    @staticmethod
    def _missing_claude_skill(contents: str) -> list[str]:
        missing: list[str] = []
        if "suzerain audit" not in contents:
            missing.append("suzerain audit step")
        return missing


class CI003CommitMessageValidation(Rule):
    id = "CI003"
    title = "CI validates commit messages (conventional commits)"
    severity = "required"
    stacks = ("*",)
    handbook_ref = "docs/handbook/03-ci.md#ci003"
    adr_ref = "0004-conventional-commits-strict"

    def check(self, repo: Repo) -> CheckResult:
        wf_dir = repo.path / ".github" / "workflows"
        if not wf_dir.is_dir():
            return CheckResult(
                passing=True,
                skipped=True,
                evidence="no .github/workflows/ directory (covered by CI001)",
            )
        contents = "\n".join(p.read_text(errors="replace") for p in wf_dir.glob("*.yml"))
        contents += "\n".join(p.read_text(errors="replace") for p in wf_dir.glob("*.yaml"))
        markers = ("cz check", "commitizen-action", "commitlint", "wagoid/commitlint")
        if any(m in contents for m in markers):
            return CheckResult(passing=True, evidence="commit-message validation step found in CI")
        return CheckResult(
            passing=False,
            evidence="no commit-message validation step found in any CI workflow",
        )


_CACHE_MARKERS = ("enable-cache", "actions/cache", "actions/setup-python", "actions/setup-node")


class CI004CacheConfigured(Rule):
    id = "CI004"
    title = (
        "at least one workflow configures caching"
        " (enable-cache / actions/cache / actions/setup-node)"
    )
    severity = "recommended"
    stacks = ("*",)
    handbook_ref = "docs/handbook/03-ci.md#ci004"

    def check(self, repo: Repo) -> CheckResult:
        wf_dir = repo.path / ".github" / "workflows"
        if not wf_dir.is_dir():
            return CheckResult(passing=True, evidence="no .github/workflows/ directory — skip")
        workflows = list(wf_dir.glob("*.yml")) + list(wf_dir.glob("*.yaml"))
        for wf in workflows:
            text = wf.read_text()
            if any(marker in text for marker in _CACHE_MARKERS):
                return CheckResult(passing=True)
        return CheckResult(
            passing=False,
            evidence=(
                "no workflow mentions enable-cache, actions/cache, actions/setup-python,"
                " or actions/setup-node with cache config"
            ),
        )
