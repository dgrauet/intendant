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


_CACHE_MARKERS = ("enable-cache", "actions/cache", "actions/setup-python")


class CI004CacheConfigured(Rule):
    id = "CI004"
    title = "at least one workflow configures caching (enable-cache / actions/cache)"
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
                "no workflow mentions enable-cache, actions/cache, or actions/setup-python"
                " with cache config"
            ),
        )
