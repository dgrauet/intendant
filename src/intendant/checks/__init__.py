"""Transverse rules — applied to all stacks."""

from intendant.checks.ci import (
    CI001CIWorkflow,
    CI003CommitMessageValidation,
    CI004CacheConfigured,
)
from intendant.checks.dg import (
    DG001Readme,
    DG002CLAUDEmd,
    DG003ADRDir,
    DG004License,
    DG005SpecsLocalOnly,
)
from intendant.checks.lo import LO003DocsDirectory
from intendant.checks.rl import (
    RL001Changelog,
    RL002ConventionalCommits,
    RL003ReleasePlease,
    RL004SemverStrict,
)
from intendant.checks.rl005 import RL005BranchProtection
from intendant.checks.sa import (
    SA001PreCommit,
    SA002Gitleaks,
    SA003EnvExample,
    SA004GitignoreBaseline,
)
from intendant.checks.ts import TS002RegressionTestsLayout
from intendant.core.rule import Rule

RULES: list[Rule] = [
    DG001Readme(),
    DG002CLAUDEmd(),
    DG003ADRDir(),
    DG004License(),
    DG005SpecsLocalOnly(),
    LO003DocsDirectory(),
    RL001Changelog(),
    RL002ConventionalCommits(),
    RL003ReleasePlease(),
    RL004SemverStrict(),
    RL005BranchProtection(),
    TS002RegressionTestsLayout(),
    CI001CIWorkflow(),
    CI003CommitMessageValidation(),
    CI004CacheConfigured(),
    SA001PreCommit(),
    SA002Gitleaks(),
    SA003EnvExample(),
    SA004GitignoreBaseline(),
]
