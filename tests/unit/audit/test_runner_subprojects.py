"""Tests for multi-subproject audit orchestration."""

from __future__ import annotations

from pathlib import Path

from intendant.audit.runner import run_audit
from intendant.core.config import IntendantConfig
from intendant.core.repo import Repo
from intendant.core.rule import CheckResult, Rule
from intendant.core.subproject import Subproject


class _AlwaysPassPython(Rule):
    id = "ZZ_PY"
    title = "always pass python"
    severity = "required"
    stacks = ("python",)
    handbook_ref = "n/a"

    def check(self, repo: Repo) -> CheckResult:
        return CheckResult(passing=True, evidence=f"on {repo.path.name}")


class _AlwaysPassNode(Rule):
    id = "ZZ_NODE"
    title = "always pass node"
    severity = "required"
    stacks = ("node",)
    handbook_ref = "n/a"

    def check(self, repo: Repo) -> CheckResult:
        return CheckResult(passing=True, evidence=f"on {repo.path.name}")


class _AlwaysPassTransverse(Rule):
    id = "ZZ_TRANSVERSE"
    title = "always pass transverse"
    severity = "required"
    stacks = ("*",)
    handbook_ref = "n/a"

    def check(self, repo: Repo) -> CheckResult:
        return CheckResult(passing=True, evidence="root")


def _make_dirs(root: Path, *paths: str) -> None:
    for p in paths:
        (root / p).mkdir(parents=True, exist_ok=True)


def test_multi_subproject_runs_transverse_at_root(tmp_path: Path) -> None:
    _make_dirs(tmp_path, "backend", "frontend")
    repo = Repo(path=tmp_path, stacks=("multi",))
    cfg = IntendantConfig(
        version="1",
        stack=None,
        enforcement="strict",
        subprojects=[
            Subproject(name="backend", path="backend", stack="python"),
            Subproject(name="frontend", path="frontend", stack="node"),
        ],
    )
    rules = [_AlwaysPassTransverse(), _AlwaysPassPython(), _AlwaysPassNode()]
    report = run_audit(repo, cfg, rules)
    transverse_findings = [f for f in report.findings if f.rule_id == "ZZ_TRANSVERSE"]
    assert len(transverse_findings) == 1
    assert transverse_findings[0].subproject is None


def test_multi_subproject_runs_stack_rules_per_subproject(tmp_path: Path) -> None:
    _make_dirs(tmp_path, "backend", "frontend")
    repo = Repo(path=tmp_path, stacks=("multi",))
    cfg = IntendantConfig(
        version="1",
        stack=None,
        enforcement="strict",
        subprojects=[
            Subproject(name="backend", path="backend", stack="python"),
            Subproject(name="frontend", path="frontend", stack="node"),
        ],
    )
    rules = [_AlwaysPassTransverse(), _AlwaysPassPython(), _AlwaysPassNode()]
    report = run_audit(repo, cfg, rules)
    py_findings = [f for f in report.findings if f.rule_id == "ZZ_PY"]
    node_findings = [f for f in report.findings if f.rule_id == "ZZ_NODE"]
    assert len(py_findings) == 1
    assert py_findings[0].subproject == "backend"
    assert len(node_findings) == 1
    assert node_findings[0].subproject == "frontend"


def test_multi_subproject_skips_when_path_missing(tmp_path: Path) -> None:
    repo = Repo(path=tmp_path, stacks=("multi",))
    cfg = IntendantConfig(
        version="1",
        stack=None,
        enforcement="strict",
        subprojects=[Subproject(name="backend", path="backend", stack="python")],
    )
    rules = [_AlwaysPassPython()]
    report = run_audit(repo, cfg, rules)
    findings = [f for f in report.findings if f.rule_id == "ZZ_PY"]
    assert len(findings) == 1
    assert findings[0].status == "skip"
    assert "subproject path not found" in findings[0].evidence


def test_single_subproject_implicit_no_subprojects_block(tmp_path: Path) -> None:
    """Backward compat: config without subprojects runs as before."""
    repo = Repo(path=tmp_path, stacks=("python",))
    cfg = IntendantConfig(version="1", stack="python", enforcement="strict")
    rules = [_AlwaysPassTransverse(), _AlwaysPassPython()]
    report = run_audit(repo, cfg, rules)
    rule_ids = {f.rule_id for f in report.findings}
    assert rule_ids == {"ZZ_TRANSVERSE", "ZZ_PY"}
    for f in report.findings:
        assert f.subproject is None
