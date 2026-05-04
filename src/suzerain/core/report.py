"""Finding and Report dataclasses."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

_SEVERITY_WEIGHT = {"required": 10, "recommended": 3, "optional": 1}


@dataclass(frozen=True)
class Finding:
    """One outcome of running a single Rule against a Repo."""

    rule_id: str
    severity: Literal["required", "recommended", "optional"]
    status: Literal["pass", "fail", "skip", "exempt"]
    evidence: str
    fix_available: bool
    fix_preview: str | None = None
    subproject: str | None = None  # subproject name; None for transverse findings


@dataclass(frozen=True)
class Report:
    """Aggregate result of an audit run on a Repo."""

    repo_path: Path
    stack: str
    findings: list[Finding] = field(default_factory=list)
    score_override: int | None = None

    @property
    def score(self) -> int:
        """Weighted 0-100 score. Skipped rules excluded; exempt counted as pass."""
        if self.score_override is not None:
            return self.score_override
        relevant = [f for f in self.findings if f.status != "skip"]
        if not relevant:
            return 100
        total = sum(_SEVERITY_WEIGHT[f.severity] for f in relevant)
        passing = sum(
            _SEVERITY_WEIGHT[f.severity] for f in relevant if f.status in ("pass", "exempt")
        )
        return round(passing / total * 100)

    @property
    def passing(self) -> int:
        return sum(1 for f in self.findings if f.status == "pass")

    @property
    def failing(self) -> int:
        return sum(1 for f in self.findings if f.status == "fail")

    @property
    def exempt(self) -> int:
        return sum(1 for f in self.findings if f.status == "exempt")

    @property
    def skipped(self) -> int:
        return sum(1 for f in self.findings if f.status == "skip")

    @property
    def fixable(self) -> int:
        return sum(1 for f in self.findings if f.status == "fail" and f.fix_available)
