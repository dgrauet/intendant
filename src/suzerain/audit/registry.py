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
    try:
        from suzerain.adapters.node import RULES

        rules.extend(RULES)
    except ImportError:
        pass
    try:
        from suzerain.adapters.rust import RULES

        rules.extend(RULES)
    except ImportError:
        pass
    try:
        from suzerain.adapters.go import RULES

        rules.extend(RULES)
    except ImportError:
        pass
    try:
        from suzerain.adapters.swift import RULES

        rules.extend(RULES)
    except ImportError:
        pass
    return rules


def filter_for_repo(rules: Sequence[Rule], repo: Repo, config: SuzerainConfig) -> list[Rule]:
    """Return the subset of rules that apply to the repo under the given mode.

    Mode filtering:
    - `recommended` excludes `optional` severity.
    - `advisory` and `strict` keep everything.

    Stack scoping:
    - If `config.subprojects` is empty (single-Repo mode): keep every rule
      that applies to any stack in `repo.stacks` (transverse OR
      stack-specific).
    - If `config.subprojects` is non-empty AND `repo.name is None` (root
      meta-Repo pass): only transverse rules (`stacks=("*",)`).
    - If `config.subprojects` is non-empty AND `repo.name is not None`
      (subproject pass): only stack-specific rules matching `repo.stacks`
      (transverse excluded).

    Exemptions are NOT removed here; the runner marks them as exempt.
    """
    if repo.name is not None:
        # Subproject pass (named repo): only stack-specific rules matching this stack
        applicable = [r for r in rules if "*" not in r.stacks and r.applies(repo)]
    elif config.subprojects:
        # Root meta-Repo in multi-subproject mode (name=None, subprojects configured):
        # only transverse rules
        applicable = [r for r in rules if "*" in r.stacks]
    else:
        # Legacy single-Repo path (name=None, no subprojects): rule applies if its
        # stacks include "*" or repo.stack. Backward compat with the existing pipeline.
        applicable = [r for r in rules if r.applies(repo)]
    if config.mode == "recommended":
        applicable = [r for r in applicable if r.severity != "optional"]
    return applicable
