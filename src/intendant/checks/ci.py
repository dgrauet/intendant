"""CI transverse rules."""

from __future__ import annotations

from intendant.core.repo import Repo
from intendant.core.rule import CheckResult, Rule


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
