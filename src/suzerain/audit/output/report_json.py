"""Render a PortfolioReport to a JSON string."""

from __future__ import annotations

import json
from typing import Any

from suzerain.audit.registry import collect_rules
from suzerain.commands.report import PortfolioReport

_SCHEMA_VERSION = "1"


def render_report_json(scan: PortfolioReport) -> str:
    """Return the JSON-serialized representation of a portfolio report scan."""
    rules_by_id = {r.id: r for r in collect_rules()}
    repos: list[dict[str, Any]] = []
    failing_ids: set[str] = set()
    fixable_ids: set[str] = set()
    for repo_path, result in scan.reports:
        try:
            rel = str(repo_path.relative_to(scan.root))
        except ValueError:
            rel = str(repo_path)
        if isinstance(result, Exception):
            repos.append(
                {
                    "path": rel,
                    "stack": None,
                    "score": None,
                    "status": "error",
                    "failing_rule_ids": [],
                    "failing_by_severity": {"required": 0, "recommended": 0, "optional": 0},
                    "fixable_count": 0,
                    "error": f"{type(result).__name__}: {result}",
                }
            )
            continue
        repo_failing = [f for f in result.findings if f.status == "fail"]
        repo_failing_ids = sorted(f.rule_id for f in repo_failing)
        repo_fixable = sum(1 for f in repo_failing if f.fix_available)
        repo_by_sev = {
            "required": sum(1 for f in repo_failing if f.severity == "required"),
            "recommended": sum(1 for f in repo_failing if f.severity == "recommended"),
            "optional": sum(1 for f in repo_failing if f.severity == "optional"),
        }
        failing_ids.update(repo_failing_ids)
        fixable_ids.update(f.rule_id for f in repo_failing if f.fix_available)
        repos.append(
            {
                "path": rel,
                "stack": result.stack,
                "score": result.score,
                "status": "ok",
                "failing_rule_ids": repo_failing_ids,
                "failing_by_severity": repo_by_sev,
                "fixable_count": repo_fixable,
            }
        )
    rules_in_scan: list[dict[str, Any]] = []
    for rid in sorted(failing_ids):
        rule = rules_by_id.get(rid)
        if rule is None:
            continue
        rules_in_scan.append(
            {
                "id": rule.id,
                "severity": rule.severity,
                "title": rule.title,
                "fixable": rid in fixable_ids,
            }
        )
    payload: dict[str, Any] = {
        "schema_version": _SCHEMA_VERSION,
        "root": str(scan.root),
        "timestamp": scan.timestamp.isoformat(),
        "scan_count": len(scan.reports),
        "repos": repos,
        "rules_in_scan": rules_in_scan,
    }
    return json.dumps(payload, indent=2, sort_keys=False)
