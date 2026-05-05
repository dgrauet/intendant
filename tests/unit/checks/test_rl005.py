"""Tests for RL005 (GitHub branch protection on main)."""

from __future__ import annotations

import subprocess
from pathlib import Path
from unittest.mock import patch

from intendant.checks.rl005 import RL005BranchProtection
from intendant.core.repo import Repo


def _repo(path: Path) -> Repo:
    return Repo(path=path, stacks=("auto",))


def _git_init(path: Path, remote_url: str | None = None) -> None:
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=path, check=True)
    if remote_url is not None:
        subprocess.run(["git", "remote", "add", "origin", remote_url], cwd=path, check=True)


def test_rl005_metadata() -> None:
    rule = RL005BranchProtection()
    assert rule.id == "RL005"
    assert rule.severity == "recommended"
    assert "*" in rule.stacks


def test_rl005_skipped_when_no_git(tmp_path: Path) -> None:
    result = RL005BranchProtection().check(_repo(tmp_path))
    assert result.skipped is True
    assert "git" in result.evidence.lower()


def test_rl005_skipped_when_no_origin_remote(tmp_path: Path) -> None:
    _git_init(tmp_path, remote_url=None)
    result = RL005BranchProtection().check(_repo(tmp_path))
    assert result.skipped is True
    assert "origin" in result.evidence.lower() or "remote" in result.evidence.lower()


def test_rl005_skipped_when_remote_is_not_github(tmp_path: Path) -> None:
    _git_init(tmp_path, remote_url="https://gitlab.com/foo/bar.git")
    result = RL005BranchProtection().check(_repo(tmp_path))
    assert result.skipped is True
    assert "github" in result.evidence.lower()


def test_rl005_skipped_when_gh_cli_missing(tmp_path: Path) -> None:
    _git_init(tmp_path, remote_url="https://github.com/dgrauet/intendant.git")
    with patch("shutil.which", return_value=None):
        result = RL005BranchProtection().check(_repo(tmp_path))
    assert result.skipped is True
    assert "gh" in result.evidence.lower()


def _make_completed(
    returncode: int, stdout: str = "", stderr: str = ""
) -> subprocess.CompletedProcess:
    return subprocess.CompletedProcess(args=[], returncode=returncode, stdout=stdout, stderr=stderr)


def _mock_gh(api_response: str | None = None, returncode: int = 0, stderr: str = "") -> object:
    """Build a side_effect that lets git through but mocks the gh api call."""
    real_run = subprocess.run

    def side_effect(cmd, *args, **kwargs):
        if cmd and cmd[0] == "gh":
            return _make_completed(returncode, stdout=api_response or "", stderr=stderr)
        return real_run(cmd, *args, **kwargs)

    return side_effect


def test_rl005_pass_when_protection_complete(tmp_path: Path) -> None:
    _git_init(tmp_path, remote_url="https://github.com/dgrauet/intendant.git")
    api_response = (
        '{"required_pull_request_reviews": {"required_approving_review_count": 0},'
        ' "allow_force_pushes": {"enabled": false},'
        ' "allow_deletions": {"enabled": false},'
        ' "enforce_admins": {"enabled": true},'
        ' "required_status_checks": {"contexts": ["lint + type + test"]}}'
    )
    with (
        patch("shutil.which", return_value="/usr/bin/gh"),
        patch("intendant.checks.rl005.subprocess.run", side_effect=_mock_gh(api_response)),
    ):
        result = RL005BranchProtection().check(_repo(tmp_path))
    assert result.passing is True


def test_rl005_fail_when_branch_not_protected(tmp_path: Path) -> None:
    _git_init(tmp_path, remote_url="https://github.com/dgrauet/intendant.git")
    with (
        patch("shutil.which", return_value="/usr/bin/gh"),
        patch(
            "intendant.checks.rl005.subprocess.run",
            side_effect=_mock_gh(returncode=1, stderr="Branch not protected (HTTP 404)"),
        ),
    ):
        result = RL005BranchProtection().check(_repo(tmp_path))
    assert result.passing is False
    assert "not protected" in result.evidence.lower() or "404" in result.evidence


def test_rl005_skipped_when_unauthorized(tmp_path: Path) -> None:
    _git_init(tmp_path, remote_url="https://github.com/dgrauet/intendant.git")
    with (
        patch("shutil.which", return_value="/usr/bin/gh"),
        patch(
            "intendant.checks.rl005.subprocess.run",
            side_effect=_mock_gh(returncode=1, stderr="HTTP 401: Bad credentials"),
        ),
    ):
        result = RL005BranchProtection().check(_repo(tmp_path))
    assert result.skipped is True


def test_rl005_fail_when_force_pushes_allowed(tmp_path: Path) -> None:
    _git_init(tmp_path, remote_url="https://github.com/dgrauet/intendant.git")
    api_response = (
        '{"required_pull_request_reviews": {"required_approving_review_count": 0},'
        ' "allow_force_pushes": {"enabled": true},'
        ' "allow_deletions": {"enabled": false},'
        ' "enforce_admins": {"enabled": true}}'
    )
    with (
        patch("shutil.which", return_value="/usr/bin/gh"),
        patch("intendant.checks.rl005.subprocess.run", side_effect=_mock_gh(api_response)),
    ):
        result = RL005BranchProtection().check(_repo(tmp_path))
    assert result.passing is False
    assert "force" in result.evidence.lower()


def test_rl005_fail_when_pr_not_required(tmp_path: Path) -> None:
    _git_init(tmp_path, remote_url="https://github.com/dgrauet/intendant.git")
    api_response = (
        '{"allow_force_pushes": {"enabled": false},'
        ' "allow_deletions": {"enabled": false},'
        ' "enforce_admins": {"enabled": true}}'
    )
    with (
        patch("shutil.which", return_value="/usr/bin/gh"),
        patch("intendant.checks.rl005.subprocess.run", side_effect=_mock_gh(api_response)),
    ):
        result = RL005BranchProtection().check(_repo(tmp_path))
    assert result.passing is False
    assert "pull_request" in result.evidence.lower() or "pr" in result.evidence.lower()


def test_rl005_supports_ssh_remote(tmp_path: Path) -> None:
    _git_init(tmp_path, remote_url="git@github.com:dgrauet/intendant.git")
    api_response = (
        '{"required_pull_request_reviews": {},'
        ' "allow_force_pushes": {"enabled": false},'
        ' "allow_deletions": {"enabled": false},'
        ' "enforce_admins": {"enabled": true}}'
    )
    with (
        patch("shutil.which", return_value="/usr/bin/gh"),
        patch("intendant.checks.rl005.subprocess.run", side_effect=_mock_gh(api_response)),
    ):
        result = RL005BranchProtection().check(_repo(tmp_path))
    assert result.passing is True
