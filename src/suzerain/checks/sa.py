"""SA (sanitizing) transverse rules."""

from __future__ import annotations

import tomllib
from pathlib import Path

from suzerain.core.patch import Patch
from suzerain.core.repo import Repo
from suzerain.core.rule import CheckResult, Rule

_MINIMUM_HOOK_IDS = {"trailing-whitespace", "end-of-file-fixer", "check-yaml"}

_BASELINE_HOOKS_REPO_YAML = """\
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v6.0.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
"""

_BASELINE_PRECOMMIT_CONTENT = """\
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v6.0.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
"""

_GITLEAKS_REPO_YAML = """\
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.30.0
    hooks:
      - id: gitleaks
"""

_GITLEAKS_PRECOMMIT_CONTENT = """\
repos:
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.30.0
    hooks:
      - id: gitleaks
"""


class SA001PreCommit(Rule):
    id = "SA001"
    title = ".pre-commit-config.yaml present with minimum baseline hooks"
    severity = "required"
    stacks = ("*",)
    handbook_ref = "docs/handbook/06-sanitizing.md#sa001"
    template_ref = "templates/python/.pre-commit-config.yaml"

    def check(self, repo: Repo) -> CheckResult:
        path = repo.path / ".pre-commit-config.yaml"
        if not path.is_file():
            return CheckResult(passing=False, evidence=".pre-commit-config.yaml not found")
        text = path.read_text()
        present = {hook for hook in _MINIMUM_HOOK_IDS if f"id: {hook}" in text}
        missing = _MINIMUM_HOOK_IDS - present
        if missing:
            return CheckResult(
                passing=False,
                evidence=f"missing baseline hooks: {sorted(missing)}",
            )
        return CheckResult(passing=True)

    def fix(self, repo: Repo, result: CheckResult) -> Patch | None:
        target = repo.path / ".pre-commit-config.yaml"
        if not target.is_file():
            return Patch(
                target_path=target,
                kind="create",
                content=_BASELINE_PRECOMMIT_CONTENT,
                diff="--- /dev/null\n+++ .pre-commit-config.yaml\n",
                safe=True,
            )
        text = target.read_text()
        if "pre-commit/pre-commit-hooks" in text:
            # Repo already declared but baseline hooks incomplete — too risky to merge
            return None
        addition = "\n" + _BASELINE_HOOKS_REPO_YAML
        new_content = text.rstrip() + addition
        return Patch(
            target_path=target,
            kind="overwrite",
            content=new_content,
            diff=(
                "--- a/.pre-commit-config.yaml\n"
                "+++ b/.pre-commit-config.yaml\n"
                f"@@ +N @@\n{addition}"
            ),
            safe=True,
        )


class SA002Gitleaks(Rule):
    id = "SA002"
    title = ".pre-commit-config.yaml exists and contains gitleaks"
    severity = "required"
    stacks = ("*",)
    handbook_ref = "docs/handbook/06-sanitizing.md#sa002"

    def check(self, repo: Repo) -> CheckResult:
        path = repo.path / ".pre-commit-config.yaml"
        if not path.is_file():
            return CheckResult(
                passing=False,
                evidence=".pre-commit-config.yaml not found",
            )
        if "gitleaks" not in path.read_text():
            return CheckResult(
                passing=False,
                evidence="gitleaks hook not found in .pre-commit-config.yaml",
            )
        return CheckResult(passing=True)

    def fix(self, repo: Repo, result: CheckResult) -> Patch | None:
        target = repo.path / ".pre-commit-config.yaml"
        if not target.is_file():
            return Patch(
                target_path=target,
                kind="create",
                content=_GITLEAKS_PRECOMMIT_CONTENT,
                diff="--- /dev/null\n+++ .pre-commit-config.yaml\n",
                safe=True,
            )
        text = target.read_text()
        if "gitleaks" in text:
            # Already present; rule should have passed — nothing to fix
            return None
        addition = "\n" + _GITLEAKS_REPO_YAML
        new_content = text.rstrip() + addition
        return Patch(
            target_path=target,
            kind="overwrite",
            content=new_content,
            diff=(
                "--- a/.pre-commit-config.yaml\n"
                "+++ b/.pre-commit-config.yaml\n"
                f"@@ +N @@\n{addition}"
            ),
            safe=True,
        )


_ENV_DOTENV_PKGS = ("python-dotenv", "python_dotenv", "dotenv", "django-dotenv")

_ENV_EXAMPLE_TEMPLATE = (
    "# Document expected environment variable names here with empty values.\n"
    "# Real .env should be gitignored and never committed.\n"
)


def _project_uses_env(repo_path: Path) -> bool:
    """Heuristic: detect if the project uses environment variables."""
    if (repo_path / ".env").is_file():
        return True
    pyproject = repo_path / "pyproject.toml"
    if pyproject.is_file():
        try:
            data = tomllib.loads(pyproject.read_text())
        except tomllib.TOMLDecodeError:
            return False
        deps_strings: list[str] = []
        deps_strings.extend(data.get("project", {}).get("dependencies", []))
        for grp in data.get("project", {}).get("optional-dependencies", {}).values():
            if isinstance(grp, list):
                deps_strings.extend(grp)
        for grp in data.get("dependency-groups", {}).values():
            if isinstance(grp, list):
                deps_strings.extend(grp)
        for dep in deps_strings:
            if not isinstance(dep, str):
                continue
            name = (
                dep.split("[", 1)[0]
                .split(">=", 1)[0]
                .split("==", 1)[0]
                .split("<", 1)[0]
                .strip()
                .lower()
            )
            if name in _ENV_DOTENV_PKGS:
                return True
    return False


class SA003EnvExample(Rule):
    id = "SA003"
    title = ".env.example documents env vars (without secrets)"
    severity = "required"
    stacks = ("*",)
    handbook_ref = "docs/handbook/06-sanitizing.md#sa003"

    def check(self, repo: Repo) -> CheckResult:
        if not _project_uses_env(repo.path):
            return CheckResult(
                passing=True,
                skipped=True,
                evidence="no .env file and no dotenv-style dep — rule does not apply",
            )
        env_example = repo.path / ".env.example"
        if env_example.is_file():
            return CheckResult(passing=True, evidence=".env.example present at repo root")
        return CheckResult(
            passing=False,
            evidence=".env.example not found at repo root (project uses env vars)",
        )

    def fix(self, repo: Repo, result: CheckResult) -> Patch | None:
        if result.skipped or result.passing:
            return None
        target = repo.path / ".env.example"
        if target.is_file():
            return None
        return Patch(
            target_path=target,
            kind="create",
            content=_ENV_EXAMPLE_TEMPLATE,
            diff=f"--- /dev/null\n+++ .env.example\n@@ +1 @@\n+{_ENV_EXAMPLE_TEMPLATE}",
            safe=True,
        )


_GITIGNORE_BASELINE_GENERIC = (".DS_Store",)


class SA004GitignoreBaseline(Rule):
    id = "SA004"
    title = ".gitignore exists with a generic baseline (.DS_Store)"
    severity = "required"
    stacks = ("*",)
    handbook_ref = "docs/handbook/06-sanitizing.md#sa004"

    def check(self, repo: Repo) -> CheckResult:
        path = repo.path / ".gitignore"
        if not path.is_file():
            return CheckResult(passing=False, evidence=".gitignore not found at repo root")
        text = path.read_text()
        missing = [p for p in _GITIGNORE_BASELINE_GENERIC if p not in text]
        if missing:
            return CheckResult(
                passing=False,
                evidence=f"missing baseline patterns in .gitignore: {missing}",
            )
        return CheckResult(passing=True, evidence="generic baseline present")
