"""End-to-end test: skill adapter audits a realistic fixture."""

from __future__ import annotations

from pathlib import Path

from intendant.adapters.claude_skill import RULES as CLAUDE_SKILL_RULES
from intendant.audit.runner import run_audit
from intendant.core.config import IntendantConfig
from intendant.core.repo import Repo


def test_e2e_valid_skill_passes_all_sk_rules(fixtures_dir: Path) -> None:
    repo_path = fixtures_dir / "valid_claude_skill_repo"
    repo = Repo.from_path(repo_path)
    assert "claude-skill" in repo.stacks

    cfg = IntendantConfig(version="1", stack="claude-skill", enforcement="strict")
    report = run_audit(repo, cfg, CLAUDE_SKILL_RULES)
    sk_findings = [f for f in report.findings if f.rule_id.startswith("CLAUDE_SKILL_SK")]
    assert len(sk_findings) == 7

    failed = [f for f in sk_findings if f.status == "fail"]
    assert failed == [], f"unexpected SK fails: {[(f.rule_id, f.evidence) for f in failed]}"
