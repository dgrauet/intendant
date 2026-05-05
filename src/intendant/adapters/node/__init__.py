"""Node adapter — language-specific rules."""

from intendant.adapters.node.ci import NODE_CI001MinimumSteps
from intendant.adapters.node.pk import NodeEnginesNode, NodeLockfile, NodePackageJson
from intendant.adapters.node.qu import NodeLinter, NodeTypeScript
from intendant.adapters.node.sa import NODE_SA001GitignoreBaseline
from intendant.adapters.node.ts import NodeTestFramework
from intendant.core.rule import Rule

RULES: list[Rule] = [
    NodePackageJson(),
    NodeLockfile(),
    NodeEnginesNode(),
    NodeLinter(),
    NodeTypeScript(),
    NodeTestFramework(),
    NODE_CI001MinimumSteps(),
    NODE_SA001GitignoreBaseline(),
]
