"""RL (releases) transverse rules."""

from __future__ import annotations

import json
import re
import subprocess
import tomllib

from suzerain.core.patch import Patch
from suzerain.core.repo import Repo
from suzerain.core.rule import CheckResult, Rule

_CHANGELOG_SKELETON = """# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
"""

# Conventional Commits 1.0 spec allows any lowercase alphabetic type;
# only `feat` and `fix` have semantic meaning. We match any [a-z]+
# type to avoid false positives on `release:` (release-please) and
# other widely-used extensions.
_CONV_COMMIT_RE = re.compile(r"^[a-z]+(\([^)]+\))?!?: .+")


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


class RL003ReleasePlease(Rule):
    id = "RL003"
    title = "release-please-config.json and .release-please-manifest.json present"
    severity = "required"
    stacks = ("*",)
    handbook_ref = "docs/handbook/07-releases.md#rl003"
    adr_ref = "0005-release-please"

    def check(self, repo: Repo) -> CheckResult:
        config = repo.path / "release-please-config.json"
        manifest = repo.path / ".release-please-manifest.json"
        missing = []
        if not config.is_file():
            missing.append("release-please-config.json")
        if not manifest.is_file():
            missing.append(".release-please-manifest.json")
        if missing:
            return CheckResult(
                passing=False,
                evidence=f"missing release-please files: {missing}",
            )
        return CheckResult(passing=True)

    def fix(self, repo: Repo, result: CheckResult) -> Patch | None:
        config_path = repo.path / "release-please-config.json"
        manifest_path = repo.path / ".release-please-manifest.json"

        # Need pyproject.toml for package name + version (Python only)
        pyproject_path = repo.path / "pyproject.toml"
        if not pyproject_path.is_file():
            return None
        try:
            pyproject = tomllib.loads(pyproject_path.read_text())
        except tomllib.TOMLDecodeError:
            return None
        name = pyproject.get("project", {}).get("name")
        version = pyproject.get("project", {}).get("version", "0.0.0")
        if not name:
            return None

        # Propose manifest first (smaller, simpler); config on second run
        if not manifest_path.is_file():
            content = json.dumps({".": str(version)}, indent=2) + "\n"
            return Patch(
                target_path=manifest_path,
                kind="create",
                content=content,
                diff="--- /dev/null\n+++ .release-please-manifest.json\n",
                safe=True,
            )

        # Manifest exists; propose config
        if not config_path.is_file():
            config = {
                "$schema": (
                    "https://raw.githubusercontent.com/googleapis/release-please"
                    "/main/schemas/config.json"
                ),
                "release-type": "python",
                "include-component-in-tag": False,
                "include-v-in-tag": True,
                "bump-minor-pre-major": True,
                "bump-patch-for-minor-pre-major": True,
                "packages": {
                    ".": {
                        "package-name": name,
                        "changelog-path": "CHANGELOG.md",
                    }
                },
            }
            return Patch(
                target_path=config_path,
                kind="create",
                content=json.dumps(config, indent=2) + "\n",
                diff="--- /dev/null\n+++ release-please-config.json\n",
                safe=True,
            )

        return None  # both exist, rule should have passed


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
