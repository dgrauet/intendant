"""Audit runner — execute rules against a repo and produce a Report."""

from __future__ import annotations

from collections.abc import Sequence

from suzerain.core.config import SuzerainConfig
from suzerain.core.repo import Repo
from suzerain.core.report import Finding, Report
from suzerain.core.rule import Rule


def run_audit(
    repo: Repo,
    config: SuzerainConfig,
    rules: Sequence[Rule],
    *,
    compute_fix_preview: bool = False,
) -> Report:
    """Execute every rule against the repo and return an aggregated Report.

    When ``config.subprojects`` is empty (legacy mode), every rule that applies
    to the repo executes against `repo` (transverse + matching stack-specific).

    When ``config.subprojects`` is non-empty (multi-subproject mode):
    - Transverse rules (`stacks=("*",)`) run once at the root meta-Repo (name=None).
    - Stack-specific rules run for each declared subproject (name=<subproject_name>),
      with the subproject's `path` resolved against the root.
    - Findings are aggregated; each Finding is tagged with the `subproject` name
      (or None for transverse).
    - If a subproject's path doesn't exist on disk, applicable stack-specific
      rules emit a `status="skip"` finding with evidence "subproject path not found".
    """
    if not config.subprojects:
        # Legacy single-Repo path
        findings: list[Finding] = []
        for rule in rules:
            finding = _run_one(rule, repo, config, compute_fix_preview=compute_fix_preview)
            findings.append(finding)
        return Report(repo_path=repo.path, stack=repo.stack, findings=findings)

    # Multi-subproject orchestration
    findings = []

    # Step 1: transverse rules at root meta-Repo (name=None)
    root_meta = Repo(path=repo.path, stack="multi", name=None)
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
                applies_check = Repo(path=sub_path, stack=sp.stack, name=sp.name)
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
        sub_repo = Repo(path=sub_path, stack=sp.stack, name=sp.name)
        for rule in stack_rules:
            if not rule.applies(sub_repo):
                continue
            findings.append(
                _run_one(rule, sub_repo, config, compute_fix_preview=compute_fix_preview)
            )

    return Report(repo_path=repo.path, stack="multi", findings=findings)


def _run_one(
    rule: Rule,
    repo: Repo,
    config: SuzerainConfig,
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
            evidence=f"rule does not apply to stack {repo.stack!r}",
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
