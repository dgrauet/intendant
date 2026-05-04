"""Tests for Node adapter CI rules."""

from pathlib import Path

from suzerain.adapters.node.ci import NODE_CI001MinimumSteps
from suzerain.core.repo import Repo


def _make_workflows_dir(tmp_path: Path) -> Path:
    wf = tmp_path / ".github" / "workflows"
    wf.mkdir(parents=True)
    return wf


_FULL_NODE_WORKFLOW = """\
name: CI
on: [push]
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/setup-node@v4
      - run: npm ci
      - run: npm run lint
  typecheck:
    runs-on: ubuntu-latest
    steps:
      - run: npm run typecheck
  test:
    runs-on: ubuntu-latest
    steps:
      - run: npm test
"""

_NODE_WORKFLOW_MISSING_LINT = """\
name: CI
on: [push]
jobs:
  typecheck:
    runs-on: ubuntu-latest
    steps:
      - run: npm run typecheck
  test:
    runs-on: ubuntu-latest
    steps:
      - run: npm test
"""

_NODE_WORKFLOW_MISSING_TYPE = """\
name: CI
on: [push]
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - run: npm run lint
  test:
    runs-on: ubuntu-latest
    steps:
      - run: npm test
"""

_NODE_WORKFLOW_MISSING_TEST = """\
name: CI
on: [push]
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - run: npm run lint
  typecheck:
    runs-on: ubuntu-latest
    steps:
      - run: npm run typecheck
"""


def test_node_ci001_skipped_when_no_workflows_dir(tmp_path: Path) -> None:
    repo = Repo(path=tmp_path, stack="node")
    result = NODE_CI001MinimumSteps().check(repo)
    assert result.passing is True
    assert result.skipped is True
    assert "CI001" in result.evidence


def test_node_ci001_passes_when_all_steps_present(tmp_path: Path) -> None:
    wf = _make_workflows_dir(tmp_path)
    (wf / "ci.yml").write_text(_FULL_NODE_WORKFLOW)
    repo = Repo(path=tmp_path, stack="node")
    result = NODE_CI001MinimumSteps().check(repo)
    assert result.passing is True


def test_node_ci001_fails_when_lint_missing(tmp_path: Path) -> None:
    wf = _make_workflows_dir(tmp_path)
    (wf / "ci.yml").write_text(_NODE_WORKFLOW_MISSING_LINT)
    repo = Repo(path=tmp_path, stack="node")
    result = NODE_CI001MinimumSteps().check(repo)
    assert result.passing is False
    assert "lint" in result.evidence


def test_node_ci001_fails_when_type_missing(tmp_path: Path) -> None:
    wf = _make_workflows_dir(tmp_path)
    (wf / "ci.yml").write_text(_NODE_WORKFLOW_MISSING_TYPE)
    repo = Repo(path=tmp_path, stack="node")
    result = NODE_CI001MinimumSteps().check(repo)
    assert result.passing is False
    assert "type" in result.evidence


def test_node_ci001_fails_when_test_missing(tmp_path: Path) -> None:
    wf = _make_workflows_dir(tmp_path)
    (wf / "ci.yml").write_text(_NODE_WORKFLOW_MISSING_TEST)
    repo = Repo(path=tmp_path, stack="node")
    result = NODE_CI001MinimumSteps().check(repo)
    assert result.passing is False
    assert "test" in result.evidence


def test_node_ci001_passes_with_eslint(tmp_path: Path) -> None:
    wf = _make_workflows_dir(tmp_path)
    (wf / "ci.yml").write_text(
        "name: CI\non: [push]\njobs:\n  q:\n    runs-on: ubuntu-latest\n    steps:\n"
        "      - run: eslint .\n      - run: tsc --noEmit\n      - run: vitest\n"
    )
    repo = Repo(path=tmp_path, stack="node")
    result = NODE_CI001MinimumSteps().check(repo)
    assert result.passing is True


def test_node_ci001_passes_with_biome(tmp_path: Path) -> None:
    wf = _make_workflows_dir(tmp_path)
    (wf / "ci.yml").write_text(
        "name: CI\non: [push]\njobs:\n  q:\n    runs-on: ubuntu-latest\n    steps:\n"
        "      - run: biome check .\n      - run: tsc --noEmit\n      - run: jest\n"
    )
    repo = Repo(path=tmp_path, stack="node")
    result = NODE_CI001MinimumSteps().check(repo)
    assert result.passing is True


def test_node_ci001_metadata() -> None:
    rule = NODE_CI001MinimumSteps()
    assert rule.id == "NODE_CI001"
    assert rule.severity == "required"
    assert "node" in rule.stacks
