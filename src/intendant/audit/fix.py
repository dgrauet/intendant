"""Apply safe fixes from an audit Report."""

from __future__ import annotations

from pathlib import Path

from intendant.audit.registry import collect_rules
from intendant.core.config import IntendantConfig
from intendant.core.patch import Patch, apply_patch
from intendant.core.repo import Repo
from intendant.core.report import Report


def apply_fixes(
    report: Report,
    repo: Repo,
    config: IntendantConfig,
    *,
    dry_run: bool = False,
) -> tuple[list[str], list[str]]:
    """Apply safe fixes; deposit unsafe ones under .intendant/proposed/.

    Returns: (applied_rule_ids, proposed_rule_ids).
    """
    rules_by_id = {r.id: r for r in collect_rules()}
    applied: list[str] = []
    proposed: list[str] = []
    for finding in report.findings:
        if finding.status != "fail" or not finding.fix_available:
            continue
        rule = rules_by_id.get(finding.rule_id)
        if rule is None:
            continue
        result = rule.check(repo)  # re-derive CheckResult to pass to fix()
        patch = rule.fix(repo, result)
        if patch is None:
            continue
        if patch.safe:
            if not dry_run:
                apply_patch(patch)
            applied.append(rule.id)
        else:
            if not dry_run:
                _propose(patch, repo.path)
            proposed.append(rule.id)
    return applied, proposed


def _propose(patch: Patch, repo_root: Path) -> None:
    out_dir = repo_root / ".intendant" / "proposed"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"{patch.target_path.name}.diff"
    out_file.write_text(patch.diff)
