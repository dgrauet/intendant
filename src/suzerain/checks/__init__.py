"""Transverse rules — applied to all stacks."""

from suzerain.checks.ci import CI001CIWorkflow, CI004CacheConfigured
from suzerain.checks.dg import (
    DG001Readme,
    DG002CLAUDEmd,
    DG003ADRDir,
    DG004License,
    DG005SpecsLocalOnly,
)
from suzerain.checks.rl import RL001Changelog, RL002ConventionalCommits, RL003ReleasePlease
from suzerain.checks.sa import SA001PreCommit, SA002Gitleaks, SA004GitignoreBaseline
from suzerain.core.rule import Rule

RULES: list[Rule] = [
    DG001Readme(),
    DG002CLAUDEmd(),
    DG003ADRDir(),
    DG004License(),
    DG005SpecsLocalOnly(),
    RL001Changelog(),
    RL002ConventionalCommits(),
    RL003ReleasePlease(),
    CI001CIWorkflow(),
    CI004CacheConfigured(),
    SA001PreCommit(),
    SA002Gitleaks(),
    SA004GitignoreBaseline(),
]
