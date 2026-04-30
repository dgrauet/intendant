"""Python adapter — language-specific rules."""

from suzerain.adapters.python.lo import LO001SrcLayout, LO002TestsAtRoot
from suzerain.adapters.python.pk import PK001PyprojectExists, PK002UvLock, PK003PythonVersion
from suzerain.core.rule import Rule

RULES: list[Rule] = [
    LO001SrcLayout(),
    LO002TestsAtRoot(),
    PK001PyprojectExists(),
    PK002UvLock(),
    PK003PythonVersion(),
]
