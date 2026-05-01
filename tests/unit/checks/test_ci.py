"""Tests for CI transverse rules."""

from pathlib import Path

from suzerain.checks.ci import CI001CIWorkflow, CI004CacheConfigured
from suzerain.core.repo import Repo


def test_ci001_pass(tmp_path: Path) -> None:
    workflows = tmp_path / ".github" / "workflows"
    workflows.mkdir(parents=True)
    (workflows / "ci.yml").write_text(
        "name: CI\non: [push]\njobs:\n  test:\n    runs-on: ubuntu-latest\n    steps: []\n"
    )
    repo = Repo(path=tmp_path, stack="python")
    assert CI001CIWorkflow().check(repo).passing is True


def test_ci001_fail_no_workflows_dir(tmp_path: Path) -> None:
    repo = Repo(path=tmp_path, stack="python")
    result = CI001CIWorkflow().check(repo)
    assert result.passing is False


def test_ci001_fail_empty_workflows_dir(tmp_path: Path) -> None:
    (tmp_path / ".github" / "workflows").mkdir(parents=True)
    repo = Repo(path=tmp_path, stack="python")
    result = CI001CIWorkflow().check(repo)
    assert result.passing is False
    assert "no workflow" in result.evidence.lower()


def test_ci001_pass_alternative_filename(tmp_path: Path) -> None:
    """Any *.yml or *.yaml in .github/workflows/ counts."""
    wf = tmp_path / ".github" / "workflows"
    wf.mkdir(parents=True)
    (wf / "test.yaml").write_text("name: test\non: [push]\njobs: {}\n")
    repo = Repo(path=tmp_path, stack="python")
    assert CI001CIWorkflow().check(repo).passing is True


# ---------------------------------------------------------------------------
# CI004CacheConfigured
# ---------------------------------------------------------------------------

_WORKFLOW_WITH_ENABLE_CACHE = """\
name: CI
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: astral-sh/setup-uv@v4
        with:
          enable-cache: true
"""

_WORKFLOW_WITH_ACTIONS_CACHE = """\
name: CI
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/cache@v4
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip
"""

_WORKFLOW_NO_CACHE = """\
name: CI
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: echo hello
"""


def _make_workflows_dir(tmp_path: Path) -> Path:
    wf = tmp_path / ".github" / "workflows"
    wf.mkdir(parents=True)
    return wf


def test_ci004_pass_enable_cache(tmp_path: Path) -> None:
    wf = _make_workflows_dir(tmp_path)
    (wf / "ci.yml").write_text(_WORKFLOW_WITH_ENABLE_CACHE)
    repo = Repo(path=tmp_path, stack="python")
    assert CI004CacheConfigured().check(repo).passing is True


def test_ci004_pass_actions_cache(tmp_path: Path) -> None:
    wf = _make_workflows_dir(tmp_path)
    (wf / "ci.yml").write_text(_WORKFLOW_WITH_ACTIONS_CACHE)
    repo = Repo(path=tmp_path, stack="python")
    assert CI004CacheConfigured().check(repo).passing is True


def test_ci004_fail_no_cache(tmp_path: Path) -> None:
    wf = _make_workflows_dir(tmp_path)
    (wf / "ci.yml").write_text(_WORKFLOW_NO_CACHE)
    repo = Repo(path=tmp_path, stack="python")
    result = CI004CacheConfigured().check(repo)
    assert result.passing is False
    assert "cache" in result.evidence.lower()


def test_ci004_skip_no_workflows_dir(tmp_path: Path) -> None:
    """No workflows directory → skip (pass with evidence)."""
    repo = Repo(path=tmp_path, stack="python")
    result = CI004CacheConfigured().check(repo)
    # Should pass cleanly (skip) when no workflows dir exists
    assert result.passing is True
    assert "no" in result.evidence.lower() or "skip" in result.evidence.lower()


def test_ci004_metadata() -> None:
    rule = CI004CacheConfigured()
    assert rule.id == "CI004"
    assert rule.severity == "recommended"
    assert "*" in rule.stacks
