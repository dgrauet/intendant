"""Python adapter — language-specific rules."""

from suzerain.adapters.python.lo import LO001SrcLayout, LO002TestsAtRoot
from suzerain.adapters.python.pk import (
    PK001PyprojectExists,
    PK002UvLock,
    PK003PythonVersion,
    PK004NoRequirementsTxt,
)
from suzerain.adapters.python.qu import QU001Ruff, QU002Ty
from suzerain.adapters.python.ts import TS001Pytest, TS003CoverageConfigured
from suzerain.core.rule import Rule

RULES: list[Rule] = [
    LO001SrcLayout(),
    LO002TestsAtRoot(),
    PK001PyprojectExists(),
    PK002UvLock(),
    PK003PythonVersion(),
    PK004NoRequirementsTxt(),
    QU001Ruff(),
    QU002Ty(),
    TS001Pytest(),
    TS003CoverageConfigured(),
]
