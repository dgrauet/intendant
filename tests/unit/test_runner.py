"""Tests for the audit runner."""

from pathlib import Path

from suzerain.audit.runner import run_audit
from suzerain.core.config import Exemption, SuzerainConfig
from suzerain.core.patch import Patch
from suzerain.core.repo import Repo
from suzerain.core.rule import CheckResult, Rule


class _PassingRule(Rule):
    id = "PASS001"
    title = "Always passes"
    severity = "required"
    stacks = ("*",)
    handbook_ref = "x"

    def check(self, repo: Repo) -> CheckResult:
        return CheckResult(passing=True)


class _FailingRule(Rule):
    id = "FAIL001"
    title = "Always fails"
    severity = "required"
    stacks = ("*",)
    handbook_ref = "x"

    def check(self, repo: Repo) -> CheckResult:
        return CheckResult(passing=False, evidence="missing X")

    def fix(self, repo: Repo, result: CheckResult) -> Patch | None:
        return Patch(
            target_path=repo.path / "X",
            kind="create",
            content="X\n",
            diff="...",
            safe=True,
        )


class _RaisingRule(Rule):
    id = "RAISE001"
    title = "Raises an exception"
    severity = "required"
    stacks = ("*",)
    handbook_ref = "x"

    def check(self, repo: Repo) -> CheckResult:
        raise RuntimeError("boom")


def test_run_audit_empty_rules(tmp_path: Path) -> None:
    repo = Repo(path=tmp_path, stack="python")
    config = SuzerainConfig(version="1", stack="python", mode="strict")
    report = run_audit(repo, config, rules=[])
    assert report.findings == []
    assert report.score == 100


def test_run_audit_passing_rule(tmp_path: Path) -> None:
    repo = Repo(path=tmp_path, stack="python")
    config = SuzerainConfig(version="1", stack="python", mode="strict")
    report = run_audit(repo, config, rules=[_PassingRule()])
    assert len(report.findings) == 1
    assert report.findings[0].status == "pass"


def test_run_audit_failing_rule_with_fix(tmp_path: Path) -> None:
    repo = Repo(path=tmp_path, stack="python")
    config = SuzerainConfig(version="1", stack="python", mode="strict")
    report = run_audit(repo, config, rules=[_FailingRule()])
    assert len(report.findings) == 1
    f = report.findings[0]
    assert f.status == "fail"
    assert f.fix_available is True
    assert f.fix_preview is not None


def test_run_audit_exempt_rule(tmp_path: Path) -> None:
    repo = Repo(path=tmp_path, stack="python")
    config = SuzerainConfig(
        version="1",
        stack="python",
        mode="strict",
        exemptions={"FAIL001": Exemption(reason="user-justified")},
    )
    report = run_audit(repo, config, rules=[_FailingRule()])
    assert len(report.findings) == 1
    f = report.findings[0]
    assert f.status == "exempt"
    assert "user-justified" in f.evidence


def test_run_audit_skipped_rule_when_not_applicable(tmp_path: Path) -> None:
    class _PythonOnly(Rule):
        id = "PY001"
        title = "Python only"
        severity = "required"
        stacks = ("python",)
        handbook_ref = "x"

        def check(self, repo: Repo) -> CheckResult:
            return CheckResult(passing=True)

    repo = Repo(path=tmp_path, stack="node")
    config = SuzerainConfig(version="1", stack="node", mode="strict")
    report = run_audit(repo, config, rules=[_PythonOnly()])
    assert len(report.findings) == 1
    assert report.findings[0].status == "skip"


def test_run_audit_handles_rule_exception(tmp_path: Path) -> None:
    repo = Repo(path=tmp_path, stack="python")
    config = SuzerainConfig(version="1", stack="python", mode="strict")
    report = run_audit(repo, config, rules=[_RaisingRule()])
    assert len(report.findings) == 1
    f = report.findings[0]
    assert f.status == "fail"
    assert "boom" in f.evidence


def test_run_audit_findings_in_rule_order(tmp_path: Path) -> None:
    repo = Repo(path=tmp_path, stack="python")
    config = SuzerainConfig(version="1", stack="python", mode="strict")
    rules = [_PassingRule(), _FailingRule()]
    report = run_audit(repo, config, rules=rules)
    assert [f.rule_id for f in report.findings] == ["PASS001", "FAIL001"]


def test_run_audit_skipped_check_emits_skip_status(tmp_path: Path) -> None:
    """A rule whose check() returns skipped=True is reported as status='skip'."""
    from suzerain.audit.runner import run_audit
    from suzerain.core.config import SuzerainConfig
    from suzerain.core.repo import Repo
    from suzerain.core.rule import CheckResult, Rule

    class SkippableRule(Rule):
        id = "ZZ999"
        title = "test"
        severity = "recommended"
        stacks = ("*",)
        handbook_ref = "n/a"

        def check(self, repo: Repo) -> CheckResult:
            return CheckResult(passing=True, evidence="precondition not met", skipped=True)

    repo = Repo(path=tmp_path, stack="auto")
    cfg = SuzerainConfig(version="1", stack="auto", mode="strict")
    report = run_audit(repo, cfg, [SkippableRule()])
    assert len(report.findings) == 1
    finding = report.findings[0]
    assert finding.status == "skip"
    assert finding.evidence == "precondition not met"
