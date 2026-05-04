"""Snapshot persistence for report scans."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from suzerain.audit.output.report_json import render_report_json
from suzerain.commands.report import PortfolioReport

DEFAULT_SNAPSHOT_DIRNAME = ".suzerain/snapshots"


def default_snapshot_dir(root: Path) -> Path:
    """Return the default snapshot directory for ``root`` (`<root>/.suzerain/snapshots/`)."""
    return root / DEFAULT_SNAPSHOT_DIRNAME


def snapshot_filename(root: Path, timestamp: datetime) -> str:
    """Return the snapshot filename: `<root-basename>-YYYY-MM-DDTHHMMSS.json`."""
    ts = timestamp.strftime("%Y-%m-%dT%H%M%S")
    return f"{root.name}-{ts}.json"


def save_snapshot(scan: PortfolioReport, snapshot_dir: Path) -> Path:
    """Serialize the scan as JSON and write it to the snapshot directory.

    Creates the directory if missing. Returns the path of the written file.
    """
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    fname = snapshot_filename(scan.root, scan.timestamp)
    target = snapshot_dir / fname
    target.write_text(render_report_json(scan))
    return target


def load_snapshot(path: Path) -> dict:  # type: ignore[type-arg]
    """Load and parse a snapshot file; returns the parsed JSON dict."""
    return json.loads(path.read_text())


def find_latest_snapshot(snapshot_dir: Path, root: Path) -> Path | None:
    """Return the most-recent snapshot for ``root`` in ``snapshot_dir``, or None."""
    if not snapshot_dir.is_dir():
        return None
    prefix = f"{root.name}-"
    candidates = sorted(p for p in snapshot_dir.glob(f"{prefix}*.json") if p.is_file())
    return candidates[-1] if candidates else None


def load_snapshot_as_portfolio_report(path: Path) -> PortfolioReport:
    """Reconstruct a stub PortfolioReport from a saved JSON snapshot.

    The reconstructed Report objects contain just enough fields for rendering:
    each ``failing_rule_ids`` entry becomes a Finding with status='fail'. Severity
    per finding is looked up from the rule registry (``collect_rules``); if a
    rule_id is not registered (e.g. dropped between snapshot and current run),
    severity defaults to 'recommended' to stay safe.

    A repo with status='error' is reconstructed as an Exception in the report
    tuple, mirroring the live-scan shape.

    Raises ValueError on unknown schema_version.
    """
    from datetime import datetime

    from suzerain.audit.registry import collect_rules
    from suzerain.core.report import Finding, Report

    data = json.loads(path.read_text())
    schema_version = data.get("schema_version")
    if schema_version != "2":
        raise ValueError(f"unsupported snapshot schema_version: {schema_version!r} (expected '2')")
    root = Path(data["root"])
    ts_str = data["timestamp"]
    timestamp = datetime.fromisoformat(ts_str) if "T" in ts_str else datetime.now()

    severity_by_id = {r.id: r.severity for r in collect_rules()}

    reports: list[tuple[Path, Report | Exception]] = []
    for entry in data["repos"]:
        rel = entry["path"]
        repo_path = root / rel if rel != "." else root
        if entry["status"] == "error":
            reports.append((repo_path, RuntimeError(entry.get("error", "unknown error"))))
            continue
        findings: list[Finding] = []
        for rid in entry.get("failing_rule_ids", []):
            severity = severity_by_id.get(rid, "recommended")
            findings.append(
                Finding(
                    rule_id=rid,
                    severity=severity,  # type: ignore[arg-type]
                    status="fail",
                    evidence="(reconstructed from snapshot)",
                    fix_available=False,
                )
            )
        report = Report(
            repo_path=repo_path,
            stacks=tuple(entry.get("stacks") or ()),
            mode=entry.get("mode") or "auto",
            findings=findings,
            score_override=entry.get("score"),
        )
        reports.append((repo_path, report))

    return PortfolioReport(root=root, reports=reports, timestamp=timestamp)
