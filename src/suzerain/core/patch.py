"""Patch dataclass and safe-apply primitives."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import tomli_w

PatchKind = Literal["create", "overwrite", "merge_toml"]


@dataclass(frozen=True)
class Patch:
    """A proposed change to one file in a repo.

    `safe=True` means apply_patch will write it. `safe=False` means it should
    only ever be deposited under .suzerain/proposed/ for human review.
    """

    target_path: Path
    kind: PatchKind
    content: str
    diff: str
    safe: bool


def apply_patch(patch: Patch) -> None:
    """Write a safe patch to disk. Raises ValueError if not safe."""
    if not patch.safe:
        raise ValueError(f"refusing to apply: patch for {patch.target_path} is not safe")
    target = patch.target_path
    target.parent.mkdir(parents=True, exist_ok=True)
    if patch.kind in ("create", "overwrite"):
        target.write_text(patch.content)
    elif patch.kind == "merge_toml":
        existing: dict = {}
        if target.is_file():
            existing = tomllib.loads(target.read_text())
        added = tomllib.loads(patch.content)
        merged = _deep_merge(existing, added)
        target.write_text(tomli_w.dumps(merged))
    else:  # pragma: no cover -- unreachable, Literal exhausts kinds
        raise ValueError(f"unknown patch kind: {patch.kind}")


def _deep_merge(base: dict, overlay: dict) -> dict:
    out = dict(base)
    for key, value in overlay.items():
        if key in out and isinstance(out[key], dict) and isinstance(value, dict):
            out[key] = _deep_merge(out[key], value)
        else:
            out[key] = value
    return out
