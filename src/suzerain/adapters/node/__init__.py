"""Node adapter — language-specific rules."""

from suzerain.adapters.node.pk import NodeEnginesNode, NodeLockfile, NodePackageJson
from suzerain.adapters.node.qu import NodeLinter, NodeTypeScript
from suzerain.adapters.node.ts import NodeTestFramework
from suzerain.core.rule import Rule

RULES: list[Rule] = [
    NodePackageJson(),
    NodeLockfile(),
    NodeEnginesNode(),
    NodeLinter(),
    NodeTypeScript(),
    NodeTestFramework(),
]
