"""Guard the wheel actually bundles the handbook, ADRs, and templates.

These assets live at the repo root (docs/, templates/) for humans, but an
installed wheel must carry them inside the package so `intendant explain`,
`doctor`, and the scaffold engine work without the source checkout. The bug
that shipped through 4.0.0 to 4.0.2 was exactly a missing force-include here.
"""

from __future__ import annotations

import tomllib
from pathlib import Path

_PYPROJECT = Path(__file__).resolve().parents[2] / "pyproject.toml"

_EXPECTED_FORCE_INCLUDE = {
    "docs/handbook": "intendant/_assets/handbook",
    "docs/adr": "intendant/_assets/adr",
    "templates": "intendant/_assets/templates",
}


def _force_include() -> dict[str, str]:
    data = tomllib.loads(_PYPROJECT.read_text())
    return data["tool"]["hatch"]["build"]["targets"]["wheel"]["force-include"]


def test_wheel_force_includes_assets() -> None:
    force_include = _force_include()
    for src, dest in _EXPECTED_FORCE_INCLUDE.items():
        assert force_include.get(src) == dest, (
            f"pyproject force-include must map {src!r} -> {dest!r} so the wheel "
            f"bundles it; got {force_include.get(src)!r}"
        )


def test_force_included_sources_exist() -> None:
    repo_root = _PYPROJECT.parent
    for src in _EXPECTED_FORCE_INCLUDE:
        assert (repo_root / src).is_dir(), f"force-include source {src!r} does not exist"
