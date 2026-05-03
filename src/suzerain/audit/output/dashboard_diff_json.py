"""Render a PortfolioDiff to JSON."""

from __future__ import annotations

import json
from typing import Any

from suzerain.audit.diff import PortfolioDiff

_SCHEMA_VERSION = "1"


def render_diff_json(diff: PortfolioDiff) -> str:
    """Return the JSON-serialized representation of a portfolio diff."""
    payload: dict[str, Any] = {
        "schema_version": _SCHEMA_VERSION,
        "current": {
            "timestamp": diff.current.get("timestamp"),
            "root": diff.current.get("root"),
        },
        "previous": {
            "timestamp": diff.previous.get("timestamp"),
            "snapshot_file": diff.previous_path,
        },
        "score_changes": diff.score_changes,
        "new_failures": diff.new_failures,
        "resolved_failures": diff.resolved_failures,
        "new_repos": diff.new_repos,
        "removed_repos": diff.removed_repos,
    }
    return json.dumps(payload, indent=2, sort_keys=False)
