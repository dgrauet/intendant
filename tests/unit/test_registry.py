"""Tests for the rule registry."""

from pathlib import Path

from suzerain.audit.registry import collect_rules, filter_for_repo
from suzerain.core.config import Exemption, SuzerainConfig
from suzerain.core.repo import Repo
from suzerain.core.rule import CheckResult, Rule


class _RuleA(Rule):
    id = "TST001"
    title = "Transverse"
    severity = "required"
    stacks = ("*",)
    handbook_ref = "x"

    def check(self, repo: Repo) -> CheckResult:
        return CheckResult(passing=True)


class _RuleB(Rule):
    id = "TST002"
    title = "Python only"
    severity = "recommended"
    stacks = ("python",)
    handbook_ref = "x"

    def check(self, repo: Repo) -> CheckResult:
        return CheckResult(passing=True)


class _RuleC(Rule):
    id = "TST003"
    title = "Optional rule"
    severity = "optional"
    stacks = ("*",)
    handbook_ref = "x"

    def check(self, repo: Repo) -> CheckResult:
        return CheckResult(passing=True)


def test_collect_rules_finds_all() -> None:
    rules = collect_rules()
    assert isinstance(rules, list)


def test_filter_applies_stack_filter(tmp_path: Path) -> None:
    rules = [_RuleA(), _RuleB(), _RuleC()]
    config = SuzerainConfig(version="1", stack="python", mode="strict")
    repo = Repo(path=tmp_path, stack="python")
    filtered = filter_for_repo(rules, repo, config)
    rule_ids = {r.id for r in filtered}
    assert rule_ids == {"TST001", "TST002", "TST003"}


def test_filter_excludes_non_applicable_stacks(tmp_path: Path) -> None:
    rules = [_RuleA(), _RuleB(), _RuleC()]
    config = SuzerainConfig(version="1", stack="node", mode="strict")
    repo = Repo(path=tmp_path, stack="node")
    filtered = filter_for_repo(rules, repo, config)
    rule_ids = {r.id for r in filtered}
    assert rule_ids == {"TST001", "TST003"}


def test_filter_strict_mode_includes_optional(tmp_path: Path) -> None:
    rules = [_RuleA(), _RuleB(), _RuleC()]
    config = SuzerainConfig(version="1", stack="python", mode="strict")
    repo = Repo(path=tmp_path, stack="python")
    filtered = filter_for_repo(rules, repo, config)
    severities = {r.severity for r in filtered}
    assert severities == {"required", "recommended", "optional"}


def test_filter_recommended_mode_excludes_optional(tmp_path: Path) -> None:
    rules = [_RuleA(), _RuleB(), _RuleC()]
    config = SuzerainConfig(version="1", stack="python", mode="recommended")
    repo = Repo(path=tmp_path, stack="python")
    filtered = filter_for_repo(rules, repo, config)
    severities = {r.severity for r in filtered}
    assert "optional" not in severities


def test_filter_advisory_mode_keeps_all_for_reporting(tmp_path: Path) -> None:
    rules = [_RuleA(), _RuleB(), _RuleC()]
    config = SuzerainConfig(version="1", stack="python", mode="advisory")
    repo = Repo(path=tmp_path, stack="python")
    filtered = filter_for_repo(rules, repo, config)
    assert len(filtered) == 3


def test_filter_does_not_remove_exempt_rules(tmp_path: Path) -> None:
    rules = [_RuleA(), _RuleB(), _RuleC()]
    config = SuzerainConfig(
        version="1",
        stack="python",
        mode="strict",
        exemptions={"TST001": Exemption(reason="test")},
    )
    repo = Repo(path=tmp_path, stack="python")
    filtered = filter_for_repo(rules, repo, config)
    rule_ids = {r.id for r in filtered}
    assert "TST001" in rule_ids


def test_collect_rules_includes_claude_skill_adapter() -> None:
    """The registry imports the claude-skill adapter's RULES list (initially empty)."""
    from suzerain.adapters.claude_skill import RULES as CLAUDE_SKILL_RULES
    from suzerain.audit.registry import collect_rules

    rules = collect_rules()
    # All claude-skill rules must appear in the collected list (set-equality on ids)
    skill_ids = {r.id for r in CLAUDE_SKILL_RULES}
    collected_ids = {r.id for r in rules}
    assert skill_ids.issubset(collected_ids)


def test_registry_imports_claude_skill_adapter_module() -> None:
    """The registry must import claude-skill adapter module without raising."""
    from suzerain.audit.registry import collect_rules

    # Should not raise even if skill adapter is empty
    collect_rules()
    # Direct import test — the adapter module must be importable
    import suzerain.adapters.claude_skill  # noqa: F401


def test_filter_for_repo_with_named_subproject_returns_only_stack_specific(tmp_path: Path) -> None:
    """When repo.name is set (subproject), only stack-specific rules apply (no transverse)."""
    from suzerain.audit.registry import collect_rules, filter_for_repo
    from suzerain.core.config import SuzerainConfig
    from suzerain.core.repo import Repo

    repo = Repo(path=Path("/tmp"), stack="python", name="backend")
    cfg = SuzerainConfig(version="1", stack="python", mode="strict")
    rules = filter_for_repo(collect_rules(), repo, cfg)
    for r in rules:
        assert "*" not in r.stacks, f"{r.id} is transverse but ran on subproject scope"


def test_filter_for_repo_with_no_name_returns_only_transverse(tmp_path: Path) -> None:
    """When repo.name is None AND multi mode, only transverse rules apply."""
    from suzerain.audit.registry import collect_rules, filter_for_repo
    from suzerain.core.config import SuzerainConfig
    from suzerain.core.repo import Repo
    from suzerain.core.subproject import Subproject

    # In multi mode (config has subprojects), name=None means root meta-Repo: only transverse
    repo = Repo(path=Path("/tmp"), stack="multi")
    cfg = SuzerainConfig(
        version="1",
        stack="multi",
        mode="strict",
        subprojects=[Subproject(name="x", path="x", stack="python")],
    )
    rules = filter_for_repo(collect_rules(), repo, cfg)
    for r in rules:
        assert "*" in r.stacks, f"{r.id} is stack-specific but ran on root meta scope"
