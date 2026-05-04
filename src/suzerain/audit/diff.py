"""Compute and render the diff between two report scans."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class PortfolioDiff:
    """Result of comparing two report scans (current vs previous)."""

    current: dict[str, Any]  # the current report JSON dict
    previous: dict[str, Any]  # the previous report JSON dict
    previous_path: str  # absolute path of the previous snapshot file

    @property
    def score_changes(self) -> list[dict[str, Any]]:
        """Per-repo score deltas. Includes 'no change' entries for parity."""
        prev_by_path = {r["path"]: r for r in self.previous.get("repos", [])}
        out: list[dict[str, Any]] = []
        for repo in self.current.get("repos", []):
            path = repo["path"]
            if path not in prev_by_path:
                continue
            before = prev_by_path[path].get("score")
            after = repo.get("score")
            if before is None or after is None:
                continue
            out.append(
                {
                    "path": path,
                    "before": before,
                    "after": after,
                    "delta": after - before,
                }
            )
        return out

    @property
    def new_failures(self) -> list[dict[str, Any]]:
        """Rules failing now that were passing (or absent) previously."""
        prev_by_path = {r["path"]: r for r in self.previous.get("repos", [])}
        out: list[dict[str, Any]] = []
        sev_map = self._severity_map()
        for repo in self.current.get("repos", []):
            path = repo["path"]
            cur_failing = set(repo.get("failing_rule_ids", []))
            prev_failing = set(prev_by_path.get(path, {}).get("failing_rule_ids", []))
            for rid in sorted(cur_failing - prev_failing):
                out.append(
                    {
                        "path": path,
                        "rule_id": rid,
                        "severity": sev_map.get(rid, "unknown"),
                    }
                )
        return out

    @property
    def resolved_failures(self) -> list[dict[str, Any]]:
        """Rules previously failing that now pass."""
        prev_by_path = {r["path"]: r for r in self.previous.get("repos", [])}
        out: list[dict[str, Any]] = []
        sev_map = self._severity_map()
        for repo in self.current.get("repos", []):
            path = repo["path"]
            cur_failing = set(repo.get("failing_rule_ids", []))
            prev_failing = set(prev_by_path.get(path, {}).get("failing_rule_ids", []))
            for rid in sorted(prev_failing - cur_failing):
                out.append(
                    {
                        "path": path,
                        "rule_id": rid,
                        "severity": sev_map.get(rid, "unknown"),
                    }
                )
        return out

    @property
    def new_repos(self) -> list[str]:
        """Repos present in current but not in previous."""
        prev_paths = {r["path"] for r in self.previous.get("repos", [])}
        return sorted(
            r["path"] for r in self.current.get("repos", []) if r["path"] not in prev_paths
        )

    @property
    def removed_repos(self) -> list[str]:
        """Repos present in previous but not in current."""
        cur_paths = {r["path"] for r in self.current.get("repos", [])}
        return sorted(
            r["path"] for r in self.previous.get("repos", []) if r["path"] not in cur_paths
        )

    @property
    def has_new_required_failure(self) -> bool:
        """True if at least one new required-severity failure appeared."""
        return any(f["severity"] == "required" for f in self.new_failures)

    def _severity_map(self) -> dict[str, str]:
        """Build rule_id -> severity map from current + previous rules_in_scan sections."""
        m: dict[str, str] = {}
        for r in self.previous.get("rules_in_scan", []):
            m[r["id"]] = r["severity"]
        for r in self.current.get("rules_in_scan", []):
            m[r["id"]] = r["severity"]
        return m


def compute_diff(
    current: dict[str, Any], previous: dict[str, Any], previous_path: str
) -> PortfolioDiff:
    """Build a PortfolioDiff from two parsed report JSON dicts."""
    return PortfolioDiff(current=current, previous=previous, previous_path=previous_path)
