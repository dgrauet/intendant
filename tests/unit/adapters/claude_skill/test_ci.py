"""Tests for Claude Skill adapter CI rules."""

from pathlib import Path

from intendant.adapters.claude_skill.ci import CLAUDE_SKILL_CI001MinimumSteps
from intendant.core.repo import Repo


def _make_workflows_dir(tmp_path: Path) -> Path:
    wf = tmp_path / ".github" / "workflows"
    wf.mkdir(parents=True)
    return wf


_CLAUDE_SKILL_WORKFLOW_FULL = """\
name: CI
on: [push]
jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: uvx intendant audit . --severity=required
"""

_CLAUDE_SKILL_WORKFLOW_NO_AUDIT = """\
name: CI
on: [push]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: echo "hello"
"""


def test_claude_skill_ci001_skipped_when_no_workflows_dir(tmp_path: Path) -> None:
    repo = Repo(path=tmp_path, stacks=("claude-skill",))
    result = CLAUDE_SKILL_CI001MinimumSteps().check(repo)
    assert result.passing is True
    assert result.skipped is True
    assert "CI001" in result.evidence


def test_claude_skill_ci001_passes_when_intendant_audit_present(tmp_path: Path) -> None:
    wf = _make_workflows_dir(tmp_path)
    (wf / "ci.yml").write_text(_CLAUDE_SKILL_WORKFLOW_FULL)
    repo = Repo(path=tmp_path, stacks=("claude-skill",))
    result = CLAUDE_SKILL_CI001MinimumSteps().check(repo)
    assert result.passing is True
    assert "intendant audit" in result.evidence


def test_claude_skill_ci001_fails_when_intendant_audit_missing(tmp_path: Path) -> None:
    wf = _make_workflows_dir(tmp_path)
    (wf / "ci.yml").write_text(_CLAUDE_SKILL_WORKFLOW_NO_AUDIT)
    repo = Repo(path=tmp_path, stacks=("claude-skill",))
    result = CLAUDE_SKILL_CI001MinimumSteps().check(repo)
    assert result.passing is False
    assert "intendant audit" in result.evidence


def test_claude_skill_ci001_metadata() -> None:
    rule = CLAUDE_SKILL_CI001MinimumSteps()
    assert rule.id == "CLAUDE_SKILL_CI001"
    assert rule.severity == "required"
    assert "claude-skill" in rule.stacks
