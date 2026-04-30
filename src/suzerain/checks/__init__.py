"""Transverse rules — applied to all stacks."""

from suzerain.checks.dg import DG001Readme, DG003ADRDir, DG004License, DG005SpecsLocalOnly
from suzerain.core.rule import Rule

RULES: list[Rule] = [
    DG001Readme(),
    DG003ADRDir(),
    DG004License(),
    DG005SpecsLocalOnly(),
]
