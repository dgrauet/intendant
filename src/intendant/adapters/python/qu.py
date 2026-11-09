"""Python adapter QU (quality) rules."""

from __future__ import annotations

import re
import subprocess
import tomllib
from pathlib import Path

from intendant.adapters.python.inspectors import (
    has_pyproject,
    load_pyproject,
    pyproject_tool_section,
)
from intendant.core.repo import Repo
from intendant.core.rule import CheckResult, Rule


class QU001Ruff(Rule):
    id = "PYTHON_QU001"
    title = "ruff configured (pyproject.toml [tool.ruff] or ruff.toml)"
    severity = "required"
    stacks = ("python",)
    handbook_ref = "docs/handbook/04-quality.md#python_qu001"

    def check(self, repo: Repo) -> CheckResult:
        if pyproject_tool_section(repo.path, "ruff") is not None:
            return CheckResult(passing=True, evidence="[tool.ruff] in pyproject.toml")
        if (repo.path / "ruff.toml").is_file() or (repo.path / ".ruff.toml").is_file():
            return CheckResult(passing=True, evidence="ruff.toml present")
        return CheckResult(passing=False, evidence="no ruff configuration found")


class QU002Ty(Rule):
    """Type-checker present: ty (Astral, default) or pyright (fallback per ADR-0003)."""

    id = "PYTHON_QU002"
    title = "type-checker declared in deps (ty default, pyright fallback)"
    severity = "required"
    stacks = ("python",)
    handbook_ref = "docs/handbook/04-quality.md#python_qu002"
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


class QU003StrictTypeAnnotations(Rule):
    id = "PYTHON_QU003"
    title = "strict type-checker config (ty/pyright/mypy strict mode)"
    severity = "required"
    stacks = ("python",)
    handbook_ref = "docs/handbook/04-quality.md#python_qu003"
    adr_ref = "0003-ty-with-pyright-fallback"

    def check(self, repo: Repo) -> CheckResult:
        if not has_pyproject(repo.path):
            return CheckResult(
                passing=True,
                skipped=True,
                evidence="no pyproject.toml (rule does not apply)",
            )
        # Pyright config file at repo root counts as strict declaration
        if (repo.path / "pyrightconfig.json").is_file():
            return CheckResult(
                passing=True, evidence="pyrightconfig.json present (strict mode assumed)"
            )
        ty_section = pyproject_tool_section(repo.path, "ty") or {}
        if ty_section.get("strict") is True:
            return CheckResult(passing=True, evidence="[tool.ty] strict = true")
        # ty's strict-mode config may live under [tool.ty.rules] or similar — for v1 we
        # accept any [tool.ty] section as opt-in (presence → strict assumed).
        if pyproject_tool_section(repo.path, "ty") is not None:
            return CheckResult(passing=True, evidence="[tool.ty] section present (strict assumed)")
        pyright = pyproject_tool_section(repo.path, "pyright") or {}
        if pyright.get("strict") is True or pyright.get("typeCheckingMode") == "strict":
            return CheckResult(passing=True, evidence="[tool.pyright] strict mode")
        mypy = pyproject_tool_section(repo.path, "mypy") or {}
        if mypy.get("strict") is True:
            return CheckResult(passing=True, evidence="[tool.mypy] strict = true")
        return CheckResult(
            passing=False,
            evidence=(
                "no strict type-checker config found"
                " ([tool.ty]/[tool.pyright]/[tool.mypy]/pyrightconfig.json)"
            ),
        )


class QU004TyCheck(Rule):
    """Run `ty check` against the repo; skip if ty/pyright not in deps.

    When the repo declares `ty`, run the version pinned in its `uv.lock`
    through `uvx ty==<version>`. The lockfile is only read as data: the audited
    project is never synced or built (`uv run` would execute its build backend,
    i.e. arbitrary code from the repo under audit). Without a usable locked
    version, fall back to the latest `ty`.
    """

    id = "PYTHON_QU004"
    title = "ty check passes (Python type-checker)"
    severity = "recommended"
    stacks = ("python",)
    handbook_ref = "docs/handbook/04-quality.md#python_qu004"
    adr_ref = "0003-ty-with-pyright-fallback"

    def applies(self, repo: Repo) -> bool:
        if not super().applies(repo):
            return False
        # Only run if ty is declared in dev deps OR pyright (fallback path).
        # Reuse the dep collection logic from QU002.
        data = load_pyproject(repo.path)
        if data is None:
            return False
        deps = _collect_dev_deps(data)
        return any(d.startswith(("ty", "pyright")) for d in deps)

    def check(self, repo: Repo) -> CheckResult:
        data = load_pyproject(repo.path)
        ty_declared = data is not None and "ty" in _collect_dev_deps(data)
        version = _locked_ty_version(repo.path) if ty_declared else None
        command = ["uvx", f"ty=={version}" if version else "ty", "check"]
        try:
            result = subprocess.run(
                command,
                cwd=repo.path,
                capture_output=True,
                text=True,
                timeout=60,
            )
        except (subprocess.TimeoutExpired, FileNotFoundError) as exc:
            return CheckResult(passing=False, evidence=f"ty invocation failed: {exc}")
        if result.returncode == 0:
            return CheckResult(passing=True)
        # Capture the diagnostic count from the last line, if present
        output = (result.stdout or "") + (result.stderr or "")
        last_line = output.rstrip().rsplit("\n", 1)[-1] if output else ""
        if last_line.startswith("Found"):
            return CheckResult(passing=False, evidence=last_line)
        detail = f": {last_line}" if last_line else ""
        return CheckResult(passing=False, evidence=f"ty exited {result.returncode}{detail}")


_PLAIN_VERSION = re.compile(r"[0-9]+(\.[0-9]+)*((a|b|rc)[0-9]+)?(\.post[0-9]+)?(\.dev[0-9]+)?")


def _locked_ty_version(repo_path: Path) -> str | None:
    """Return the `ty` version pinned in `uv.lock`, or None if there is no usable one.

    The value ends up in a `uvx` requirement, so anything that is not a plain
    version number (e.g. a direct URL reference) is rejected.
    """
    try:
        lock = tomllib.loads((repo_path / "uv.lock").read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, tomllib.TOMLDecodeError):
        return None
    packages = lock.get("package", [])
    if not isinstance(packages, list):
        return None
    for package in packages:
        if isinstance(package, dict) and package.get("name") == "ty":
            version = package.get("version")
            if isinstance(version, str) and _PLAIN_VERSION.fullmatch(version):
                return version
            return None
    return None


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
