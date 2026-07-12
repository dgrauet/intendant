"""LO (layout) transverse rules."""

from __future__ import annotations

from intendant.core.config import load_config
from intendant.core.repo import Repo, detect_stacks, find_nested_stack_roots
from intendant.core.rule import CheckResult, Rule


class LO003DocsDirectory(Rule):
    id = "LO003"
    title = "Documentation in docs/"
    severity = "recommended"
    stacks = ("*",)
    handbook_ref = "docs/handbook/01-layout.md#lo003"

    def check(self, repo: Repo) -> CheckResult:
        if (repo.path / "docs").is_dir():
            return CheckResult(passing=True)
        return CheckResult(passing=False, evidence="docs/ directory not found at repo root")


class LO004NestedStackCoverage(Rule):
    id = "LO004"
    title = "nested stack roots covered by declared governance"
    severity = "recommended"
    stacks = ("*",)
    handbook_ref = "docs/handbook/01-layout.md#lo004"

    def check(self, repo: Repo) -> CheckResult:
        nested = find_nested_stack_roots(repo.path)
        if not nested:
            return CheckResult(passing=True, evidence="no nested stack roots")
        config = load_config(repo.path)
        # Stacks declared per repo-relative path prefix: subprojects, plus the
        # root composition (manual pin, or auto-detection when nothing is
        # declared at the root).
        declared: list[tuple[str, str]] = [(sp.path, sp.stack) for sp in config.subprojects]
        if config.stack is not None:
            declared.append((".", config.stack))
        if not declared or all(path != "." for path, _ in declared):
            declared.extend((".", stack) for stack in detect_stacks(repo.path))
        orphans = [
            f"{directory} ({stack})"
            for directory, stack in nested
            if not any(
                decl_stack == stack
                and (
                    decl_path == "."
                    or directory == decl_path
                    or directory.startswith(decl_path + "/")
                )
                for decl_path, decl_stack in declared
            )
        ]
        if orphans:
            return CheckResult(
                passing=False,
                evidence=(
                    f"{len(orphans)} nested stack root(s) not covered by any "
                    f"declared stack: {orphans[:5]} — declare a [[subprojects]] "
                    "entry or exempt LO004 with a reason"
                ),
            )
        return CheckResult(
            passing=True,
            evidence=f"{len(nested)} nested stack root(s), all covered",
        )
