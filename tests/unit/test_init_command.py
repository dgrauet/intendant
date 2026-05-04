"""Tests for the suzerain init command."""

import shutil
import tomllib
from pathlib import Path

from typer.testing import CliRunner

from suzerain.cli import app

runner = CliRunner()


def _setup_target(tmp_path: Path, fixture_name: str | None, fixtures_dir: Path) -> Path:
    target = tmp_path / "target_repo"
    target.mkdir()
    if fixture_name:
        src = fixtures_dir / fixture_name
        for item in src.iterdir():
            if item.is_file():
                shutil.copy2(item, target / item.name)
            elif item.is_dir():
                shutil.copytree(item, target / item.name)
    return target


def test_init_in_empty_dir_writes_config(tmp_path: Path, fixtures_dir: Path) -> None:
    target = _setup_target(tmp_path, "empty_repo", fixtures_dir)
    result = runner.invoke(app, ["init", "--path", str(target)])
    assert result.exit_code == 0, result.stdout
    config_path = target / ".suzerain.toml"
    assert config_path.is_file()
    config = tomllib.loads(config_path.read_text())
    assert config["suzerain"]["version"] == "1"
    # Empty repo → no detection → no `stack` field written (auto-detect each run)
    assert "stack" not in config["suzerain"]
    assert config["suzerain"]["mode"] == "advisory"


def test_init_in_python_repo_detects_stack(tmp_path: Path, fixtures_dir: Path) -> None:
    target = _setup_target(tmp_path, "python_repo", fixtures_dir)
    result = runner.invoke(app, ["init", "--path", str(target)])
    assert result.exit_code == 0
    config = tomllib.loads((target / ".suzerain.toml").read_text())
    assert config["suzerain"]["stack"] == "python"


def test_init_in_node_repo_detects_stack(tmp_path: Path, fixtures_dir: Path) -> None:
    target = _setup_target(tmp_path, "node_repo", fixtures_dir)
    result = runner.invoke(app, ["init", "--path", str(target)])
    assert result.exit_code == 0
    config = tomllib.loads((target / ".suzerain.toml").read_text())
    assert config["suzerain"]["stack"] == "node"


def test_init_creates_adoption_adr(tmp_path: Path, fixtures_dir: Path) -> None:
    target = _setup_target(tmp_path, "python_repo", fixtures_dir)
    result = runner.invoke(app, ["init", "--path", str(target)])
    assert result.exit_code == 0
    adr_path = target / "docs" / "adr" / "0000-adopt-suzerain.md"
    assert adr_path.is_file()
    content = adr_path.read_text()
    assert "ADR-0000" in content
    assert "adopt suzerain" in content.lower() or "adoption de suzerain" in content.lower()


def test_init_refuses_to_overwrite_existing_config(tmp_path: Path, fixtures_dir: Path) -> None:
    target = _setup_target(tmp_path, "python_repo", fixtures_dir)
    (target / ".suzerain.toml").write_text('[suzerain]\nversion = "0"\n')
    result = runner.invoke(app, ["init", "--path", str(target)])
    assert result.exit_code != 0
    config = tomllib.loads((target / ".suzerain.toml").read_text())
    assert config["suzerain"]["version"] == "0"  # untouched


def test_init_with_force_overwrites(tmp_path: Path, fixtures_dir: Path) -> None:
    target = _setup_target(tmp_path, "python_repo", fixtures_dir)
    (target / ".suzerain.toml").write_text('[suzerain]\nversion = "0"\n')
    result = runner.invoke(app, ["init", "--path", str(target), "--force"])
    assert result.exit_code == 0
    config = tomllib.loads((target / ".suzerain.toml").read_text())
    assert config["suzerain"]["version"] == "1"


def test_init_does_not_overwrite_existing_adr_0000(tmp_path: Path, fixtures_dir: Path) -> None:
    target = _setup_target(tmp_path, "python_repo", fixtures_dir)
    adr_dir = target / "docs" / "adr"
    adr_dir.mkdir(parents=True)
    existing = adr_dir / "0000-adopt-suzerain.md"
    existing.write_text("# Custom ADR — keep me\n")
    result = runner.invoke(app, ["init", "--path", str(target)])
    assert result.exit_code == 0
    assert existing.read_text() == "# Custom ADR — keep me\n"
