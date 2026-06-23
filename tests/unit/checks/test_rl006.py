"""Tests for RL006 (release-please wired through a GitHub App token)."""

from __future__ import annotations

from pathlib import Path

from intendant.checks.rl006 import RL006ReleasePleaseGitHubApp
from intendant.core.repo import Repo


def _repo(path: Path) -> Repo:
    return Repo(path=path, stacks=("auto",))


def _write_workflow(path: Path, name: str, content: str) -> None:
    wf_dir = path / ".github" / "workflows"
    wf_dir.mkdir(parents=True, exist_ok=True)
    (wf_dir / name).write_text(content)


_COMPLETE = """\
name: release-please
on:
  push:
    branches: [main]
jobs:
  release-please:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/create-github-app-token@v3
        id: app-token
        with:
          app-id: ${{ secrets.RELEASE_APP_ID }}
          private-key: ${{ secrets.RELEASE_APP_PRIVATE_KEY }}
      - uses: googleapis/release-please-action@v5
        id: release
        with:
          token: ${{ steps.app-token.outputs.token }}
          config-file: release-please-config.json
          manifest-file: .release-please-manifest.json
"""

_DEFAULT_TOKEN = """\
name: release-please
on: {push: {branches: [main]}}
jobs:
  release-please:
    runs-on: ubuntu-latest
    steps:
      - uses: googleapis/release-please-action@v5
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
          config-file: release-please-config.json
          manifest-file: .release-please-manifest.json
"""

_NO_APP_TOKEN = """\
name: release-please
on: {push: {branches: [main]}}
jobs:
  release-please:
    runs-on: ubuntu-latest
    steps:
      - uses: googleapis/release-please-action@v5
        with:
          config-file: release-please-config.json
          manifest-file: .release-please-manifest.json
"""

_MISSING_INPUTS = """\
name: release-please
on: {push: {branches: [main]}}
jobs:
  release-please:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/create-github-app-token@v3
        id: app-token
      - uses: googleapis/release-please-action@v5
        with:
          token: ${{ steps.app-token.outputs.token }}
"""

_UNRELATED = """\
name: ci
on: {push: {}}
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
"""


def test_rl006_metadata() -> None:
    rule = RL006ReleasePleaseGitHubApp()
    assert rule.id == "RL006"
    assert rule.severity == "recommended"
    assert "*" in rule.stacks


def test_rl006_skipped_when_no_workflows_dir(tmp_path: Path) -> None:
    result = RL006ReleasePleaseGitHubApp().check(_repo(tmp_path))
    assert result.skipped is True


def test_rl006_skipped_when_no_release_please(tmp_path: Path) -> None:
    _write_workflow(tmp_path, "ci.yml", _UNRELATED)
    result = RL006ReleasePleaseGitHubApp().check(_repo(tmp_path))
    assert result.skipped is True


def test_rl006_pass_complete(tmp_path: Path) -> None:
    _write_workflow(tmp_path, "release-please.yml", _COMPLETE)
    result = RL006ReleasePleaseGitHubApp().check(_repo(tmp_path))
    assert result.passing is True


def test_rl006_pass_ignores_unrelated_sibling_workflow(tmp_path: Path) -> None:
    _write_workflow(tmp_path, "ci.yml", _UNRELATED)
    _write_workflow(tmp_path, "release-please.yml", _COMPLETE)
    result = RL006ReleasePleaseGitHubApp().check(_repo(tmp_path))
    assert result.passing is True


def test_rl006_fail_default_github_token(tmp_path: Path) -> None:
    _write_workflow(tmp_path, "release-please.yml", _DEFAULT_TOKEN)
    result = RL006ReleasePleaseGitHubApp().check(_repo(tmp_path))
    assert result.passing is False
    assert "github_token" in result.evidence.lower() or "app" in result.evidence.lower()


def test_rl006_fail_no_app_token_step(tmp_path: Path) -> None:
    _write_workflow(tmp_path, "release-please.yml", _NO_APP_TOKEN)
    result = RL006ReleasePleaseGitHubApp().check(_repo(tmp_path))
    assert result.passing is False
    assert "app" in result.evidence.lower()


def test_rl006_fail_missing_config_or_manifest_input(tmp_path: Path) -> None:
    _write_workflow(tmp_path, "release-please.yml", _MISSING_INPUTS)
    result = RL006ReleasePleaseGitHubApp().check(_repo(tmp_path))
    assert result.passing is False
    assert "config-file" in result.evidence or "manifest-file" in result.evidence
