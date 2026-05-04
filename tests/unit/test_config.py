"""Tests for SuzerainConfig (parses .suzerain.toml)."""

from pathlib import Path

from suzerain.core.config import (
    DEFAULT_MODE,
    Exemption,
    SuzerainConfig,
    load_config,
)


def test_default_config_when_no_file(tmp_path: Path) -> None:
    config = load_config(tmp_path)
    assert config.version == "1"
    assert config.mode == "advisory"
    assert config.stack is None
    assert config.exemptions == {}


def test_load_minimal_config(tmp_path: Path) -> None:
    (tmp_path / ".suzerain.toml").write_text(
        '[suzerain]\nversion = "1"\nstack = "python"\nmode = "strict"\n'
    )
    config = load_config(tmp_path)
    assert config.version == "1"
    assert config.stack == "python"
    assert config.mode == "strict"


def test_load_with_string_exemption(tmp_path: Path) -> None:
    (tmp_path / ".suzerain.toml").write_text(
        '[suzerain]\nversion = "1"\nstack = "python"\nmode = "strict"\n'
        "[exemptions]\n"
        'PYTHON_LO001 = "Fork upstream"\n'
    )
    config = load_config(tmp_path)
    assert "PYTHON_LO001" in config.exemptions
    assert config.exemptions["PYTHON_LO001"].reason == "Fork upstream"
    assert config.exemptions["PYTHON_LO001"].until is None


def test_load_with_dict_exemption(tmp_path: Path) -> None:
    (tmp_path / ".suzerain.toml").write_text(
        '[suzerain]\nversion = "1"\nstack = "python"\nmode = "strict"\n'
        "[exemptions]\n"
        'CI003 = { reason = "Private repo", until = "2026-09-01" }\n'
    )
    config = load_config(tmp_path)
    assert config.exemptions["CI003"].reason == "Private repo"
    assert config.exemptions["CI003"].until == "2026-09-01"


def test_is_rule_exempt() -> None:
    config = SuzerainConfig(
        version="1",
        stack="python",
        mode="strict",
        exemptions={"PYTHON_LO001": Exemption(reason="Fork upstream", until=None)},
    )
    assert config.is_rule_exempt("PYTHON_LO001") is True
    assert config.is_rule_exempt("PYTHON_PK001") is False


def test_default_mode_constant() -> None:
    assert DEFAULT_MODE == "advisory"
