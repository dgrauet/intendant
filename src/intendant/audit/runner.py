"""Audit runner — execute rules against a repo and produce a Report."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from intendant.core.config import IntendantConfig
from intendant.core.repo import Repo, detect_stacks
from intendant.core.report import Finding, Report
from intendant.core.rule import Rule


def resolve_repo(repo_path: Path, config: IntendantConfig) -> Repo:
    """Build the effective root Repo from filesystem + ``.intendant.toml``.

    Resolution rules:
    - subprojects declared → ``mode=manual``, stacks = union of subproject stacks
    - top-level ``stack = "..."`` pinned → ``mode=manual``, stacks=(that one,)
    - neither → ``mode=auto``, stacks = whatever ``detect_stacks`` finds
    """
    path = repo_path
    if config.subprojects:
        seen: list[str] = []
        for sp in config.subprojects:
            if sp.stack and sp.stack not in seen:
                seen.append(sp.stack)
        return Repo(path=path, stacks=tuple(seen), mode="manual")
    if config.stack is not None:
        return Repo(path=path, stacks=(config.stack,), mode="manual")
    return Repo(path=path, stacks=detect_stacks(path), mode="auto")


def run_audit(
    repo: Repo,
    config: IntendantConfig,
    rules: Sequence[Rule],
    *,
    compute_fix_preview: bool = False,
) -> Report:
    """Execute every rule against the repo and return an aggregated Report.

    When ``config.subprojects`` is empty (single-Repo mode), every rule that
    applies to the repo executes against `repo` (transverse + matching
    stack-specific). The repo's own ``mode`` and ``stacks`` are surfaced on
    the resulting ``Report``.

    When ``config.subprojects`` is non-empty (multi-subproject mode):
    - Transverse rules (``stacks=("*",)``) run once at the root meta-Repo
      (``name=None``), built with ``mode="manual"`` and the union of the
      subprojects' stacks.
    - Stack-specific rules run for each declared subproject (``name=<n>``),
      with the subproject's ``path`` resolved against the root and
      ``stacks=(sp.stack,)``.
    - Findings are aggregated; each Finding is tagged with the ``subproject``
      name (or None for transverse).
    - If a subproject's path doesn't exist on disk, applicable stack-specific
      rules emit a ``status="skip"`` finding.
    """
    if not config.subprojects:
        findings: list[Finding] = []
        for rule in rules:
            findings.append(_run_one(rule, repo, config, compute_fix_preview=compute_fix_preview))
        return Report(
            repo_path=repo.path,
            stacks=repo.stacks,
            mode=repo.mode,
            findings=findings,
        )

    # Multi-subproject orchestration
    findings = []
    sub_stacks: list[str] = []
    for sp in config.subprojects:
        if sp.stack and sp.stack not in sub_stacks:
            sub_stacks.append(sp.stack)
    aggregated = tuple(sub_stacks)

    # Step 1: transverse rules at root meta-Repo (name=None)
    root_meta = Repo(path=repo.path, stacks=aggregated, mode="manual", name=None)
    transverse_rules = [r for r in rules if "*" in r.stacks]
    for rule in transverse_rules:
        findings.append(_run_one(rule, root_meta, config, compute_fix_preview=compute_fix_preview))

    # Step 2: stack-specific rules per subproject
    stack_rules = [r for r in rules if "*" not in r.stacks]
    for sp in config.subprojects:
        sub_path_raw = repo.path / sp.path
        sub_path = sub_path_raw.resolve() if sub_path_raw.exists() else sub_path_raw
        if not sub_path_raw.is_dir():
            evidence = (
                f"subproject path not found: {sp.path!r}"
                if not sub_path_raw.exists()
                else f"subproject path is not a directory: {sp.path!r}"
            )
            for rule in stack_rules:
                applies_check = Repo(path=sub_path, stacks=(sp.stack,), mode="manual", name=sp.name)
                if rule.applies(applies_check):
                    findings.append(
                        Finding(
                            rule_id=rule.id,
                            severity=rule.severity,
                            status="skip",
                            evidence=evidence,
                            fix_available=False,
                            subproject=sp.name,
                        )
                    )
            continue
        sub_repo = Repo(path=sub_path, stacks=(sp.stack,), mode="manual", name=sp.name)
        for rule in stack_rules:
            if not rule.applies(sub_repo):
                continue
            findings.append(
                _run_one(rule, sub_repo, config, compute_fix_preview=compute_fix_preview)
            )

    return Report(repo_path=repo.path, stacks=aggregated, mode="manual", findings=findings)


def _run_one(
    rule: Rule,
    repo: Repo,
    config: IntendantConfig,
    *,
    compute_fix_preview: bool = False,
) -> Finding:
    """Run a single rule and return a Finding (tagged with repo.name as subproject)."""
    sp = repo.name
    if not rule.applies(repo):
        return Finding(
            rule_id=rule.id,
            severity=rule.severity,
            status="skip",
            evidence=f"rule does not apply to stacks {list(repo.stacks)!r}",
            fix_available=False,
            subproject=sp,
        )
    exemption = config.is_rule_exempt_for_subproject(rule.id, sp)
    if exemption is not None:
        return Finding(
            rule_id=rule.id,
            severity=rule.severity,
            status="exempt",
            evidence=f"exemption: {exemption.reason}",
            fix_available=False,
            subproject=sp,
        )
    try:
        result = rule.check(repo)
    except Exception as exc:
        return Finding(
            rule_id=rule.id,
            severity=rule.severity,
            status="fail",
            evidence=f"rule raised: {exc}",
            fix_available=False,
            subproject=sp,
        )
    if result.skipped:
        return Finding(
            rule_id=rule.id,
            severity=rule.severity,
            status="skip",
            evidence=result.evidence,
            fix_available=False,
            subproject=sp,
        )
    if result.passing:
        return Finding(
            rule_id=rule.id,
            severity=rule.severity,
            status="pass",
            evidence=result.evidence,
            fix_available=False,
            subproject=sp,
        )
    if not compute_fix_preview:
        return Finding(
            rule_id=rule.id,
            severity=rule.severity,
            status="fail",
            evidence=result.evidence,
            fix_available=type(rule).supports_fix(),
            fix_preview=None,
            subproject=sp,
        )
    patch = rule.fix(repo, result)
    return Finding(
        rule_id=rule.id,
        severity=rule.severity,
        status="fail",
        evidence=result.evidence,
        fix_available=patch is not None,
        fix_preview=patch.diff if patch is not None else None,
        subproject=sp,
    )
