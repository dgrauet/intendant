"""Tests for JSON output."""

import json
from pathlib import Path

from suzerain.audit.output.json_format import render_json
from suzerain.core.report import Finding, Report


def test_json_basic_shape(tmp_path: Path) -> None:
    report = Report(repo_path=tmp_path, stack="python", findings=[])
    out = render_json(report)
    parsed = json.loads(out)
    assert parsed["repo_path"] == str(tmp_path)
    assert parsed["stack"] == "python"
    assert parsed["score"] == 100
    assert parsed["findings"] == []


def test_json_finding_fields(tmp_path: Path) -> None:
    findings = [
        Finding(
            rule_id="PYTHON_PK002",
            severity="required",
            status="fail",
            evidence="missing uv.lock",
            fix_available=True,
            fix_preview="--- /dev/null\n+++ uv.lock\n",
        )
    ]
    report = Report(repo_path=tmp_path, stack="python", findings=findings)
    parsed = json.loads(render_json(report))
    assert len(parsed["findings"]) == 1
    f = parsed["findings"][0]
    assert f["rule_id"] == "PYTHON_PK002"
    assert f["status"] == "fail"
    assert f["fix_available"] is True
    assert f["fix_preview"].startswith("---")


def test_json_summary_counts(tmp_path: Path) -> None:
    findings = [
        Finding(rule_id="A", severity="required", status="pass", evidence="", fix_available=False),
        Finding(rule_id="B", severity="required", status="fail", evidence="x", fix_available=True),
    ]
    report = Report(repo_path=tmp_path, stack="python", findings=findings)
    parsed = json.loads(render_json(report))
    assert parsed["summary"]["passing"] == 1
    assert parsed["summary"]["failing"] == 1
    assert parsed["summary"]["fixable"] == 1
