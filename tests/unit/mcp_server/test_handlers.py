"""Tests for the MCP handler functions (the plain-Python layer FastMCP wraps)."""

from __future__ import annotations

from pathlib import Path

import pytest

from intendant.mcp_server.handlers import (
    audit_repo,
    diff_portfolio,
    explain_rule,
    list_rules,
    report_portfolio,
)

FIXTURES = Path(__file__).resolve().parents[2] / "fixtures"


def test_audit_repo_returns_schema_v2_payload() -> None:
    payload = audit_repo(str(FIXTURES / "conformant_python_repo"))
    assert payload["schema_version"] == "2"
    assert payload["stacks"] == ["python"]
    assert payload["mode"] == "manual"  # fixture pins stack="python" in .intendant.toml
    assert isinstance(payload["score"], int)
    assert isinstance(payload["findings"], list)
    assert payload["findings"], "conformant repo should still produce per-rule findings"


def test_audit_repo_unknown_path_returns_error() -> None:
    payload = audit_repo("/tmp/this-path-does-not-exist-intendant-mcp")
    assert payload["error"]
    assert "not found" in payload["error"].lower() or "does not exist" in payload["error"].lower()


def test_audit_repo_severity_filters_findings() -> None:
    full = audit_repo(str(FIXTURES / "nonconformant_python_repo"))
    required_only = audit_repo(str(FIXTURES / "nonconformant_python_repo"), severity="required")
    assert len(required_only["findings"]) <= len(full["findings"])
    for f in required_only["findings"]:
        assert f["severity"] == "required"


def test_explain_rule_returns_handbook_body_for_known_rule() -> None:
    payload = explain_rule("RL002")
    assert payload["rule_id"] == "RL002"
    assert payload["severity"] == "required"
    assert payload["body"]
    assert "conventional" in payload["body"].lower()


def test_explain_rule_unknown_returns_error() -> None:
    payload = explain_rule("NOPE_999")
    assert payload["error"]
    assert "NOPE_999" in payload["error"]


def test_list_rules_returns_all_rules_with_metadata() -> None:
    payload = list_rules()
    assert isinstance(payload["rules"], list)
    assert payload["count"] == len(payload["rules"])
    assert payload["count"] >= 30  # 38+ rules ship today
    sample = payload["rules"][0]
    assert {"id", "title", "severity", "stacks"}.issubset(sample.keys())


def test_list_rules_filtered_by_stack() -> None:
    payload = list_rules(stack="python")
    assert payload["rules"]
    for r in payload["rules"]:
        assert "python" in r["stacks"] or "*" in r["stacks"]


def test_list_rules_filtered_by_severity() -> None:
    payload = list_rules(severity="required")
    assert payload["rules"]
    for r in payload["rules"]:
        assert r["severity"] == "required"


def test_report_portfolio_returns_schema_v2_payload() -> None:
    payload = report_portfolio(str(FIXTURES / "portfolio_mini"))
    assert payload["schema_version"] == "2"
    assert payload["scan_count"] >= 1
    assert isinstance(payload["repos"], list)


def test_report_portfolio_unknown_path_returns_error() -> None:
    payload = report_portfolio("/tmp/this-path-does-not-exist-intendant-mcp")
    assert payload["error"]


def test_diff_portfolio_without_snapshot_returns_explanatory_error(tmp_path: Path) -> None:
    payload = diff_portfolio(str(tmp_path))
    assert payload["error"]
    assert "snapshot" in payload["error"].lower()


@pytest.mark.parametrize("severity", ["nonsense", "REQUIRED", ""])
def test_audit_repo_invalid_severity_rejected(severity: str) -> None:
    payload = audit_repo(str(FIXTURES / "conformant_python_repo"), severity=severity)
    assert payload["error"]
