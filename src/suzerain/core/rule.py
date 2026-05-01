"""Rule abstract base class and CheckResult dataclass."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import ClassVar, Literal

from suzerain.core.patch import Patch
from suzerain.core.repo import Repo


@dataclass(frozen=True)
class CheckResult:
    """Outcome of running a Rule against a Repo."""

    passing: bool
    evidence: str = ""
    skipped: bool = False


class Rule(ABC):
    """Abstract base class for all suzerain rules."""

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

    def fix(self, repo: Repo, result: CheckResult) -> Patch | None:
        """Default: no auto-fix. Subclasses override to provide one."""
        return None
