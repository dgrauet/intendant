"""Swift adapter — language-specific rules."""

from suzerain.adapters.swift.ci import SWIFT_CI001MinimumSteps
from suzerain.adapters.swift.pk import SwiftPackage, SwiftResolved, SwiftToolsVersion
from suzerain.adapters.swift.qu import SwiftLinter
from suzerain.adapters.swift.sa import SWIFT_SA001GitignoreBaseline
from suzerain.adapters.swift.ts import SwiftTestFiles
from suzerain.core.rule import Rule

RULES: list[Rule] = [
    SwiftPackage(),
    SwiftResolved(),
    SwiftToolsVersion(),
    SwiftLinter(),
    SwiftTestFiles(),
    SWIFT_CI001MinimumSteps(),
    SWIFT_SA001GitignoreBaseline(),
]
