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
) -> Report:
    """Execute every rule against the repo and return an aggregated Report.

    Status mapping:
    - `applies()` returns False → `skip`
    - `is_rule_exempt(rule.id)` → `exempt` (regardless of check outcome)
    - `check()` raises → `fail` with the exception message in evidence
    - `check()` returns passing=True → `pass`
    - `check()` returns passing=False → `fail` (fix preview computed if available)
    """
    findings: list[Finding] = []
    for rule in rules:
        finding = _run_one(rule, repo, config)
        findings.append(finding)
    return Report(repo_path=repo.path, stack=repo.stack, findings=findings)


def _run_one(rule: Rule, repo: Repo, config: SuzerainConfig) -> Finding:
    if not rule.applies(repo):
        return Finding(
            rule_id=rule.id,
            severity=rule.severity,
            status="skip",
            evidence=f"rule does not apply to stack {repo.stack!r}",
            fix_available=False,
        )
    if config.is_rule_exempt(rule.id):
        exemption = config.exemptions[rule.id]
        return Finding(
            rule_id=rule.id,
            severity=rule.severity,
            status="exempt",
            evidence=f"exemption: {exemption.reason}",
            fix_available=False,
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
        )
    if result.passing:
        return Finding(
            rule_id=rule.id,
            severity=rule.severity,
            status="pass",
            evidence=result.evidence,
            fix_available=False,
        )
    patch = rule.fix(repo, result)
    return Finding(
        rule_id=rule.id,
        severity=rule.severity,
        status="fail",
        evidence=result.evidence,
        fix_available=patch is not None,
        fix_preview=patch.diff if patch is not None else None,
    )
