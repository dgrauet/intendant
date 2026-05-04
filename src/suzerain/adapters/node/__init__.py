"""Node adapter — language-specific rules."""

from suzerain.adapters.node.ci import NODE_CI001MinimumSteps
from suzerain.adapters.node.pk import NodeEnginesNode, NodeLockfile, NodePackageJson
from suzerain.adapters.node.qu import NodeLinter, NodeTypeScript
from suzerain.adapters.node.sa import NODE_SA001GitignoreBaseline
from suzerain.adapters.node.ts import NodeTestFramework
from suzerain.core.rule import Rule

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
