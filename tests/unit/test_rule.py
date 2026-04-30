"""Tests for the Rule abstract base class."""

from pathlib import Path

import pytest

from suzerain.core.repo import Repo
from suzerain.core.rule import CheckResult, Rule


class _PassingRule(Rule):
    id = "TST001"
    title = "Test passing rule"
    severity = "required"
    stacks = ("*",)
    handbook_ref = "docs/handbook/99-test.md#tst001"

    def check(self, repo: Repo) -> CheckResult:
        return CheckResult(passing=True)


class _FailingRule(Rule):
    id = "TST002"
    title = "Test failing rule"
    severity = "recommended"
    stacks = ("python",)
    handbook_ref = "docs/handbook/99-test.md#tst002"
    adr_ref = "9999-test-decision"

    def check(self, repo: Repo) -> CheckResult:
        return CheckResult(passing=False, evidence="something missing")


def test_rule_class_attributes_required() -> None:
    rule = _PassingRule()
    assert rule.id == "TST001"
    assert rule.title == "Test passing rule"
    assert rule.severity == "required"
    assert rule.stacks == ("*",)
    assert rule.handbook_ref == "docs/handbook/99-test.md#tst001"
    assert rule.adr_ref is None
    assert rule.template_ref is None


def test_rule_applies_wildcard(tmp_path: Path) -> None:
    rule = _PassingRule()
    repo = Repo(path=tmp_path, stack="python")
    assert rule.applies(repo) is True
    repo_node = Repo(path=tmp_path, stack="node")
    assert rule.applies(repo_node) is True


def test_rule_applies_specific_stack(tmp_path: Path) -> None:
    rule = _FailingRule()
    repo_python = Repo(path=tmp_path, stack="python")
    assert rule.applies(repo_python) is True
    repo_node = Repo(path=tmp_path, stack="node")
    assert rule.applies(repo_node) is False


def test_check_result_passing() -> None:
    result = CheckResult(passing=True)
    assert result.passing is True
    assert result.evidence == ""


def test_check_result_failing_with_evidence() -> None:
    result = CheckResult(passing=False, evidence="missing file: uv.lock")
    assert result.passing is False
    assert result.evidence == "missing file: uv.lock"


def test_rule_default_fix_returns_none(tmp_path: Path) -> None:
    rule = _FailingRule()
    repo = Repo(path=tmp_path, stack="python")
    result = rule.check(repo)
    assert rule.fix(repo, result) is None


def test_rule_check_is_abstract() -> None:
    class _Incomplete(Rule):
        id = "TST999"
        title = "Incomplete"
        severity = "required"
        stacks = ("*",)
        handbook_ref = "x"

    with pytest.raises(TypeError):
        _Incomplete()  # type: ignore[abstract]
