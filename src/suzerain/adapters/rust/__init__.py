"""Rust adapter — language-specific rules."""

from suzerain.adapters.rust.ci import RUST_CI001MinimumSteps
from suzerain.adapters.rust.pk import RustCargoLock, RustCargoToml, RustEdition
from suzerain.adapters.rust.qu import RustToolchainPin
from suzerain.adapters.rust.sa import RUST_SA001GitignoreBaseline
from suzerain.adapters.rust.ts import RustTestAnnotations
from suzerain.core.rule import Rule

RULES: list[Rule] = [
    RustCargoToml(),
    RustCargoLock(),
    RustEdition(),
    RustToolchainPin(),
    RustTestAnnotations(),
    RUST_CI001MinimumSteps(),
    RUST_SA001GitignoreBaseline(),
]
