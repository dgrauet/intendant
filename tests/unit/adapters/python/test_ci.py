"""Tests for Python adapter CI rules."""

from pathlib import Path

from suzerain.adapters.python.ci import PYTHON_CI001MinimumSteps
from suzerain.core.repo import Repo


def _make_workflows_dir(tmp_path: Path) -> Path:
    wf = tmp_path / ".github" / "workflows"
    wf.mkdir(parents=True)
    return wf


_FULL_PYTHON_WORKFLOW = """\
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

_PYTHON_WORKFLOW_MISSING_LINT = """\
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

_PYTHON_WORKFLOW_MISSING_FORMAT = """\
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

_PYTHON_WORKFLOW_MISSING_TYPE = """\
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

_PYTHON_WORKFLOW_MISSING_TEST = """\
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


def test_python_ci001_skipped_when_no_workflows_dir(tmp_path: Path) -> None:
    repo = Repo(path=tmp_path, stacks=("python",))
    result = PYTHON_CI001MinimumSteps().check(repo)
    assert result.passing is True
    assert result.skipped is True
    assert "CI001" in result.evidence


def test_python_ci001_passes_when_all_steps_present(tmp_path: Path) -> None:
    wf = _make_workflows_dir(tmp_path)
    (wf / "ci.yml").write_text(_FULL_PYTHON_WORKFLOW)
    repo = Repo(path=tmp_path, stacks=("python",))
    result = PYTHON_CI001MinimumSteps().check(repo)
    assert result.passing is True
    assert "lint" in result.evidence.lower() or "Python" in result.evidence


def test_python_ci001_fails_when_lint_missing(tmp_path: Path) -> None:
    wf = _make_workflows_dir(tmp_path)
    (wf / "ci.yml").write_text(_PYTHON_WORKFLOW_MISSING_LINT)
    repo = Repo(path=tmp_path, stacks=("python",))
    result = PYTHON_CI001MinimumSteps().check(repo)
    assert result.passing is False
    assert "lint" in result.evidence


def test_python_ci001_fails_when_format_missing(tmp_path: Path) -> None:
    wf = _make_workflows_dir(tmp_path)
    (wf / "ci.yml").write_text(_PYTHON_WORKFLOW_MISSING_FORMAT)
    repo = Repo(path=tmp_path, stacks=("python",))
    result = PYTHON_CI001MinimumSteps().check(repo)
    assert result.passing is False
    assert "format" in result.evidence


def test_python_ci001_fails_when_type_missing(tmp_path: Path) -> None:
    wf = _make_workflows_dir(tmp_path)
    (wf / "ci.yml").write_text(_PYTHON_WORKFLOW_MISSING_TYPE)
    repo = Repo(path=tmp_path, stacks=("python",))
    result = PYTHON_CI001MinimumSteps().check(repo)
    assert result.passing is False
    assert "type" in result.evidence


def test_python_ci001_fails_when_test_missing(tmp_path: Path) -> None:
    wf = _make_workflows_dir(tmp_path)
    (wf / "ci.yml").write_text(_PYTHON_WORKFLOW_MISSING_TEST)
    repo = Repo(path=tmp_path, stacks=("python",))
    result = PYTHON_CI001MinimumSteps().check(repo)
    assert result.passing is False
    assert "test" in result.evidence


def test_python_ci001_passes_with_pyright_instead_of_ty(tmp_path: Path) -> None:
    wf = _make_workflows_dir(tmp_path)
    (wf / "ci.yml").write_text(
        "name: CI\non: [push]\njobs:\n  q:\n    runs-on: ubuntu-latest\n    steps:\n"
        "      - run: ruff check .\n      - run: ruff format .\n"
        "      - run: pyright\n      - run: pytest\n"
    )
    repo = Repo(path=tmp_path, stacks=("python",))
    result = PYTHON_CI001MinimumSteps().check(repo)
    assert result.passing is True


def test_python_ci001_passes_with_unittest(tmp_path: Path) -> None:
    wf = _make_workflows_dir(tmp_path)
    (wf / "ci.yml").write_text(
        "name: CI\non: [push]\njobs:\n  q:\n    runs-on: ubuntu-latest\n    steps:\n"
        "      - run: ruff check .\n      - run: ruff format .\n"
        "      - run: ty check\n      - run: python -m unittest\n"
    )
    repo = Repo(path=tmp_path, stacks=("python",))
    result = PYTHON_CI001MinimumSteps().check(repo)
    assert result.passing is True


def test_python_ci001_metadata() -> None:
    rule = PYTHON_CI001MinimumSteps()
    assert rule.id == "PYTHON_CI001"
    assert rule.severity == "required"
    assert "python" in rule.stacks
