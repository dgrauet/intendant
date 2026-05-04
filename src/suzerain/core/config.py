"""Parser for .suzerain.toml — per-repo governance configuration."""

from __future__ import annotations

import re
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

from suzerain.core.subproject import Subproject

DEFAULT_MODE: Literal["advisory"] = "advisory"

_SUBPROJECT_NAME_RE = re.compile(r"^[a-zA-Z0-9_-]+$")


@dataclass(frozen=True)
class Exemption:
    """A user-declared exemption for a single rule."""

    reason: str
    until: str | None = None  # ISO date "YYYY-MM-DD"


@dataclass(frozen=True)
class SuzerainConfig:
    """Parsed .suzerain.toml content.

    ``stack`` is the user's manual pin, or ``None`` to leave detection to
    ``detect_stacks``. ``mode`` is the audit-mode (strict/recommended/advisory),
    *not* the stack-resolution mode (auto/manual) — that distinction lives on
    ``Repo``.
    """

    version: str
    stack: str | None
    mode: Literal["strict", "recommended", "advisory"]
    subprojects: list[Subproject] = field(default_factory=list)
    exemptions: dict[str, Exemption] = field(default_factory=dict)
    subproject_exemptions: dict[str, dict[str, Exemption]] = field(default_factory=dict)

    def is_rule_exempt(self, rule_id: str) -> bool:
        return rule_id in self.exemptions

    def is_rule_exempt_for_subproject(
        self, rule_id: str, subproject_name: str | None
    ) -> Exemption | None:
        """Return the matching Exemption (or None).

        Resolution order: subproject-scoped > top-level.
        """
        if subproject_name is not None:
            scoped = self.subproject_exemptions.get(subproject_name, {}).get(rule_id)
            if scoped is not None:
                return scoped
        return self.exemptions.get(rule_id)


def load_config(repo_path: Path) -> SuzerainConfig:
    """Load .suzerain.toml from `repo_path`. Returns defaults if no file.

    ``stack = "auto"`` (legacy sentinel) is treated as no pin (``None``).
    """
    cfg_path = repo_path / ".suzerain.toml"
    if not cfg_path.is_file():
        return SuzerainConfig(version="1", stack=None, mode=DEFAULT_MODE)
    raw = tomllib.loads(cfg_path.read_text())
    suz = raw.get("suzerain", {})
    raw_exemptions = raw.get("exemptions", {})
    exemptions = _parse_exemptions(raw_exemptions)
    subprojects = _parse_subprojects(raw.get("subprojects", []))
    subproject_exemptions = _parse_subproject_exemptions(raw_exemptions)
    raw_stack = suz.get("stack")
    stack = None if raw_stack in (None, "auto") else str(raw_stack)
    return SuzerainConfig(
        version=str(suz.get("version", "1")),
        stack=stack,
        mode=suz.get("mode", DEFAULT_MODE),
        subprojects=subprojects,
        exemptions=exemptions,
        subproject_exemptions=subproject_exemptions,
    )


def _parse_exemptions(raw: dict) -> dict[str, Exemption]:
    """Parse top-level exemptions.

    Heuristic: a value that is a dict with a `reason` key is a single Exemption
    (e.g., RULE001 = {reason = "...", until = "..."}). A value that is a dict
    WITHOUT `reason` is a scoped sub-table (e.g., [exemptions.backend]) and
    handled by `_parse_subproject_exemptions`.
    """
    out: dict[str, Exemption] = {}
    for rule_id, value in raw.items():
        if isinstance(value, str):
            out[rule_id] = Exemption(reason=value)
        elif isinstance(value, dict) and "reason" in value:
            out[rule_id] = Exemption(
                reason=str(value.get("reason", "")),
                until=value.get("until"),
            )
    return out


def _parse_subproject_exemptions(raw: dict) -> dict[str, dict[str, Exemption]]:
    """Parse [exemptions.<subproject_name>] sub-tables."""
    out: dict[str, dict[str, Exemption]] = {}
    for key, value in raw.items():
        if not isinstance(value, dict):
            continue
        # If it has a `reason` key, it's a single Exemption (handled elsewhere)
        if "reason" in value:
            continue
        # Scoped block: every entry is rule_id -> Exemption-spec
        scoped: dict[str, Exemption] = {}
        for rule_id, rule_value in value.items():
            if isinstance(rule_value, str):
                scoped[rule_id] = Exemption(reason=rule_value)
            elif isinstance(rule_value, dict):
                scoped[rule_id] = Exemption(
                    reason=str(rule_value.get("reason", "")),
                    until=rule_value.get("until"),
                )
        if scoped:
            out[key] = scoped
    return out


def _parse_subprojects(raw: list) -> list[Subproject]:
    """Parse [[subprojects]] array. Validates all required fields and constraints."""
    if not isinstance(raw, list):
        return []
    out: list[Subproject] = []
    seen_names: set[str] = set()
    seen_paths: set[str] = set()
    for entry in raw:
        if not isinstance(entry, dict):
            continue
        if "path" not in entry:
            raise ValueError("subproject missing required field: path")
        if "stack" not in entry:
            raise ValueError("subproject missing required field: stack")
        path = str(entry["path"])
        stack = str(entry["stack"])
        if path.startswith("/"):
            raise ValueError(f"subproject path must be relative: {path!r}")
        if ".." in Path(path).parts:
            raise ValueError(f"subproject path must not contain '..': {path!r}")
        # Resolve default name
        if "name" in entry:
            name = str(entry["name"])
        elif path == ".":
            name = "root"
        else:
            name = Path(path).name
        if not _SUBPROJECT_NAME_RE.match(name):
            raise ValueError(f"subproject name must match [a-zA-Z0-9_-]+: {name!r}")
        if name in seen_names:
            raise ValueError(f"duplicate subproject name: {name}")
        if path in seen_paths:
            raise ValueError(f"duplicate subproject path: {path}")
        seen_names.add(name)
        seen_paths.add(path)
        out.append(Subproject(name=name, path=path, stack=stack))
    return out
