"""Go adapter — language-specific rules."""

from intendant.adapters.go.ci import GO_CI001MinimumSteps
from intendant.adapters.go.pk import GoMod, GoSum, GoVersion
from intendant.adapters.go.qu import GoLinter
from intendant.adapters.go.sa import GO_SA001GitignoreBaseline
from intendant.adapters.go.ts import GoTestFiles
from intendant.core.rule import Rule

RULES: list[Rule] = [
    GoMod(),
    GoSum(),
    GoVersion(),
    GoLinter(),
    GoTestFiles(),
    GO_CI001MinimumSteps(),
    GO_SA001GitignoreBaseline(),
]
