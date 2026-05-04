"""Python adapter CI rules."""

from __future__ import annotations

from suzerain.core.repo import Repo
from suzerain.core.rule import CheckResult, Rule


class PYTHON_CI001MinimumSteps(Rule):  # noqa: N801
    id = "PYTHON_CI001"
    title = "CI workflow runs ruff + ty/pyright + pytest"
    severity = "required"
    stacks = ("python",)
    handbook_ref = "docs/handbook/03-ci.md#python_ci001"

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
        missing: list[str] = []
        if "ruff check" not in contents:
            missing.append("lint (ruff check)")
        if "ruff format" not in contents:
            missing.append("format (ruff format)")
        if "ty check" not in contents and "pyright" not in contents:
            missing.append("type (ty check or pyright)")
        if "pytest" not in contents and "unittest" not in contents:
            missing.append("test (pytest or unittest)")
        if missing:
            return CheckResult(
                passing=False,
                evidence=f"CI workflow(s) missing Python steps: {missing}",
            )
        return CheckResult(
            passing=True,
            evidence="CI workflow(s) include Python lint+format+type+test",
        )
