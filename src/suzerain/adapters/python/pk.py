"""Python adapter PK (packaging & deps) rules."""

from __future__ import annotations

import re
import subprocess
import tomllib

from suzerain.core.patch import Patch
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

    def fix(self, repo: Repo, result: CheckResult) -> Patch | None:
        """Create a .python-version file pinned to the minimum required Python version.

        Resolution order:
        1. ``requires-python`` in pyproject.toml → extract minimum minor (e.g. ">=3.10" → "3.10")
        2. System ``python3 --version`` → major.minor
        3. Hard fallback → "3.11"
        """
        version = _resolve_python_version(repo)
        content = f"{version}\n"
        target = repo.path / ".python-version"
        diff = f"--- /dev/null\n+++ .python-version\n@@ -0,0 +1,1 @@\n+{version}\n"
        return Patch(
            target_path=target,
            kind="create",
            content=content,
            diff=diff,
            safe=True,
        )


def _resolve_python_version(repo: Repo) -> str:
    """Return a ``major.minor`` string for the Python version to pin."""
    # 1. Try requires-python from pyproject.toml
    pyproject = repo.path / "pyproject.toml"
    if pyproject.is_file():
        try:
            data = tomllib.loads(pyproject.read_text())
            requires = data.get("project", {}).get("requires-python", "")
            match = re.search(r"(\d+\.\d+)", requires)
            if match:
                return match.group(1)
        except tomllib.TOMLDecodeError:
            pass
    # 2. Try system python3
    try:
        out = subprocess.run(
            ["python3", "--version"],
            capture_output=True,
            text=True,
            timeout=3,
        )
        match = re.search(r"(\d+\.\d+)", out.stdout)
        if match:
            return match.group(1)
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    # 3. Hard fallback
    return "3.11"
