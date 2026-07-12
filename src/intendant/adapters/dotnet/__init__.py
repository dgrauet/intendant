""".NET adapter — language-specific rules."""

from intendant.adapters.dotnet.ci import DOTNET_CI001MinimumSteps
from intendant.adapters.dotnet.pk import DotnetLockfile, DotnetProject
from intendant.adapters.dotnet.qu import DotnetEditorconfig, DotnetNullable
from intendant.adapters.dotnet.sa import DOTNET_SA001GitignoreBaseline
from intendant.adapters.dotnet.ts import DotnetTestProject
from intendant.core.rule import Rule

RULES: list[Rule] = [
    DotnetProject(),
    DotnetLockfile(),
    DotnetNullable(),
    DotnetEditorconfig(),
    DotnetTestProject(),
    DOTNET_CI001MinimumSteps(),
    DOTNET_SA001GitignoreBaseline(),
]
