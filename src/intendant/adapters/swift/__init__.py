"""Swift adapter — language-specific rules."""

from intendant.adapters.swift.ci import SWIFT_CI001MinimumSteps
from intendant.adapters.swift.pk import SwiftPackage, SwiftResolved, SwiftToolsVersion
from intendant.adapters.swift.qu import SwiftLinter
from intendant.adapters.swift.sa import SWIFT_SA001GitignoreBaseline
from intendant.adapters.swift.ts import SwiftTestFiles
from intendant.core.rule import Rule

RULES: list[Rule] = [
    SwiftPackage(),
    SwiftResolved(),
    SwiftToolsVersion(),
    SwiftLinter(),
    SwiftTestFiles(),
    SWIFT_CI001MinimumSteps(),
    SWIFT_SA001GitignoreBaseline(),
]
