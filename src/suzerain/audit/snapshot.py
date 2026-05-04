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
