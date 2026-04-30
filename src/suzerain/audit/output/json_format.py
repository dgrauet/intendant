"""Render a Report to JSON."""

from __future__ import annotations

import json
from dataclasses import asdict

from suzerain.core.report import Report


def render_json(report: Report) -> str:
    """Serialize report to JSON. Suitable for CI pipelines and aggregation."""
    payload = {
        "repo_path": str(report.repo_path),
        "stack": report.stack,
        "score": report.score,
        "summary": {
            "passing": report.passing,
            "failing": report.failing,
            "exempt": report.exempt,
            "skipped": report.skipped,
            "fixable": report.fixable,
        },
        "findings": [asdict(f) for f in report.findings],
    }
    return json.dumps(payload, indent=2, sort_keys=False)
