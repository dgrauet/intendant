"""Tests for stack detection."""

from pathlib import Path

import pytest

from suzerain.core.repo import Repo, detect_stack


def test_detect_python_from_pyproject(fixtures_dir: Path) -> None:
    stack = detect_stack(fixtures_dir / "python_repo")
    assert stack == "python"


def test_detect_node_from_package_json(fixtures_dir: Path) -> None:
    stack = detect_stack(fixtures_dir / "node_repo")
    assert stack == "node"


def test_detect_rust_from_cargo_toml(fixtures_dir: Path) -> None:
    stack = detect_stack(fixtures_dir / "rust_repo")
    assert stack == "rust"


def test_detect_unknown_returns_none(fixtures_dir: Path) -> None:
    stack = detect_stack(fixtures_dir / "empty_repo")
    assert stack is None


def test_repo_dataclass(fixtures_dir: Path) -> None:
    repo = Repo.from_path(fixtures_dir / "python_repo")
    assert repo.path == fixtures_dir / "python_repo"
    assert repo.stack == "python"


def test_repo_unknown_stack_defaults_to_auto(fixtures_dir: Path) -> None:
    repo = Repo.from_path(fixtures_dir / "empty_repo")
    assert repo.stack == "auto"


def test_detect_stack_raises_for_missing_path(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        detect_stack(tmp_path / "does_not_exist")
