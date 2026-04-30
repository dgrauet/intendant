"""Python adapter PK (packaging & deps) rules."""

from __future__ import annotations

import tomllib

from suzerain.core.repo import Repo
from suzerain.core.rule import CheckResult, Rule


class PK001PyprojectExists(Rule):
    id = "PK001"
    title = "pyproject.toml exists with [project] section"
    severity = "required"
    stacks = ("python",)
    handbook_ref = "docs/handbook/02-packaging.md#pk001"
    adr_ref = "0002-uv-as-dependency-manager"

    def check(self, repo: Repo) -> CheckResult:
        path = repo.path / "pyproject.toml"
        if not path.is_file():
            return CheckResult(passing=False, evidence="pyproject.toml not found")
        try:
            data = tomllib.loads(path.read_text())
        except tomllib.TOMLDecodeError as exc:
            return CheckResult(passing=False, evidence=f"invalid TOML: {exc}")
        if "project" not in data:
            return CheckResult(passing=False, evidence="missing [project] section")
        return CheckResult(passing=True)


class PK002UvLock(Rule):
    id = "PK002"
    title = "uv.lock present and committed"
    severity = "required"
    stacks = ("python",)
    handbook_ref = "docs/handbook/02-packaging.md#pk002"
    adr_ref = "0002-uv-as-dependency-manager"

    def check(self, repo: Repo) -> CheckResult:
        if (repo.path / "uv.lock").is_file():
            return CheckResult(passing=True)
        return CheckResult(passing=False, evidence="uv.lock not found at repo root")


class PK003PythonVersion(Rule):
    id = "PK003"
    title = ".python-version pinned"
    severity = "required"
    stacks = ("python",)
    handbook_ref = "docs/handbook/02-packaging.md#pk003"

    def check(self, repo: Repo) -> CheckResult:
        path = repo.path / ".python-version"
        if not path.is_file():
            return CheckResult(passing=False, evidence=".python-version not found")
        if not path.read_text().strip():
            return CheckResult(passing=False, evidence=".python-version is empty")
        return CheckResult(passing=True)
