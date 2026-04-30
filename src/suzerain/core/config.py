"""Parser for .suzerain.toml — per-repo governance configuration."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

DEFAULT_MODE: Literal["advisory"] = "advisory"


@dataclass(frozen=True)
class Exemption:
    """A user-declared exemption for a single rule."""

    reason: str
    until: str | None = None  # ISO date "YYYY-MM-DD"


@dataclass(frozen=True)
class SuzerainConfig:
    """Parsed .suzerain.toml content."""

    version: str
    stack: str
    mode: Literal["strict", "recommended", "advisory"]
    exemptions: dict[str, Exemption] = field(default_factory=dict)

    def is_rule_exempt(self, rule_id: str) -> bool:
        return rule_id in self.exemptions


def load_config(repo_path: Path) -> SuzerainConfig:
    """Load .suzerain.toml from `repo_path`. Returns defaults if no file."""
    cfg_path = repo_path / ".suzerain.toml"
    if not cfg_path.is_file():
        return SuzerainConfig(version="1", stack="auto", mode=DEFAULT_MODE)
    raw = tomllib.loads(cfg_path.read_text())
    suz = raw.get("suzerain", {})
    exemptions = _parse_exemptions(raw.get("exemptions", {}))
    return SuzerainConfig(
        version=str(suz.get("version", "1")),
        stack=str(suz.get("stack", "auto")),
        mode=suz.get("mode", DEFAULT_MODE),
        exemptions=exemptions,
    )


def _parse_exemptions(raw: dict) -> dict[str, Exemption]:
    out: dict[str, Exemption] = {}
    for rule_id, value in raw.items():
        if isinstance(value, str):
            out[rule_id] = Exemption(reason=value)
        elif isinstance(value, dict):
            out[rule_id] = Exemption(
                reason=str(value.get("reason", "")),
                until=value.get("until"),
            )
    return out
