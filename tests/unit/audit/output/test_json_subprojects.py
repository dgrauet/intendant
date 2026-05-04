"""Tests for multi-subproject JSON rendering."""

from __future__ import annotations

import json
from pathlib import Path

from suzerain.audit.output.json_format import render_json
from suzerain.core.report import Finding, Report


def _make_finding(rule_id: str, subproject: str | None) -> Finding:
    return Finding(
        rule_id=rule_id,
        severity="required",
        status="pass",
        evidence="",
        fix_available=False,
        subproject=subproject,
    )


def test_json_flat_when_no_subprojects(tmp_path: Path) -> None:
    """Backward compat: report without subprojects emits flat JSON (no `subprojects` key)."""
    report = Report(
        repo_path=tmp_path,
        stack="python",
        findings=[_make_finding("PYTHON_LO001", None)],
    )
    parsed = json.loads(render_json(report))
    assert "subprojects" not in parsed
    assert parsed["findings"]


def test_json_nested_when_multi_subproject(tmp_path: Path) -> None:
    """Multi-subproject report emits nested format with synthetic _global_ entry."""
    report = Report(
        repo_path=tmp_path,
        stack="multi",
        findings=[
            _make_finding("DG001", None),
            _make_finding("PYTHON_LO001", "backend"),
            _make_finding("NODE_PK001", "frontend"),
        ],
    )
    parsed = json.loads(render_json(report))
    assert "subprojects" in parsed
    names = [g["name"] for g in parsed["subprojects"]]
    assert names == ["_global_", "backend", "frontend"]
    global_entry = parsed["subprojects"][0]
    assert global_entry["name"] == "_global_"
    assert global_entry["path"] is None
    assert any(f["rule_id"] == "DG001" for f in global_entry["findings"])
