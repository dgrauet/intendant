"""Render a Report to JSON."""

from __future__ import annotations

import json

from intendant.core.report import Finding, Report


def render_json(report: Report) -> str:
    """Serialize report to JSON. Suitable for CI pipelines and aggregation."""
    payload = _build_payload(report)
    return json.dumps(payload, indent=2, sort_keys=False)


def _build_payload(report: Report) -> dict:  # type: ignore[type-arg]
    has_subprojects = any(f.subproject is not None for f in report.findings)
    base: dict = {  # type: ignore[type-arg]
        "schema_version": "2",
        "repo_path": str(report.repo_path),
        "stacks": list(report.stacks),
        "mode": report.mode,
        "score": report.score,
    }
    if not has_subprojects:
        base["findings"] = [_finding_to_dict(f) for f in report.findings]
    else:
        groups: dict[str | None, list[Finding]] = {}
        for f in report.findings:
            groups.setdefault(f.subproject, []).append(f)
        subprojects_list: list[dict] = []  # type: ignore[type-arg]
        if None in groups:
            subprojects_list.append(
                {
                    "name": "_global_",
                    "path": None,
                    "stack": "transverse",
                    "findings": [_finding_to_dict(f) for f in groups[None]],
                }
            )
        for name, findings in groups.items():
            if name is None:
                continue
            subprojects_list.append(
                {
                    "name": name,
                    "path": None,
                    "stack": None,
                    "findings": [_finding_to_dict(f) for f in findings],
                }
            )
        base["subprojects"] = subprojects_list
    base["summary"] = {
        "passing": report.passing,
        "failing": report.failing,
        "exempt": report.exempt,
        "skipped": report.skipped,
        "fixable": report.fixable,
    }
    return base


def _finding_to_dict(f: Finding) -> dict:  # type: ignore[type-arg]
    return {
        "rule_id": f.rule_id,
        "severity": f.severity,
        "status": f.status,
        "evidence": f.evidence,
        "fix_available": f.fix_available,
        "fix_preview": f.fix_preview,
    }
