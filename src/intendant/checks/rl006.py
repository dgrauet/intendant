"""RL006 — release-please wired through a GitHub App token.

Static check (no network, unlike RL005). Locates the single workflow file
that uses ``googleapis/release-please-action`` and verifies the *complete*
configuration: a GitHub App token is minted and used (not the default
``GITHUB_TOKEN``), and the ``config-file`` / ``manifest-file`` inputs are
referenced.

Rationale: a release PR created with the default ``GITHUB_TOKEN`` cannot
trigger other workflows (GitHub loop prevention), leaving required checks
unrun and the PR unmergeable. The App token avoids this.

Skips silently when the repo has no ``.github/workflows/`` directory
(covered by CI001) or when no workflow uses release-please (the repo has
not opted into release-please; presence of the JSON files is RL003's job).
"""

from __future__ import annotations

import re

from intendant.core.repo import Repo
from intendant.core.rule import CheckResult, Rule

_RELEASE_PLEASE_ACTION = "googleapis/release-please-action"
_APP_TOKEN_ACTION = "actions/create-github-app-token"
# A reference to the minted App token's output, e.g.
# ${{ steps.app-token.outputs.token }} (step id is arbitrary).
_APP_TOKEN_OUTPUT_RE = re.compile(r"steps\.[\w-]+\.outputs\.token")
# Default-token markers that must NOT be used as the release-please token.
_DEFAULT_TOKEN_MARKERS = ("secrets.GITHUB_TOKEN", "github.token")


class RL006ReleasePleaseGitHubApp(Rule):
    id = "RL006"
    title = "release-please uses a GitHub App token (not the default GITHUB_TOKEN)"
    severity = "recommended"
    stacks = ("*",)
    handbook_ref = "docs/handbook/07-releases.md#rl006"
    adr_ref = "0005-release-please"

    def check(self, repo: Repo) -> CheckResult:
        wf_dir = repo.path / ".github" / "workflows"
        if not wf_dir.is_dir():
            return CheckResult(
                passing=True,
                skipped=True,
                evidence="no .github/workflows/ directory (covered by CI001)",
            )

        workflows = list(wf_dir.glob("*.yml")) + list(wf_dir.glob("*.yaml"))
        target = None
        for wf in workflows:
            text = wf.read_text(errors="replace")
            if _RELEASE_PLEASE_ACTION in text:
                target = text
                break
        if target is None:
            return CheckResult(
                passing=True,
                skipped=True,
                evidence=(
                    "no workflow uses googleapis/release-please-action (RL003 covers file presence)"
                ),
            )

        problems: list[str] = []
        if _APP_TOKEN_ACTION not in target:
            problems.append("no actions/create-github-app-token step (GitHub App token missing)")
        if not _APP_TOKEN_OUTPUT_RE.search(target):
            problems.append("release-please token is not bound to a create-github-app-token output")
        used_default = [m for m in _DEFAULT_TOKEN_MARKERS if m in target]
        if used_default:
            problems.append(f"default token used instead of a GitHub App token: {used_default}")
        if "config-file:" not in target:
            problems.append("config-file: input missing")
        if "manifest-file:" not in target:
            problems.append("manifest-file: input missing")

        if problems:
            return CheckResult(passing=False, evidence="; ".join(problems))
        return CheckResult(
            passing=True,
            evidence=(
                "release-please wired through a GitHub App token with config-file + manifest-file"
            ),
        )
