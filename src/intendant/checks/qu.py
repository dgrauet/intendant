"""QU (quality coherence) transverse rules."""

from __future__ import annotations

from pathlib import Path

from intendant.core.repo import Repo
from intendant.core.rule import CheckResult, Rule

# Known quality-tool config files → CI markers proving the tool actually runs.
# Only unambiguous, tool-specific config names belong here (universal files
# like .editorconfig would produce false positives).
_TOOL_CONFIGS: dict[str, tuple[str, ...]] = {
    ".swiftlint.yml": ("swiftlint",),
    ".swiftlint.yaml": ("swiftlint",),
    ".swiftformat": ("swiftformat",),
    "rustfmt.toml": ("cargo fmt", "rustfmt"),
    ".rustfmt.toml": ("cargo fmt", "rustfmt"),
    "clippy.toml": ("clippy",),
    ".golangci.yml": ("golangci-lint",),
    ".golangci.yaml": ("golangci-lint",),
    ".golangci.toml": ("golangci-lint",),
    "deny.toml": ("cargo deny", "cargo-deny"),
    "ruff.toml": ("ruff",),
    ".ruff.toml": ("ruff",),
    "biome.json": ("biome",),
    "biome.jsonc": ("biome",),
    "eslint.config.js": ("eslint",),
    "eslint.config.mjs": ("eslint",),
    ".eslintrc.json": ("eslint",),
    ".eslintrc.js": ("eslint",),
    ".eslintrc.yml": ("eslint",),
}

_SCAN_SKIP = {
    "node_modules",
    "target",
    "dist",
    "build",
    ".build",
    "bin",
    "obj",
    "vendor",
    "__pycache__",
    ".venv",
    "venv",
    "Pods",
}
_SCAN_MAX_DEPTH = 5


def _find_tool_configs(repo_path: Path) -> list[tuple[str, str, tuple[str, ...]]]:
    """Return ``(tool config rel path, tool name, CI markers)`` for known configs.

    Scans the repo root and subdirectories (bounded depth, skipping hidden
    and build/vendored dirs). A ``pyproject.toml`` declaring ``[tool.ruff``
    counts as a ruff config.
    """
    found: list[tuple[str, str, tuple[str, ...]]] = []

    def scan_dir(directory: Path, depth: int) -> None:
        for name, markers in _TOOL_CONFIGS.items():
            if (directory / name).is_file():
                rel = (directory / name).relative_to(repo_path).as_posix()
                found.append((rel, markers[0].split()[0], markers))
        pyproject = directory / "pyproject.toml"
        if pyproject.is_file():
            try:
                if "[tool.ruff" in pyproject.read_text(errors="replace"):
                    rel = pyproject.relative_to(repo_path).as_posix()
                    found.append((f"{rel} [tool.ruff]", "ruff", ("ruff",)))
            except OSError:
                pass
        if depth >= _SCAN_MAX_DEPTH:
            return
        for entry in sorted(directory.iterdir()):
            if not entry.is_dir():
                continue
            if entry.name.startswith(".") or entry.name in _SCAN_SKIP:
                continue
            scan_dir(entry, depth + 1)

    scan_dir(repo_path, 0)
    return found


class QU001ConfiguredToolsRunInCI(Rule):
    id = "QU001"
    title = "configured quality tools are exercised in CI"
    severity = "recommended"
    stacks = ("*",)
    handbook_ref = "docs/handbook/04-quality.md#qu001"

    def check(self, repo: Repo) -> CheckResult:
        wf_dir = repo.path / ".github" / "workflows"
        if not wf_dir.is_dir():
            return CheckResult(
                passing=True,
                skipped=True,
                evidence="no .github/workflows/ directory (covered by CI001)",
            )
        configs = _find_tool_configs(repo.path)
        if not configs:
            return CheckResult(passing=True, evidence="no known quality-tool config found")
        contents = "\n".join(
            p.read_text(errors="replace")
            for pattern in ("*.yml", "*.yaml")
            for p in wf_dir.glob(pattern)
        )
        dormant = [
            f"{rel} (expected `{tool}` in a workflow)"
            for rel, tool, markers in configs
            if not any(m in contents for m in markers)
        ]
        if dormant:
            return CheckResult(
                passing=False,
                evidence=(
                    f"{len(dormant)} quality-tool config(s) never executed by CI: "
                    f"{dormant[:5]} — add the CI step or remove the dormant config"
                ),
            )
        return CheckResult(
            passing=True,
            evidence=f"{len(configs)} configured tool(s), all exercised in CI",
        )
