"""Unit tests for suzerain.audit.diff."""

from __future__ import annotations

from typing import Any

from suzerain.audit.diff import PortfolioDiff, compute_diff

# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------


def _make_snapshot(
    *,
    repos: list[dict[str, Any]] | None = None,
    rules_in_scan: list[dict[str, Any]] | None = None,
    timestamp: str = "2026-05-01T12:00:00",
    root: str = "/work",
) -> dict[str, Any]:
    return {
        "schema_version": "2",
        "root": root,
        "timestamp": timestamp,
        "scan_count": len(repos or []),
        "repos": repos or [],
        "rules_in_scan": rules_in_scan or [],
    }


def _repo(
    path: str,
    score: int | None = 100,
    failing: list[str] | None = None,
) -> dict[str, Any]:
    failing = failing or []
    return {
        "path": path,
        "stack": "python",
        "score": score,
        "status": "ok",
        "failing_rule_ids": failing,
        "failing_by_severity": {"required": 0, "recommended": 0, "optional": 0},
        "fixable_count": 0,
    }


def _rule(rid: str, severity: str = "required") -> dict[str, Any]:
    return {"id": rid, "severity": severity, "title": f"Rule {rid}", "fixable": False}


# ---------------------------------------------------------------------------
# compute_diff
# ---------------------------------------------------------------------------


def test_compute_diff_returns_portfolio_diff() -> None:
    current = _make_snapshot()
    previous = _make_snapshot()
    diff = compute_diff(current, previous, "/path/to/prev.json")
    assert isinstance(diff, PortfolioDiff)
    assert diff.previous_path == "/path/to/prev.json"


# ---------------------------------------------------------------------------
# score_changes
# ---------------------------------------------------------------------------


def test_score_changes_positive_delta() -> None:
    current = _make_snapshot(repos=[_repo("proj-a", score=92)])
    previous = _make_snapshot(repos=[_repo("proj-a", score=87)])
    diff = compute_diff(current, previous, "prev.json")
    changes = diff.score_changes
    assert len(changes) == 1
    assert changes[0] == {"path": "proj-a", "before": 87, "after": 92, "delta": 5}


def test_score_changes_negative_delta() -> None:
    current = _make_snapshot(repos=[_repo("proj-b", score=87)])
    previous = _make_snapshot(repos=[_repo("proj-b", score=94)])
    diff = compute_diff(current, previous, "prev.json")
    changes = diff.score_changes
    assert len(changes) == 1
    assert changes[0]["delta"] == -7


def test_score_changes_no_delta() -> None:
    current = _make_snapshot(repos=[_repo("proj-c", score=100)])
    previous = _make_snapshot(repos=[_repo("proj-c", score=100)])
    diff = compute_diff(current, previous, "prev.json")
    changes = diff.score_changes
    assert len(changes) == 1
    assert changes[0]["delta"] == 0


def test_score_changes_excludes_new_repos() -> None:
    """Repos only in current (new repos) are not in score_changes."""
    current = _make_snapshot(repos=[_repo("existing", score=90), _repo("brand-new", score=80)])
    previous = _make_snapshot(repos=[_repo("existing", score=85)])
    diff = compute_diff(current, previous, "prev.json")
    paths = [c["path"] for c in diff.score_changes]
    assert "brand-new" not in paths
    assert "existing" in paths


def test_score_changes_excludes_removed_repos() -> None:
    """Repos only in previous (removed) are not in score_changes."""
    current = _make_snapshot(repos=[_repo("existing", score=90)])
    previous = _make_snapshot(repos=[_repo("existing", score=85), _repo("removed", score=70)])
    diff = compute_diff(current, previous, "prev.json")
    paths = [c["path"] for c in diff.score_changes]
    assert "removed" not in paths


def test_score_changes_skips_none_scores() -> None:
    r = _repo("proj", score=None)
    current = _make_snapshot(repos=[r])
    previous = _make_snapshot(repos=[r])
    diff = compute_diff(current, previous, "prev.json")
    assert diff.score_changes == []


def test_score_changes_multiple_repos() -> None:
    current = _make_snapshot(
        repos=[
            _repo("a", score=92),
            _repo("b", score=87),
            _repo("c", score=100),
        ]
    )
    previous = _make_snapshot(
        repos=[
            _repo("a", score=87),
            _repo("b", score=94),
            _repo("c", score=100),
        ]
    )
    diff = compute_diff(current, previous, "prev.json")
    changes = {c["path"]: c["delta"] for c in diff.score_changes}
    assert changes["a"] == 5
    assert changes["b"] == -7
    assert changes["c"] == 0


# ---------------------------------------------------------------------------
# new_failures / resolved_failures
# ---------------------------------------------------------------------------


def test_new_failures_detects_regression() -> None:
    rules = [_rule("SA001", "required"), _rule("DG002", "recommended")]
    current = _make_snapshot(
        repos=[_repo("proj-b", failing=["SA001", "DG002"])],
        rules_in_scan=rules,
    )
    previous = _make_snapshot(repos=[_repo("proj-b", failing=[])], rules_in_scan=rules)
    diff = compute_diff(current, previous, "prev.json")
    new = diff.new_failures
    assert len(new) == 2
    rule_ids = {f["rule_id"] for f in new}
    assert "SA001" in rule_ids
    assert "DG002" in rule_ids


def test_new_failures_empty_when_no_regression() -> None:
    current = _make_snapshot(repos=[_repo("a", failing=["RL001"])])
    previous = _make_snapshot(repos=[_repo("a", failing=["RL001"])])
    diff = compute_diff(current, previous, "prev.json")
    assert diff.new_failures == []


def test_new_failures_severity_from_rules_in_scan() -> None:
    rules = [_rule("SA001", "required")]
    current = _make_snapshot(repos=[_repo("a", failing=["SA001"])], rules_in_scan=rules)
    previous = _make_snapshot(repos=[_repo("a", failing=[])], rules_in_scan=rules)
    diff = compute_diff(current, previous, "prev.json")
    new = diff.new_failures
    assert new[0]["severity"] == "required"


def test_new_failures_severity_unknown_for_unknown_rule() -> None:
    current = _make_snapshot(repos=[_repo("a", failing=["XX999"])])
    previous = _make_snapshot(repos=[_repo("a", failing=[])])
    diff = compute_diff(current, previous, "prev.json")
    new = diff.new_failures
    assert new[0]["severity"] == "unknown"


def test_resolved_failures_detects_improvement() -> None:
    rules = [_rule("RL001", "required")]
    current = _make_snapshot(repos=[_repo("proj-a", failing=[])], rules_in_scan=rules)
    previous = _make_snapshot(repos=[_repo("proj-a", failing=["RL001"])], rules_in_scan=rules)
    diff = compute_diff(current, previous, "prev.json")
    resolved = diff.resolved_failures
    assert len(resolved) == 1
    assert resolved[0]["rule_id"] == "RL001"
    assert resolved[0]["severity"] == "required"


def test_resolved_failures_empty_when_no_improvement() -> None:
    current = _make_snapshot(repos=[_repo("a", failing=["RL001"])])
    previous = _make_snapshot(repos=[_repo("a", failing=["RL001"])])
    diff = compute_diff(current, previous, "prev.json")
    assert diff.resolved_failures == []


def test_new_and_resolved_failures_disjoint() -> None:
    """SA001 added, RL001 resolved — both tracked simultaneously."""
    rules = [_rule("SA001", "required"), _rule("RL001", "required")]
    current = _make_snapshot(repos=[_repo("a", failing=["SA001"])], rules_in_scan=rules)
    previous = _make_snapshot(repos=[_repo("a", failing=["RL001"])], rules_in_scan=rules)
    diff = compute_diff(current, previous, "prev.json")
    assert any(f["rule_id"] == "SA001" for f in diff.new_failures)
    assert any(f["rule_id"] == "RL001" for f in diff.resolved_failures)


# ---------------------------------------------------------------------------
# new_repos / removed_repos
# ---------------------------------------------------------------------------


def test_new_repos_detects_addition() -> None:
    current = _make_snapshot(repos=[_repo("existing"), _repo("brand-new")])
    previous = _make_snapshot(repos=[_repo("existing")])
    diff = compute_diff(current, previous, "prev.json")
    assert diff.new_repos == ["brand-new"]


def test_new_repos_empty_when_none_added() -> None:
    current = _make_snapshot(repos=[_repo("a")])
    previous = _make_snapshot(repos=[_repo("a")])
    diff = compute_diff(current, previous, "prev.json")
    assert diff.new_repos == []


def test_removed_repos_detects_removal() -> None:
    current = _make_snapshot(repos=[_repo("existing")])
    previous = _make_snapshot(repos=[_repo("existing"), _repo("old-project")])
    diff = compute_diff(current, previous, "prev.json")
    assert diff.removed_repos == ["old-project"]


def test_removed_repos_empty_when_none_removed() -> None:
    current = _make_snapshot(repos=[_repo("a")])
    previous = _make_snapshot(repos=[_repo("a")])
    diff = compute_diff(current, previous, "prev.json")
    assert diff.removed_repos == []


def test_new_and_removed_repos_simultaneously() -> None:
    current = _make_snapshot(repos=[_repo("old"), _repo("new-one")])
    previous = _make_snapshot(repos=[_repo("old"), _repo("gone")])
    diff = compute_diff(current, previous, "prev.json")
    assert diff.new_repos == ["new-one"]
    assert diff.removed_repos == ["gone"]


def test_new_repos_sorted() -> None:
    current = _make_snapshot(repos=[_repo("z-repo"), _repo("a-repo"), _repo("m-repo")])
    previous = _make_snapshot(repos=[])
    diff = compute_diff(current, previous, "prev.json")
    assert diff.new_repos == ["a-repo", "m-repo", "z-repo"]


# ---------------------------------------------------------------------------
# has_new_required_failure
# ---------------------------------------------------------------------------


def test_has_new_required_failure_true_when_required_added() -> None:
    rules = [_rule("SA001", "required")]
    current = _make_snapshot(repos=[_repo("a", failing=["SA001"])], rules_in_scan=rules)
    previous = _make_snapshot(repos=[_repo("a", failing=[])], rules_in_scan=rules)
    diff = compute_diff(current, previous, "prev.json")
    assert diff.has_new_required_failure is True


def test_has_new_required_failure_false_when_only_recommended() -> None:
    rules = [_rule("DG002", "recommended")]
    current = _make_snapshot(repos=[_repo("a", failing=["DG002"])], rules_in_scan=rules)
    previous = _make_snapshot(repos=[_repo("a", failing=[])], rules_in_scan=rules)
    diff = compute_diff(current, previous, "prev.json")
    assert diff.has_new_required_failure is False


def test_has_new_required_failure_false_when_no_new_failures() -> None:
    current = _make_snapshot(repos=[_repo("a", failing=[])])
    previous = _make_snapshot(repos=[_repo("a", failing=[])])
    diff = compute_diff(current, previous, "prev.json")
    assert diff.has_new_required_failure is False


def test_has_new_required_failure_false_when_improvement_only() -> None:
    """Resolved failure doesn't trigger exit-code-1."""
    rules = [_rule("RL001", "required")]
    current = _make_snapshot(repos=[_repo("a", failing=[])], rules_in_scan=rules)
    previous = _make_snapshot(repos=[_repo("a", failing=["RL001"])], rules_in_scan=rules)
    diff = compute_diff(current, previous, "prev.json")
    assert diff.has_new_required_failure is False


# ---------------------------------------------------------------------------
# _severity_map — uses both current and previous rules_in_scan
# ---------------------------------------------------------------------------


def test_severity_map_merges_both_scans() -> None:
    current = _make_snapshot(
        repos=[_repo("a", failing=["SA001"])],
        rules_in_scan=[_rule("SA001", "required")],
    )
    previous = _make_snapshot(
        repos=[_repo("a", failing=["RL001"])],
        rules_in_scan=[_rule("RL001", "recommended")],
    )
    diff = compute_diff(current, previous, "prev.json")
    sev_map = diff._severity_map()
    assert sev_map["SA001"] == "required"
    assert sev_map["RL001"] == "recommended"


def test_severity_map_current_overrides_previous() -> None:
    """If same rule exists in both, current wins (per spec: current rules updated last)."""
    rule_in_prev = {"id": "SA001", "severity": "recommended", "title": "Old", "fixable": False}
    rule_in_cur = {"id": "SA001", "severity": "required", "title": "Updated", "fixable": False}
    current = _make_snapshot(repos=[], rules_in_scan=[rule_in_cur])
    previous = _make_snapshot(repos=[], rules_in_scan=[rule_in_prev])
    diff = compute_diff(current, previous, "prev.json")
    assert diff._severity_map()["SA001"] == "required"


# ---------------------------------------------------------------------------
# Empty portfolio edge cases
# ---------------------------------------------------------------------------


def test_empty_portfolios_produce_no_diffs() -> None:
    current = _make_snapshot(repos=[])
    previous = _make_snapshot(repos=[])
    diff = compute_diff(current, previous, "prev.json")
    assert diff.score_changes == []
    assert diff.new_failures == []
    assert diff.resolved_failures == []
    assert diff.new_repos == []
    assert diff.removed_repos == []
    assert diff.has_new_required_failure is False
