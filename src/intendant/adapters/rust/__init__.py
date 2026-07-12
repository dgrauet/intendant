"""Rust adapter — language-specific rules."""

from intendant.adapters.rust.ci import RUST_CI001MinimumSteps
from intendant.adapters.rust.pk import RustCargoLock, RustCargoToml, RustEdition
from intendant.adapters.rust.qu import RustToolchainPin
from intendant.adapters.rust.sa import RUST_SA001GitignoreBaseline, RUST_SA002CargoDenyAudit
from intendant.adapters.rust.ts import RustTestAnnotations
from intendant.core.rule import Rule

RULES: list[Rule] = [
    RustCargoToml(),
    RustCargoLock(),
    RustEdition(),
    RustToolchainPin(),
    RustTestAnnotations(),
    RUST_CI001MinimumSteps(),
    RUST_SA001GitignoreBaseline(),
    RUST_SA002CargoDenyAudit(),
]
