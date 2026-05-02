"""Rule registry — discovers rules and filters them for a target repo."""

from __future__ import annotations

from collections.abc import Sequence

from suzerain.core.config import SuzerainConfig
from suzerain.core.repo import Repo
from suzerain.core.rule import Rule


def collect_rules() -> list[Rule]:
    """Discover all registered rules.

    For palier 2 we collect by importing the known modules and instantiating
    every Rule subclass. Adapters and checks register their rules through
    their module's `RULES` constant.
    """
    rules: list[Rule] = []
    try:
        from suzerain.checks import RULES

        rules.extend(RULES)
    except ImportError:
        pass
    try:
        from suzerain.adapters.python import RULES

        rules.extend(RULES)
    except ImportError:
        pass
    try:
        from suzerain.adapters.claude_skill import RULES

        rules.extend(RULES)
    except ImportError:
        pass
    return rules


def filter_for_repo(rules: Sequence[Rule], repo: Repo, config: SuzerainConfig) -> list[Rule]:
    """Return the subset of rules that apply to the repo under the given mode.

    - Mode `recommended` excludes `optional` severity.
    - Mode `advisory` keeps everything (reporting only).
    - Mode `strict` keeps everything.
    Stack filtering: a rule applies if its `stacks` includes "*" or the
    repo's stack.
    Exemptions are NOT removed here; the runner marks them as exempt.
    """
    applicable = [r for r in rules if r.applies(repo)]
    if config.mode == "recommended":
        applicable = [r for r in applicable if r.severity != "optional"]
    return applicable
