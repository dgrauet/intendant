"""Sub-project declaration for multi-language repos."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Subproject:
    """A declared sub-project within a multi-subproject repository."""

    name: str
    path: str  # repo-relative; "." means root
    stack: str  # one of the supported stacks: python | node | claude-skill | rust | go | swift
