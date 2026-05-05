"""Tests for IntendantConfig multi-subproject parsing + exemption resolution."""

from __future__ import annotations

from pathlib import Path

import pytest

from intendant.core.config import (
    Exemption,
    IntendantConfig,
    load_config,
)


def _write(tmp_path: Path, body: str) -> Path:
    target = tmp_path / ".intendant.toml"
    target.write_text(body)
    return tmp_path


def test_load_config_no_subprojects_returns_empty_list(tmp_path: Path) -> None:
    repo = _write(
        tmp_path, '[intendant]\nversion = "1"\nstack = "python"\nenforcement = "advisory"\n'
    )
    cfg = load_config(repo)
    assert cfg.subprojects == []
    assert cfg.subproject_exemptions == {}


def test_load_config_parses_minimal_subproject(tmp_path: Path) -> None:
    repo = _write(
        tmp_path,
        '[intendant]\nversion = "1"\nenforcement = "strict"\n\n'
        '[[subprojects]]\nname = "backend"\npath = "backend"\nstack = "python"\n',
    )
    cfg = load_config(repo)
    assert len(cfg.subprojects) == 1
    sp = cfg.subprojects[0]
    assert sp.name == "backend"
    assert sp.path == "backend"
    assert sp.stack == "python"


def test_load_config_default_name_from_basename(tmp_path: Path) -> None:
    repo = _write(
        tmp_path,
        '[intendant]\nversion = "1"\nenforcement = "strict"\n\n'
        '[[subprojects]]\npath = "packages/foo"\nstack = "python"\n',
    )
    cfg = load_config(repo)
    assert cfg.subprojects[0].name == "foo"


def test_load_config_default_name_root_for_dot_path(tmp_path: Path) -> None:
    repo = _write(
        tmp_path,
        '[intendant]\nversion = "1"\nenforcement = "strict"\n\n'
        '[[subprojects]]\npath = "."\nstack = "swift"\n',
    )
    cfg = load_config(repo)
    assert cfg.subprojects[0].name == "root"


def test_load_config_missing_path_raises(tmp_path: Path) -> None:
    repo = _write(
        tmp_path,
        '[intendant]\nversion = "1"\nenforcement = "strict"\n\n'
        '[[subprojects]]\nname = "x"\nstack = "python"\n',
    )
    with pytest.raises(ValueError, match="missing required field: path"):
        load_config(repo)


def test_load_config_missing_stack_raises(tmp_path: Path) -> None:
    repo = _write(
        tmp_path,
        '[intendant]\nversion = "1"\nenforcement = "strict"\n\n'
        '[[subprojects]]\nname = "x"\npath = "x"\n',
    )
    with pytest.raises(ValueError, match="missing required field: stack"):
        load_config(repo)


def test_load_config_absolute_path_raises(tmp_path: Path) -> None:
    repo = _write(
        tmp_path,
        '[intendant]\nversion = "1"\nenforcement = "strict"\n\n'
        '[[subprojects]]\nname = "x"\npath = "/abs"\nstack = "python"\n',
    )
    with pytest.raises(ValueError, match="must be relative"):
        load_config(repo)


def test_load_config_path_traversal_raises(tmp_path: Path) -> None:
    repo = _write(
        tmp_path,
        '[intendant]\nversion = "1"\nenforcement = "strict"\n\n'
        '[[subprojects]]\nname = "x"\npath = "../foo"\nstack = "python"\n',
    )
    with pytest.raises(ValueError, match="must not contain"):
        load_config(repo)


def test_load_config_invalid_name_raises(tmp_path: Path) -> None:
    repo = _write(
        tmp_path,
        '[intendant]\nversion = "1"\nenforcement = "strict"\n\n'
        '[[subprojects]]\nname = "bad name"\npath = "x"\nstack = "python"\n',
    )
    with pytest.raises(ValueError, match="must match"):
        load_config(repo)


def test_load_config_duplicate_names_raise(tmp_path: Path) -> None:
    repo = _write(
        tmp_path,
        '[intendant]\nversion = "1"\nenforcement = "strict"\n\n'
        '[[subprojects]]\nname = "x"\npath = "a"\nstack = "python"\n\n'
        '[[subprojects]]\nname = "x"\npath = "b"\nstack = "python"\n',
    )
    with pytest.raises(ValueError, match="duplicate subproject name: x"):
        load_config(repo)


def test_load_config_duplicate_paths_raise(tmp_path: Path) -> None:
    repo = _write(
        tmp_path,
        '[intendant]\nversion = "1"\nenforcement = "strict"\n\n'
        '[[subprojects]]\nname = "a"\npath = "x"\nstack = "python"\n\n'
        '[[subprojects]]\nname = "b"\npath = "x"\nstack = "python"\n',
    )
    with pytest.raises(ValueError, match="duplicate subproject path: x"):
        load_config(repo)


def test_load_config_parses_subproject_exemptions(tmp_path: Path) -> None:
    repo = _write(
        tmp_path,
        '[intendant]\nversion = "1"\nenforcement = "strict"\n\n'
        '[[subprojects]]\nname = "backend"\npath = "backend"\nstack = "python"\n\n'
        '[exemptions]\nDG002 = "no claude.md"\n\n'
        '[exemptions.backend]\nPYTHON_QU001 = "ruff config TBD"\n',
    )
    cfg = load_config(repo)
    assert "DG002" in cfg.exemptions
    assert "backend" in cfg.subproject_exemptions
    assert "PYTHON_QU001" in cfg.subproject_exemptions["backend"]
    assert cfg.subproject_exemptions["backend"]["PYTHON_QU001"].reason == "ruff config TBD"


def test_is_rule_exempt_for_subproject_scoped_wins(tmp_path: Path) -> None:
    cfg = IntendantConfig(
        version="1",
        stack=None,
        enforcement="strict",
        exemptions={"X": Exemption(reason="top-level")},
        subproject_exemptions={"backend": {"X": Exemption(reason="scoped")}},
    )
    result = cfg.is_rule_exempt_for_subproject("X", "backend")
    assert result is not None
    assert result.reason == "scoped"


def test_is_rule_exempt_for_subproject_falls_back_to_top_level(tmp_path: Path) -> None:
    cfg = IntendantConfig(
        version="1",
        stack=None,
        enforcement="strict",
        exemptions={"X": Exemption(reason="top-level")},
        subproject_exemptions={"backend": {}},
    )
    result = cfg.is_rule_exempt_for_subproject("X", "backend")
    assert result is not None
    assert result.reason == "top-level"


def test_is_rule_exempt_for_subproject_no_match_returns_none(tmp_path: Path) -> None:
    cfg = IntendantConfig(version="1", stack=None, enforcement="strict")
    assert cfg.is_rule_exempt_for_subproject("X", "backend") is None


def test_is_rule_exempt_for_subproject_with_none_subproject_uses_top_level_only(
    tmp_path: Path,
) -> None:
    cfg = IntendantConfig(
        version="1",
        stack=None,
        enforcement="strict",
        exemptions={"X": Exemption(reason="top-level")},
    )
    result = cfg.is_rule_exempt_for_subproject("X", None)
    assert result is not None
    assert result.reason == "top-level"
