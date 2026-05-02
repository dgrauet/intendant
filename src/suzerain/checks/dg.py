"""DG (docs & governance) transverse rules."""

from __future__ import annotations

from pathlib import Path

from suzerain.core.patch import Patch
from suzerain.core.repo import Repo
from suzerain.core.rule import CheckResult, Rule

_README_SKELETON = """# {name}

> One-line description.

## Status

🚧 Work in progress.

## Installation

```bash
# install command here
```

## Documentation

See [docs/](docs/).

## License

See [LICENSE](LICENSE).
"""


class DG001Readme(Rule):
    id = "DG001"
    title = "README.md present at repo root"
    severity = "required"
    stacks = ("*",)
    handbook_ref = "docs/handbook/08-docs-and-agent.md#dg001"
    template_ref = "templates/_common/README.skeleton.md"

    def check(self, repo: Repo) -> CheckResult:
        if (repo.path / "README.md").is_file():
            return CheckResult(passing=True)
        return CheckResult(passing=False, evidence="README.md not found at repo root")

    def fix(self, repo: Repo, result: CheckResult) -> Patch | None:
        target = repo.path / "README.md"
        filled = _README_SKELETON.format(name=repo.path.name)
        lines = filled.splitlines()
        diff = (
            f"--- /dev/null\n+++ README.md\n@@ -0,0 +1,{_README_SKELETON.count(chr(10))} @@\n"
            + "".join(f"+{line}\n" for line in lines)
        )
        return Patch(
            target_path=target,
            kind="create",
            content=filled,
            diff=diff,
            safe=True,
        )


class DG002CLAUDEmd(Rule):
    id = "DG002"
    title = "CLAUDE.md present at repo root"
    severity = "recommended"
    stacks = ("*",)
    handbook_ref = "docs/handbook/08-docs-and-agent.md#dg002"

    def check(self, repo: Repo) -> CheckResult:
        if (repo.path / "CLAUDE.md").is_file():
            return CheckResult(passing=True)
        return CheckResult(passing=False, evidence="CLAUDE.md not found at repo root")


class DG003ADRDir(Rule):
    id = "DG003"
    title = "docs/adr/ directory exists with at least one ADR"
    severity = "required"
    stacks = ("*",)
    handbook_ref = "docs/handbook/08-docs-and-agent.md#dg003"
    adr_ref = "0000-record-architecture-decisions"

    def check(self, repo: Repo) -> CheckResult:
        adr_dir = repo.path / "docs" / "adr"
        if not adr_dir.is_dir():
            return CheckResult(passing=False, evidence="docs/adr/ directory not found")
        adrs = list(adr_dir.glob("*.md"))
        if not adrs:
            return CheckResult(
                passing=False, evidence="docs/adr/ exists but contains no ADRs (empty)"
            )
        return CheckResult(passing=True)


class DG004License(Rule):
    id = "DG004"
    title = "LICENSE file present at repo root"
    severity = "required"
    stacks = ("*",)
    handbook_ref = "docs/handbook/08-docs-and-agent.md#dg004"
    template_ref = "templates/_common/LICENSE.template"

    def check(self, repo: Repo) -> CheckResult:
        for name in ("LICENSE", "LICENSE.txt", "LICENSE.md", "COPYING"):
            if (repo.path / name).is_file():
                return CheckResult(passing=True)
        return CheckResult(passing=False, evidence="LICENSE file not found at repo root")


_GITATTRIBUTES_LINE = "docs/superpowers/ export-ignore\n"
_GITIGNORE_BLOCK = (
    "\n# Local-only design artifacts (archived outside the repo per DG005)\ndocs/superpowers/\n"
)


def _gitignore_protects(repo_path: Path) -> bool:
    p = repo_path / ".gitignore"
    return p.is_file() and "docs/superpowers/" in p.read_text()


def _gitattributes_protects(repo_path: Path) -> bool:
    p = repo_path / ".gitattributes"
    return p.is_file() and "docs/superpowers/" in p.read_text()


class DG005SpecsLocalOnly(Rule):
    id = "DG005"
    title = "docs/superpowers/specs|plans/ are local-only"
    severity = "required"
    stacks = ("*",)
    handbook_ref = "docs/handbook/08-docs-and-agent.md#dg005"

    def check(self, repo: Repo) -> CheckResult:
        sp_dir = repo.path / "docs" / "superpowers"
        if not sp_dir.exists():
            return CheckResult(passing=True, evidence="no docs/superpowers/ directory")
        missing = []
        if not _gitignore_protects(repo.path):
            missing.append(".gitignore")
        if not _gitattributes_protects(repo.path):
            missing.append(".gitattributes")
        if not missing:
            return CheckResult(
                passing=True,
                evidence="docs/superpowers/ excluded by .gitignore + .gitattributes",
            )
        return CheckResult(
            passing=False,
            evidence=f"docs/superpowers/ exists but missing protection in: {missing}",
        )

    def fix(self, repo: Repo, result: CheckResult) -> Patch | None:
        # 2-pass: prioritize .gitignore (more critical for daily git add)
        if not _gitignore_protects(repo.path):
            target = repo.path / ".gitignore"
            existing = target.read_text() if target.is_file() else ""
            new_content = (
                existing.rstrip() + _GITIGNORE_BLOCK if existing else _GITIGNORE_BLOCK.lstrip("\n")
            )
            return Patch(
                target_path=target,
                kind="overwrite",
                content=new_content,
                diff=f"--- a/.gitignore\n+++ b/.gitignore\n@@ +N @@\n{_GITIGNORE_BLOCK}",
                safe=True,
            )
        if not _gitattributes_protects(repo.path):
            target = repo.path / ".gitattributes"
            existing = target.read_text() if target.is_file() else ""
            new_content = existing
            if existing and not existing.endswith("\n"):
                new_content += "\n"
            new_content += _GITATTRIBUTES_LINE
            _diff = f"--- a/.gitattributes\n+++ b/.gitattributes\n@@ +1 @@\n+{_GITATTRIBUTES_LINE}"
            return Patch(
                target_path=target,
                kind="overwrite",
                content=new_content,
                diff=_diff,
                safe=True,
            )
        return None
