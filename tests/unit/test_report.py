"""Tests for Finding and Report dataclasses."""

from pathlib import Path

from suzerain.core.report import Finding, Report


def test_finding_pass() -> None:
    f = Finding(
        rule_id="TST001",
        severity="required",
        status="pass",
        evidence="",
        fix_available=False,
    )
    assert f.rule_id == "TST001"
    assert f.status == "pass"
    assert f.fix_preview is None


def test_finding_fail_with_fix() -> None:
    f = Finding(
        rule_id="PYTHON_PK002",
        severity="required",
        status="fail",
        evidence="missing file: uv.lock",
        fix_available=True,
        fix_preview="--- /dev/null\n+++ uv.lock\n@@ -0,0 +1 @@\n+# generated lockfile\n",
    )
    assert f.status == "fail"
    assert f.fix_available is True
    assert f.fix_preview is not None and "uv.lock" in f.fix_preview


def test_finding_exempt() -> None:
    f = Finding(
        rule_id="PYTHON_LO001",
        severity="required",
        status="exempt",
        evidence="exemption: Fork upstream layout",
        fix_available=False,
    )
    assert f.status == "exempt"
    assert "Fork upstream" in f.evidence


def test_report_empty(tmp_path: Path) -> None:
    r = Report(repo_path=tmp_path, stack="python", findings=[])
    assert r.score == 100  # no findings = perfect


def test_report_score_with_findings(tmp_path: Path) -> None:
    findings = [
        Finding(rule_id="A", severity="required", status="pass", evidence="", fix_available=False),
        Finding(rule_id="B", severity="required", status="fail", evidence="x", fix_available=False),
        Finding(
            rule_id="C", severity="recommended", status="pass", evidence="", fix_available=False
        ),
        Finding(rule_id="D", severity="optional", status="fail", evidence="x", fix_available=False),
    ]
    r = Report(repo_path=tmp_path, stack="python", findings=findings)
    # 2 of 4 fully pass; weights: required=10, recommended=3, optional=1
    # max = 10+10+3+1 = 24 ; got = 10+0+3+0 = 13
    # 13/24 * 100 = 54 (rounded)
    assert r.score == 54


def test_report_skipped_does_not_count(tmp_path: Path) -> None:
    findings = [
        Finding(rule_id="A", severity="required", status="pass", evidence="", fix_available=False),
        Finding(
            rule_id="B",
            severity="required",
            status="skip",
            evidence="rule did not apply",
            fix_available=False,
        ),
    ]
    r = Report(repo_path=tmp_path, stack="python", findings=findings)
    # Skipped rules excluded from scoring
    assert r.score == 100


def test_report_exempt_counted_as_pass(tmp_path: Path) -> None:
    findings = [
        Finding(rule_id="A", severity="required", status="pass", evidence="", fix_available=False),
        Finding(
            rule_id="B",
            severity="required",
            status="exempt",
            evidence="user-justified",
            fix_available=False,
        ),
    ]
    r = Report(repo_path=tmp_path, stack="python", findings=findings)
    assert r.score == 100  # exempt = passing for scoring


def test_report_summary_counts(tmp_path: Path) -> None:
    findings = [
        Finding(rule_id="A", severity="required", status="pass", evidence="", fix_available=False),
        Finding(rule_id="B", severity="required", status="fail", evidence="x", fix_available=True),
        Finding(
            rule_id="C",
            severity="recommended",
            status="exempt",
            evidence="reason",
            fix_available=False,
        ),
        Finding(
            rule_id="D",
            severity="optional",
            status="skip",
            evidence="N/A",
            fix_available=False,
        ),
    ]
    r = Report(repo_path=tmp_path, stack="python", findings=findings)
    assert r.passing == 1
    assert r.failing == 1
    assert r.exempt == 1
    assert r.skipped == 1
    assert r.fixable == 1
