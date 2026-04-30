"""RL (releases) transverse rules."""

from __future__ import annotations

import re
import subprocess

from suzerain.core.patch import Patch
from suzerain.core.repo import Repo
from suzerain.core.rule import CheckResult, Rule

_CHANGELOG_SKELETON = """# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
"""

_CONV_COMMIT_RE = re.compile(
    r"^(feat|fix|docs|chore|refactor|test|ci|perf|build|style|revert)(\([^)]+\))?!?: .+"
)


class RL001Changelog(Rule):
    id = "RL001"
    title = "CHANGELOG.md present, Keep-a-Changelog format"
    severity = "required"
    stacks = ("*",)
    handbook_ref = "docs/handbook/07-releases.md#rl001"
    adr_ref = "0005-release-please"
    template_ref = "templates/_common/CHANGELOG.skeleton.md"

    def check(self, repo: Repo) -> CheckResult:
        path = repo.path / "CHANGELOG.md"
        if not path.is_file():
            return CheckResult(passing=False, evidence="CHANGELOG.md not found")
        text = path.read_text()
        if "Keep a Changelog" not in text and "[Unreleased]" not in text:
            return CheckResult(
                passing=False,
                evidence="CHANGELOG.md does not follow Keep-a-Changelog format "
                "(no Keep a Changelog reference and no [Unreleased] section)",
            )
        return CheckResult(passing=True)

    def fix(self, repo: Repo, result: CheckResult) -> Patch | None:
        target = repo.path / "CHANGELOG.md"
        return Patch(
            target_path=target,
            kind="create" if not target.exists() else "overwrite",
            content=_CHANGELOG_SKELETON,
            diff="--- /dev/null\n+++ CHANGELOG.md\n",
            safe=True,
        )


class RL002ConventionalCommits(Rule):
    id = "RL002"
    title = "Recent commits follow Conventional Commits"
    severity = "required"
    stacks = ("*",)
    handbook_ref = "docs/handbook/07-releases.md#rl002"
    adr_ref = "0004-conventional-commits-strict"

    def check(self, repo: Repo) -> CheckResult:
        if not (repo.path / ".git").exists():
            return CheckResult(passing=True, evidence="not a git repo, rule advisory")
        try:
            out = subprocess.run(
                ["git", "log", "-n", "20", "--format=%s"],
                cwd=repo.path,
                capture_output=True,
                text=True,
                check=True,
                timeout=5,
            )
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
            return CheckResult(passing=False, evidence=f"git log failed: {exc}")
        violators = []
        for line in out.stdout.splitlines():
            if not line.strip():
                continue
            if line.startswith("Merge ") or line.startswith("Revert "):
                continue
            if not _CONV_COMMIT_RE.match(line):
                violators.append(line)
        if violators:
            return CheckResult(
                passing=False,
                evidence=f"non-conventional commit messages found: {violators[:3]}",
            )
        return CheckResult(passing=True)
