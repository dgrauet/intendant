"""Python adapter — language-specific rules."""

from intendant.adapters.python.ci import PYTHON_CI001MinimumSteps
from intendant.adapters.python.lo import LO001SrcLayout, LO002TestsAtRoot
from intendant.adapters.python.pk import (
    PK001PyprojectExists,
    PK002UvLock,
    PK003PythonVersion,
    PK004NoRequirementsTxt,
)
from intendant.adapters.python.qu import (
    QU001Ruff,
    QU002Ty,
    QU003StrictTypeAnnotations,
    QU004TyCheck,
)
from intendant.adapters.python.sa import PYTHON_SA001GitignoreBaseline
from intendant.adapters.python.ts import TS001Pytest, TS003CoverageConfigured
from intendant.core.rule import Rule

RULES: list[Rule] = [
    LO001SrcLayout(),
    LO002TestsAtRoot(),
    PK001PyprojectExists(),
    PK002UvLock(),
    PK003PythonVersion(),
    PK004NoRequirementsTxt(),
    QU001Ruff(),
    QU002Ty(),
    QU003StrictTypeAnnotations(),
    QU004TyCheck(),
    TS001Pytest(),
    TS003CoverageConfigured(),
    PYTHON_CI001MinimumSteps(),
    PYTHON_SA001GitignoreBaseline(),
]
