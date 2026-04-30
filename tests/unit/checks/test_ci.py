"""Tests for CI transverse rules."""

from pathlib import Path

from suzerain.checks.ci import CI001CIWorkflow
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
