"""Rule abstract base class and CheckResult dataclass."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import ClassVar, Literal

from suzerain.core.repo import Repo


@dataclass(frozen=True)
class CheckResult:
    """Outcome of running a Rule against a Repo."""

    passing: bool
    evidence: str = ""


class Rule(ABC):
    """Abstract base class for all suzerain rules.

    Subclasses MUST set the class-level metadata (`id`, `title`, etc.)
    and implement `check`. They MAY override `fix` (default returns None).
    """

    id: ClassVar[str]
    title: ClassVar[str]
    severity: ClassVar[Literal["required", "recommended", "optional"]]
    stacks: ClassVar[tuple[str, ...]]
    handbook_ref: ClassVar[str]
    adr_ref: ClassVar[str | None] = None
    template_ref: ClassVar[str | None] = None

    def applies(self, repo: Repo) -> bool:
        return "*" in self.stacks or repo.stack in self.stacks

    @abstractmethod
    def check(self, repo: Repo) -> CheckResult: ...

    def fix(self, repo: Repo, result: CheckResult) -> Patch | None:  # noqa: F821
        """Default: no auto-fix. Subclasses override to provide one."""
        return None
