"""Tests for CI transverse rules."""

from pathlib import Path

import intendant.checks.ci as ci_module
from intendant.checks.ci import (
    CI001CIWorkflow,
    CI003CommitMessageValidation,
    CI004CacheConfigured,
    CI005ActionsPinnedToSHA,
)
from intendant.core.repo import Repo


def test_ci_module_no_longer_exports_ci002() -> None:
    """CI002MinimumSteps must have been removed from the ci module."""
    assert not hasattr(ci_module, "CI002MinimumSteps"), (
        "CI002MinimumSteps is still present in intendant.checks.ci — "
        "it should have been deleted in Palier M0"
    )


def test_ci001_pass(tmp_path: Path) -> None:
    workflows = tmp_path / ".github" / "workflows"
    workflows.mkdir(parents=True)
    (workflows / "ci.yml").write_text(
        "name: CI\non: [push]\njobs:\n  test:\n    runs-on: ubuntu-latest\n    steps: []\n"
    )
    repo = Repo(path=tmp_path, stacks=("python",))
    assert CI001CIWorkflow().check(repo).passing is True


def test_ci001_fail_no_workflows_dir(tmp_path: Path) -> None:
    repo = Repo(path=tmp_path, stacks=("python",))
    result = CI001CIWorkflow().check(repo)
    assert result.passing is False


def test_ci001_fail_empty_workflows_dir(tmp_path: Path) -> None:
    (tmp_path / ".github" / "workflows").mkdir(parents=True)
    repo = Repo(path=tmp_path, stacks=("python",))
    result = CI001CIWorkflow().check(repo)
    assert result.passing is False
    assert "no workflow" in result.evidence.lower()


def test_ci001_pass_alternative_filename(tmp_path: Path) -> None:
    """Any *.yml or *.yaml in .github/workflows/ counts."""
    wf = tmp_path / ".github" / "workflows"
    wf.mkdir(parents=True)
    (wf / "test.yaml").write_text("name: test\non: [push]\njobs: {}\n")
    repo = Repo(path=tmp_path, stacks=("python",))
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
    repo = Repo(path=tmp_path, stacks=("python",))
    assert CI004CacheConfigured().check(repo).passing is True


def test_ci004_pass_actions_cache(tmp_path: Path) -> None:
    wf = _make_workflows_dir(tmp_path)
    (wf / "ci.yml").write_text(_WORKFLOW_WITH_ACTIONS_CACHE)
    repo = Repo(path=tmp_path, stacks=("python",))
    assert CI004CacheConfigured().check(repo).passing is True


_WORKFLOW_WITH_RUST_CACHE = """\
name: CI
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: Swatinem/rust-cache@v2
      - run: cargo test
"""

_WORKFLOW_WITH_SCCACHE = """\
name: CI
on: [push]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: mozilla-actions/sccache-action@v0.0.5
      - run: cargo build
"""

_WORKFLOW_WITH_SETUP_GO = """\
name: CI
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/setup-go@v5
        with:
          go-version: '1.22'
      - run: go test ./...
"""


def test_ci004_pass_swatinem_rust_cache(tmp_path: Path) -> None:
    wf = _make_workflows_dir(tmp_path)
    (wf / "ci.yml").write_text(_WORKFLOW_WITH_RUST_CACHE)
    repo = Repo(path=tmp_path, stacks=("rust",))
    assert CI004CacheConfigured().check(repo).passing is True


def test_ci004_pass_sccache_action(tmp_path: Path) -> None:
    wf = _make_workflows_dir(tmp_path)
    (wf / "ci.yml").write_text(_WORKFLOW_WITH_SCCACHE)
    repo = Repo(path=tmp_path, stacks=("rust",))
    assert CI004CacheConfigured().check(repo).passing is True


def test_ci004_pass_setup_go(tmp_path: Path) -> None:
    wf = _make_workflows_dir(tmp_path)
    (wf / "ci.yml").write_text(_WORKFLOW_WITH_SETUP_GO)
    repo = Repo(path=tmp_path, stacks=("go",))
    assert CI004CacheConfigured().check(repo).passing is True


_WORKFLOW_SETUP_PYTHON_NO_CACHE = """\
name: CI
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/setup-python@v5
        with:
          python-version: '3.13'
"""

_WORKFLOW_SETUP_PYTHON_WITH_CACHE = """\
name: CI
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/setup-python@v5
        with:
          python-version: '3.13'
          cache: pip
"""

_WORKFLOW_SETUP_JAVA_NO_CACHE = """\
name: CI
on: [push]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/setup-java@v4
        with:
          distribution: temurin
          java-version: '21'
"""

_WORKFLOW_CACHE_INPUT_DISABLED = """\
name: CI
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: false
"""

_WORKFLOW_CACHE_INPUT_ON_UNLISTED_ACTION = """\
name: CI
on: [push]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: erlef/setup-beam@v1
        with:
          otp-version: '27'
          cache: rebar
"""


def test_ci004_fail_setup_python_without_cache_input(tmp_path: Path) -> None:
    """Bare setup-python configures no cache (cache: input absent) → fail."""
    wf = _make_workflows_dir(tmp_path)
    (wf / "ci.yml").write_text(_WORKFLOW_SETUP_PYTHON_NO_CACHE)
    repo = Repo(path=tmp_path, stacks=("python",))
    assert CI004CacheConfigured().check(repo).passing is False


def test_ci004_fail_setup_java_without_cache_input(tmp_path: Path) -> None:
    """setup-java does not cache by default; bare presence must not pass."""
    wf = _make_workflows_dir(tmp_path)
    (wf / "ci.yml").write_text(_WORKFLOW_SETUP_JAVA_NO_CACHE)
    repo = Repo(path=tmp_path, stacks=("java",))
    assert CI004CacheConfigured().check(repo).passing is False


def test_ci004_fail_cache_input_disabled(tmp_path: Path) -> None:
    """`cache: false` explicitly disables caching → must not count."""
    wf = _make_workflows_dir(tmp_path)
    (wf / "ci.yml").write_text(_WORKFLOW_CACHE_INPUT_DISABLED)
    repo = Repo(path=tmp_path, stacks=("node",))
    assert CI004CacheConfigured().check(repo).passing is False


def test_ci004_pass_setup_python_with_cache_input(tmp_path: Path) -> None:
    """setup-python WITH `cache: pip` does configure a cache → pass."""
    wf = _make_workflows_dir(tmp_path)
    (wf / "ci.yml").write_text(_WORKFLOW_SETUP_PYTHON_WITH_CACHE)
    repo = Repo(path=tmp_path, stacks=("python",))
    assert CI004CacheConfigured().check(repo).passing is True


def test_ci004_pass_cache_input_on_any_setup_action(tmp_path: Path) -> None:
    """A non-default `cache:` input counts regardless of which action sets it."""
    wf = _make_workflows_dir(tmp_path)
    (wf / "ci.yml").write_text(_WORKFLOW_CACHE_INPUT_ON_UNLISTED_ACTION)
    repo = Repo(path=tmp_path, stacks=("*",))
    assert CI004CacheConfigured().check(repo).passing is True


def test_ci004_fail_no_cache(tmp_path: Path) -> None:
    wf = _make_workflows_dir(tmp_path)
    (wf / "ci.yml").write_text(_WORKFLOW_NO_CACHE)
    repo = Repo(path=tmp_path, stacks=("python",))
    result = CI004CacheConfigured().check(repo)
    assert result.passing is False
    assert "cache" in result.evidence.lower()


def test_ci004_skip_no_workflows_dir(tmp_path: Path) -> None:
    """No workflows directory → skip (pass with evidence)."""
    repo = Repo(path=tmp_path, stacks=("python",))
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
    repo = Repo(path=tmp_path, stacks=("python",))
    result = CI003CommitMessageValidation().check(repo)
    assert result.passing is True
    assert result.skipped is True


def test_ci003_passes_with_cz_check(tmp_path: Path) -> None:
    wf = _make_workflows_dir(tmp_path)
    (wf / "ci.yml").write_text(_WORKFLOW_WITH_CZ_CHECK)
    repo = Repo(path=tmp_path, stacks=("python",))
    assert CI003CommitMessageValidation().check(repo).passing is True


def test_ci003_passes_with_commitizen_action(tmp_path: Path) -> None:
    wf = _make_workflows_dir(tmp_path)
    (wf / "ci.yml").write_text(_WORKFLOW_WITH_COMMITIZEN_ACTION)
    repo = Repo(path=tmp_path, stacks=("python",))
    assert CI003CommitMessageValidation().check(repo).passing is True


def test_ci003_passes_with_commitlint(tmp_path: Path) -> None:
    wf = _make_workflows_dir(tmp_path)
    (wf / "ci.yml").write_text(_WORKFLOW_WITH_COMMITLINT)
    repo = Repo(path=tmp_path, stacks=("python",))
    assert CI003CommitMessageValidation().check(repo).passing is True


def test_ci003_fails_when_no_commit_validation(tmp_path: Path) -> None:
    wf = _make_workflows_dir(tmp_path)
    (wf / "ci.yml").write_text(_WORKFLOW_WITHOUT_COMMIT_VALIDATION)
    repo = Repo(path=tmp_path, stacks=("python",))
    result = CI003CommitMessageValidation().check(repo)
    assert result.passing is False
    assert "commit" in result.evidence.lower()


# --- CI005: actions pinned to commit SHAs ---


def _write_wf(tmp_path: Path, body: str) -> None:
    wf = tmp_path / ".github" / "workflows"
    wf.mkdir(parents=True, exist_ok=True)
    (wf / "ci.yml").write_text(body)


def test_ci005_pass_all_sha_pinned(tmp_path: Path) -> None:
    _write_wf(
        tmp_path,
        "jobs:\n  a:\n    steps:\n"
        "      - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683  # v4.2.2\n"
        "      - uses: astral-sh/setup-uv@11f9893b081a58869d3b5fccaea48c9e9e46f990  # v8.3.2\n",
    )
    repo = Repo(path=tmp_path, stacks=("python",))
    result = CI005ActionsPinnedToSHA().check(repo)
    assert result.passing is True


def test_ci005_fail_tag_pinned(tmp_path: Path) -> None:
    _write_wf(
        tmp_path,
        "jobs:\n  a:\n    steps:\n"
        "      - uses: actions/checkout@v4\n"
        "      - uses: astral-sh/setup-uv@11f9893b081a58869d3b5fccaea48c9e9e46f990\n",
    )
    repo = Repo(path=tmp_path, stacks=("python",))
    result = CI005ActionsPinnedToSHA().check(repo)
    assert result.passing is False
    assert "actions/checkout@v4" in result.evidence


def test_ci005_fail_unpinned(tmp_path: Path) -> None:
    _write_wf(tmp_path, "jobs:\n  a:\n    steps:\n      - uses: actions/checkout\n")
    repo = Repo(path=tmp_path, stacks=("python",))
    assert CI005ActionsPinnedToSHA().check(repo).passing is False


def test_ci005_ignores_local_and_docker_uses(tmp_path: Path) -> None:
    _write_wf(
        tmp_path,
        "jobs:\n  a:\n    steps:\n"
        "      - uses: ./.github/actions/local-thing\n"
        "      - uses: docker://alpine:3.20\n",
    )
    repo = Repo(path=tmp_path, stacks=("python",))
    assert CI005ActionsPinnedToSHA().check(repo).passing is True


def test_ci005_skipped_when_no_workflows_dir(tmp_path: Path) -> None:
    repo = Repo(path=tmp_path, stacks=("python",))
    assert CI005ActionsPinnedToSHA().check(repo).skipped is True


def test_ci005_metadata() -> None:
    rule = CI005ActionsPinnedToSHA()
    assert rule.id == "CI005"
    assert rule.severity == "required"
    assert rule.stacks == ("*",)
