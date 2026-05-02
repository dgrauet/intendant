"""Tests for CI transverse rules."""

from pathlib import Path

from suzerain.checks.ci import (
    CI001CIWorkflow,
    CI002MinimumSteps,
    CI003CommitMessageValidation,
    CI004CacheConfigured,
)
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


# ---------------------------------------------------------------------------
# CI002MinimumSteps
# ---------------------------------------------------------------------------

_FULL_WORKFLOW = """\
name: CI
on: [push]
jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - run: uv run ruff check .
      - run: uv run ruff format --check .
      - run: uvx ty check
      - run: uv run pytest
"""

_WORKFLOW_MISSING_LINT = """\
name: CI
on: [push]
jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - run: uv run ruff format --check .
      - run: uvx ty check
      - run: uv run pytest
"""

_WORKFLOW_MISSING_FORMAT = """\
name: CI
on: [push]
jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - run: uv run ruff check .
      - run: uvx ty check
      - run: uv run pytest
"""

_WORKFLOW_MISSING_TYPE = """\
name: CI
on: [push]
jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - run: uv run ruff check .
      - run: uv run ruff format --check .
      - run: uv run pytest
"""

_WORKFLOW_MISSING_TEST = """\
name: CI
on: [push]
jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - run: uv run ruff check .
      - run: uv run ruff format --check .
      - run: uvx ty check
"""


def test_ci002_skipped_when_no_workflows_dir(tmp_path: Path) -> None:
    repo = Repo(path=tmp_path, stack="python")
    result = CI002MinimumSteps().check(repo)
    assert result.passing is True
    assert result.skipped is True


def test_ci002_passes_when_all_steps_present(tmp_path: Path) -> None:
    wf = _make_workflows_dir(tmp_path)
    (wf / "ci.yml").write_text(_FULL_WORKFLOW)
    repo = Repo(path=tmp_path, stack="python")
    assert CI002MinimumSteps().check(repo).passing is True


def test_ci002_fails_when_lint_missing(tmp_path: Path) -> None:
    wf = _make_workflows_dir(tmp_path)
    (wf / "ci.yml").write_text(_WORKFLOW_MISSING_LINT)
    repo = Repo(path=tmp_path, stack="python")
    result = CI002MinimumSteps().check(repo)
    assert result.passing is False
    assert "lint" in result.evidence


def test_ci002_fails_when_format_missing(tmp_path: Path) -> None:
    wf = _make_workflows_dir(tmp_path)
    (wf / "ci.yml").write_text(_WORKFLOW_MISSING_FORMAT)
    repo = Repo(path=tmp_path, stack="python")
    result = CI002MinimumSteps().check(repo)
    assert result.passing is False
    assert "format" in result.evidence


def test_ci002_fails_when_type_missing(tmp_path: Path) -> None:
    wf = _make_workflows_dir(tmp_path)
    (wf / "ci.yml").write_text(_WORKFLOW_MISSING_TYPE)
    repo = Repo(path=tmp_path, stack="python")
    result = CI002MinimumSteps().check(repo)
    assert result.passing is False
    assert "type" in result.evidence


def test_ci002_fails_when_test_missing(tmp_path: Path) -> None:
    wf = _make_workflows_dir(tmp_path)
    (wf / "ci.yml").write_text(_WORKFLOW_MISSING_TEST)
    repo = Repo(path=tmp_path, stack="python")
    result = CI002MinimumSteps().check(repo)
    assert result.passing is False
    assert "test" in result.evidence


# ---------------------------------------------------------------------------
# CI003CommitMessageValidation
# ---------------------------------------------------------------------------

_WORKFLOW_WITH_CZ_CHECK = """\
name: commit-lint
on: [pull_request]
jobs:
  commitlint:
    runs-on: ubuntu-latest
    steps:
      - run: uv tool run cz check --rev-range origin/${{ github.base_ref }}..HEAD
"""

_WORKFLOW_WITH_COMMITIZEN_ACTION = """\
name: commit-lint
on: [pull_request]
jobs:
  commitlint:
    runs-on: ubuntu-latest
    steps:
      - uses: commitizen-tools/commitizen-action@master
"""

_WORKFLOW_WITH_COMMITLINT = """\
name: commit-lint
on: [pull_request]
jobs:
  commitlint:
    runs-on: ubuntu-latest
    steps:
      - uses: wagoid/commitlint-github-action@v5
"""

_WORKFLOW_WITHOUT_COMMIT_VALIDATION = """\
name: CI
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - run: uv run pytest
"""


def test_ci003_skipped_when_no_workflows_dir(tmp_path: Path) -> None:
    repo = Repo(path=tmp_path, stack="python")
    result = CI003CommitMessageValidation().check(repo)
    assert result.passing is True
    assert result.skipped is True


def test_ci003_passes_with_cz_check(tmp_path: Path) -> None:
    wf = _make_workflows_dir(tmp_path)
    (wf / "ci.yml").write_text(_WORKFLOW_WITH_CZ_CHECK)
    repo = Repo(path=tmp_path, stack="python")
    assert CI003CommitMessageValidation().check(repo).passing is True


def test_ci003_passes_with_commitizen_action(tmp_path: Path) -> None:
    wf = _make_workflows_dir(tmp_path)
    (wf / "ci.yml").write_text(_WORKFLOW_WITH_COMMITIZEN_ACTION)
    repo = Repo(path=tmp_path, stack="python")
    assert CI003CommitMessageValidation().check(repo).passing is True


def test_ci003_passes_with_commitlint(tmp_path: Path) -> None:
    wf = _make_workflows_dir(tmp_path)
    (wf / "ci.yml").write_text(_WORKFLOW_WITH_COMMITLINT)
    repo = Repo(path=tmp_path, stack="python")
    assert CI003CommitMessageValidation().check(repo).passing is True


def test_ci003_fails_when_no_commit_validation(tmp_path: Path) -> None:
    wf = _make_workflows_dir(tmp_path)
    (wf / "ci.yml").write_text(_WORKFLOW_WITHOUT_COMMIT_VALIDATION)
    repo = Repo(path=tmp_path, stack="python")
    result = CI003CommitMessageValidation().check(repo)
    assert result.passing is False
    assert "commit" in result.evidence.lower()
