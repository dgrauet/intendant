"""RL005 — GitHub branch protection on `main`.

This is the only suzerain rule that hits the network. It uses the local
`gh` CLI to query GitHub's branch-protection API and verifies that
direct pushes to `main` are blocked. The check skips silently in any of
these cases (so it never blocks repos that have intentionally opted out):

- the repo is not a git repo
- there is no `origin` remote
- `origin` is not a GitHub URL
- the `gh` CLI is not on PATH
- the call returns 401/403 (no auth, no access)
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path

from suzerain.core.repo import Repo
from suzerain.core.rule import CheckResult, Rule

_GITHUB_HTTPS_RE = re.compile(r"^https://github\.com/([^/]+)/([^/]+?)(?:\.git)?/?$")
_GITHUB_SSH_RE = re.compile(r"^git@github\.com:([^/]+)/([^/]+?)(?:\.git)?$")


class RL005BranchProtection(Rule):
    id = "RL005"
    title = "main branch protected on GitHub (push direct blocked, PR required)"
    severity = "recommended"
    stacks = ("*",)
    handbook_ref = "docs/handbook/07-releases.md#rl005"

    def check(self, repo: Repo) -> CheckResult:
        if not (repo.path / ".git").exists():
            return CheckResult(passing=True, skipped=True, evidence="not a git repo")

        remote_url = _get_origin_url(repo.path)
        if remote_url is None:
            return CheckResult(passing=True, skipped=True, evidence="no `origin` remote configured")

        owner_repo = _parse_github_remote(remote_url)
        if owner_repo is None:
            return CheckResult(
                passing=True, skipped=True, evidence=f"origin is not a GitHub URL: {remote_url!r}"
            )

        if shutil.which("gh") is None:
            return CheckResult(
                passing=True, skipped=True, evidence="`gh` CLI not on PATH; cannot query GitHub"
            )

        owner, name = owner_repo
        proc = subprocess.run(
            ["gh", "api", f"repos/{owner}/{name}/branches/main/protection"],
            capture_output=True,
            text=True,
            check=False,
        )
        if proc.returncode != 0:
            stderr = proc.stderr.strip()
            if "401" in stderr or "403" in stderr or "Bad credentials" in stderr:
                return CheckResult(
                    passing=True,
                    skipped=True,
                    evidence=f"not authenticated to GitHub ({stderr[:80]})",
                )
            return CheckResult(
                passing=False,
                evidence=f"branch `main` is not protected on GitHub: {stderr[:120]}",
            )

        try:
            data = json.loads(proc.stdout)
        except json.JSONDecodeError:
            return CheckResult(
                passing=False,
                evidence="GitHub returned non-JSON response for branch protection",
            )

        problems: list[str] = []
        if not isinstance(data.get("required_pull_request_reviews"), dict):
            problems.append("PR not required (required_pull_request_reviews missing)")
        if data.get("allow_force_pushes", {}).get("enabled") is True:
            problems.append("force-pushes allowed")
        if data.get("allow_deletions", {}).get("enabled") is True:
            problems.append("branch deletion allowed")
        if data.get("enforce_admins", {}).get("enabled") is not True:
            problems.append("admins exempt from rules (enforce_admins=false)")

        if problems:
            return CheckResult(
                passing=False,
                evidence=f"branch protection weak: {problems}",
            )
        return CheckResult(
            passing=True,
            evidence=f"branch `main` protected on github.com/{owner}/{name}",
        )


def _get_origin_url(repo_path: Path) -> str | None:
    proc = subprocess.run(
        ["git", "-C", str(repo_path), "remote", "get-url", "origin"],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        return None
    url = proc.stdout.strip()
    return url or None


def _parse_github_remote(url: str) -> tuple[str, str] | None:
    for pattern in (_GITHUB_HTTPS_RE, _GITHUB_SSH_RE):
        match = pattern.match(url)
        if match:
            return (match.group(1), match.group(2))
    return None
