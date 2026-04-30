"""Python adapter QU (quality) rules."""

from __future__ import annotations

from suzerain.adapters.python.inspectors import (
    has_pyproject,
    load_pyproject,
    pyproject_tool_section,
)
from suzerain.core.repo import Repo
from suzerain.core.rule import CheckResult, Rule


class QU001Ruff(Rule):
    id = "QU001"
    title = "ruff configured (pyproject.toml [tool.ruff] or ruff.toml)"
    severity = "required"
    stacks = ("python",)
    handbook_ref = "docs/handbook/04-quality.md#qu001"

    def check(self, repo: Repo) -> CheckResult:
        if pyproject_tool_section(repo.path, "ruff") is not None:
            return CheckResult(passing=True, evidence="[tool.ruff] in pyproject.toml")
        if (repo.path / "ruff.toml").is_file() or (repo.path / ".ruff.toml").is_file():
            return CheckResult(passing=True, evidence="ruff.toml present")
        return CheckResult(passing=False, evidence="no ruff configuration found")


class QU002Ty(Rule):
    """Type-checker present: ty (Astral, default) or pyright (fallback per ADR-0003)."""

    id = "QU002"
    title = "type-checker declared in deps (ty default, pyright fallback)"
    severity = "required"
    stacks = ("python",)
    handbook_ref = "docs/handbook/04-quality.md#qu002"
    adr_ref = "0003-ty-with-pyright-fallback"

    def check(self, repo: Repo) -> CheckResult:
        if not has_pyproject(repo.path):
            return CheckResult(passing=False, evidence="no pyproject.toml")
        data = load_pyproject(repo.path)
        if data is None:
            return CheckResult(passing=False, evidence="pyproject.toml unparseable")
        deps = _collect_dev_deps(data)
        if any(dep.startswith("ty") for dep in deps):
            return CheckResult(passing=True, evidence="ty declared in dev deps")
        if any(dep.startswith("pyright") for dep in deps):
            return CheckResult(
                passing=True,
                evidence="pyright fallback per ADR-0003",
            )
        return CheckResult(
            passing=False,
            evidence=f"neither ty nor pyright in dev deps; found: {sorted(deps)[:5]}",
        )


def _collect_dev_deps(pyproject: dict) -> set[str]:
    """Extract dev-group dep names (lowered first token) from both PEP 735 and PEP 621."""
    deps: set[str] = set()
    # PEP 735 [dependency-groups]
    groups = pyproject.get("dependency-groups", {})
    for grp_deps in groups.values():
        if isinstance(grp_deps, list):
            deps.update(_dep_name(d) for d in grp_deps if isinstance(d, str))
    # PEP 621 [project.optional-dependencies]
    optional = pyproject.get("project", {}).get("optional-dependencies", {})
    for grp_deps in optional.values():
        if isinstance(grp_deps, list):
            deps.update(_dep_name(d) for d in grp_deps if isinstance(d, str))
    return deps


def _dep_name(spec: str) -> str:
    """Extract package name from a PEP 508 spec like 'foo>=1.2'."""
    name = spec.split("[", 1)[0]
    for sep in ("==", ">=", "<=", "!=", "~=", ">", "<", " "):
        idx = name.find(sep)
        if idx != -1:
            name = name[:idx]
    return name.strip().lower()
