"""Go adapter — language-specific rules."""

from suzerain.adapters.go.ci import GO_CI001MinimumSteps
from suzerain.adapters.go.pk import GoMod, GoSum, GoVersion
from suzerain.adapters.go.qu import GoLinter
from suzerain.adapters.go.sa import GO_SA001GitignoreBaseline
from suzerain.adapters.go.ts import GoTestFiles
from suzerain.core.rule import Rule

RULES: list[Rule] = [
    GoMod(),
    GoSum(),
    GoVersion(),
    GoLinter(),
    GoTestFiles(),
    GO_CI001MinimumSteps(),
    GO_SA001GitignoreBaseline(),
]
