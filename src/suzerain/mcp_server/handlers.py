"""MCP tool handlers — plain-Python entry points returning JSON-friendly dicts.

These functions are the testable layer underneath the FastMCP wrappers in
:mod:`suzerain.mcp_server.server`. Each returns either a successful payload
or `{"error": "<message>"}` — never raises for expected user-facing failures.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from suzerain.audit.diff import compute_diff
from suzerain.audit.output.json_format import _build_payload
from suzerain.audit.output.report_json import render_report_json
from suzerain.audit.registry import collect_rules, filter_for_repo
from suzerain.audit.runner import resolve_repo, run_audit
from suzerain.audit.snapshot import find_latest_snapshot, load_snapshot
from suzerain.core.config import load_config
from suzerain.core.handbook import Handbook
from suzerain.core.paths import docs_root

_VALID_SEVERITIES = ("required", "recommended", "optional")


def _err(msg: str) -> dict[str, Any]:
    return {"error": msg}


def _resolve_existing_dir(path_str: str) -> Path | None:
    p = Path(path_str).expanduser()
    if not p.exists() or not p.is_dir():
        return None
    return p.resolve()


def audit_repo(path: str, severity: str | None = None) -> dict[str, Any]:
    """Audit a single repo. Returns the same JSON shape as `suzerain audit --format=json`.

    `severity`, when provided, filters returned findings to that severity only
    (must be one of "required", "recommended", "optional").
    """
    if severity is not None and severity not in _VALID_SEVERITIES:
        return _err(f"invalid severity {severity!r}; expected one of {list(_VALID_SEVERITIES)}")
    repo_path = _resolve_existing_dir(path)
    if repo_path is None:
        return _err(f"path not found or not a directory: {path}")
    try:
        config = load_config(repo_path)
        repo = resolve_repo(repo_path, config)
        all_rules = collect_rules()
        rules = all_rules if config.subprojects else filter_for_repo(all_rules, repo, config)
        report = run_audit(repo, config, rules)
    except Exception as exc:
        return _err(f"{type(exc).__name__}: {exc}")
    payload = _build_payload(report)
    if severity is not None:
        payload["findings"] = [f for f in payload.get("findings", []) if f["severity"] == severity]
    return payload


def explain_rule(rule_id: str) -> dict[str, Any]:
    """Return the handbook section for a rule (id, title, severity, body, stacks, adr)."""
    try:
        handbook = Handbook(docs_root())
    except FileNotFoundError as exc:
        return _err(str(exc))
    section = handbook.get_rule(rule_id)
    if section is None:
        return _err(f"unknown rule_id: {rule_id}")
    return {
        "rule_id": section.rule_id,
        "title": section.title,
        "severity": section.severity,
        "stacks": list(section.stacks),
        "adr_ref": section.adr_ref,
        "body": section.body,
    }


def list_rules(stack: str | None = None, severity: str | None = None) -> dict[str, Any]:
    """List registered rules, optionally filtered by stack and/or severity."""
    if severity is not None and severity not in _VALID_SEVERITIES:
        return _err(f"invalid severity {severity!r}; expected one of {list(_VALID_SEVERITIES)}")
    rules = collect_rules()
    out: list[dict[str, Any]] = []
    for rule in rules:
        if severity is not None and rule.severity != severity:
            continue
        if stack is not None and stack not in rule.stacks and "*" not in rule.stacks:
            continue
        out.append(
            {
                "id": rule.id,
                "title": rule.title,
                "severity": rule.severity,
                "stacks": list(rule.stacks),
                "fixable": rule.supports_fix(),
            }
        )
    out.sort(key=lambda r: r["id"])
    return {"count": len(out), "rules": out}


def report_portfolio(path: str, maxdepth: int = 2) -> dict[str, Any]:
    """Scan a portfolio root and return the same JSON as `suzerain report --format=json`."""
    root = _resolve_existing_dir(path)
    if root is None:
        return _err(f"path not found or not a directory: {path}")
    try:
        # Lazy import to avoid circular: report imports from this module's siblings
        from suzerain.commands.report import _scan_all

        scan = _scan_all(root, maxdepth=maxdepth)
        return json.loads(render_report_json(scan))
    except Exception as exc:
        return _err(f"{type(exc).__name__}: {exc}")


def diff_portfolio(path: str, against: str | None = None, maxdepth: int = 2) -> dict[str, Any]:
    """Diff the current portfolio scan against a snapshot.

    If `against` is None, looks up the latest snapshot in `<path>/.suzerain/snapshots/`.
    Returns sections: score_changes, new_failures, resolved_failures, new_repos, removed_repos.
    """
    root = _resolve_existing_dir(path)
    if root is None:
        return _err(f"path not found or not a directory: {path}")
    if against is not None:
        snapshot_path = Path(against).expanduser()
        if not snapshot_path.is_file():
            return _err(f"snapshot file not found: {against}")
    else:
        snapshot_dir = root / ".suzerain" / "snapshots"
        snapshot_path = find_latest_snapshot(snapshot_dir, root) if snapshot_dir.is_dir() else None
        if snapshot_path is None:
            return _err(
                f"no snapshot found under {snapshot_dir}; "
                "run `suzerain report --save-snapshot` first or pass `against`"
            )
    try:
        from suzerain.commands.report import _scan_all

        scan = _scan_all(root, maxdepth=maxdepth)
        current = json.loads(render_report_json(scan))
        previous = load_snapshot(snapshot_path)
        diff = compute_diff(current, previous, str(snapshot_path))
    except Exception as exc:
        return _err(f"{type(exc).__name__}: {exc}")
    return {
        "snapshot": str(snapshot_path),
        "score_changes": diff.score_changes,
        "new_failures": diff.new_failures,
        "resolved_failures": diff.resolved_failures,
        "new_repos": diff.new_repos,
        "removed_repos": diff.removed_repos,
    }
