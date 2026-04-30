"""Transverse rules — applied to all stacks."""

from suzerain.checks.ci import CI001CIWorkflow
from suzerain.checks.dg import DG001Readme, DG003ADRDir, DG004License, DG005SpecsLocalOnly
from suzerain.checks.rl import RL001Changelog, RL002ConventionalCommits
from suzerain.checks.sa import SA001PreCommit
from suzerain.core.rule import Rule

RULES: list[Rule] = [
    DG001Readme(),
    DG003ADRDir(),
    DG004License(),
    DG005SpecsLocalOnly(),
    RL001Changelog(),
    RL002ConventionalCommits(),
    CI001CIWorkflow(),
    SA001PreCommit(),
]
