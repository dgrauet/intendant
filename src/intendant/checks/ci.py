"""CI transverse rules."""

from __future__ import annotations

import re

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


# Markers that configure caching by their mere presence — either dedicated
# cache actions or setup-* actions whose cache is on by default. Each is
# documented; we only list ones that genuinely cache without an extra input.
_CACHE_MARKERS = (
    "enable-cache",  # astral-sh/setup-uv, oven-sh/setup-bun, … with caching turned on
    "actions/cache",  # the canonical low-level GitHub Actions cache
    "actions/setup-go",  # Go module + build cache (on by default since v4)
    "gradle/actions/setup-gradle",  # caches the Gradle user home by default
    "Swatinem/rust-cache",  # the de-facto standard cargo registry + target cache
    "mozilla-actions/sccache-action",  # sccache shared compilation cache
)

# Setup actions such as actions/setup-python, setup-node, setup-java and
# setup-dotnet only cache when given an explicit `cache:` input — their bare
# presence is NOT a cache signal. Match an actual `cache:` mapping key whose
# value is non-empty and not a disabled sentinel (false / none / null / ~ /
# no / off / 0 / empty), so `cache: pip` counts but `cache: false` does not.
_CACHE_INPUT_RE = re.compile(
    r"""^[ \t]*cache:[ \t]*
        (?!
            (?:false|none|null|no|off|0|~)\s*(?:\#.*)?$  # cache: false / none / ~ / …
            |['"]{2}\s*(?:\#.*)?$                        # cache: '' or ""
            |\s*(?:\#.*)?$                               # cache: (empty / block follows)
        )
        \S
    """,
    re.MULTILINE | re.VERBOSE,
)


class CI004CacheConfigured(Rule):
    id = "CI004"
    title = (
        "at least one workflow configures caching"
        " (enable-cache / actions/cache / a non-disabled cache: input)"
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
            if any(marker in text for marker in _CACHE_MARKERS) or _CACHE_INPUT_RE.search(text):
                return CheckResult(passing=True)
        return CheckResult(
            passing=False,
            evidence=(
                "no workflow configures caching (looked for enable-cache, actions/cache,"
                " setup-go / setup-gradle, Swatinem/rust-cache, sccache, or a non-disabled"
                " cache: input)"
            ),
        )
