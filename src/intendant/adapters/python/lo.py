"""Python adapter LO (layout) rules."""

from __future__ import annotations

from intendant.adapters.python.inspectors import has_pyproject
from intendant.core.repo import Repo
from intendant.core.rule import CheckResult, Rule


class LO001SrcLayout(Rule):
    id = "PYTHON_LO001"
    title = "Python project uses src/ layout"
    severity = "required"
    stacks = ("python",)
    handbook_ref = "docs/handbook/01-layout.md#python_lo001"
    adr_ref = "0001-layout-src-vs-flat"

    def check(self, repo: Repo) -> CheckResult:
        if not has_pyproject(repo.path):
            return CheckResult(
                passing=True, evidence="no pyproject.toml — PYTHON_LO001 inconclusive"
            )
        src_dir = repo.path / "src"
        if src_dir.is_dir():
            packages = [
                p for p in src_dir.iterdir() if p.is_dir() and (p / "__init__.py").is_file()
            ]
            if packages:
                return CheckResult(passing=True)
            return CheckResult(passing=False, evidence="src/ exists but contains no Python package")
        return CheckResult(
            passing=False, evidence="src/ directory not found; project uses flat layout"
        )


class LO002TestsAtRoot(Rule):
    id = "PYTHON_LO002"
    title = "tests/ directory at repo root"
    severity = "required"
    stacks = ("python",)
    handbook_ref = "docs/handbook/01-layout.md#python_lo002"
    adr_ref = "0001-layout-src-vs-flat"

    def check(self, repo: Repo) -> CheckResult:
        if (repo.path / "tests").is_dir():
            return CheckResult(passing=True)
        return CheckResult(passing=False, evidence="tests/ directory not found at repo root")
