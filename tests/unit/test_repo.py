"""Tests for stack detection."""

from pathlib import Path

import pytest

from suzerain.core.repo import Repo, detect_stacks


def test_detect_python_from_pyproject(fixtures_dir: Path) -> None:
    assert detect_stacks(fixtures_dir / "python_repo") == ("python",)


def test_detect_node_from_package_json(fixtures_dir: Path) -> None:
    assert detect_stacks(fixtures_dir / "node_repo") == ("node",)


def test_detect_rust_from_cargo_toml(fixtures_dir: Path) -> None:
    assert detect_stacks(fixtures_dir / "rust_repo") == ("rust",)


def test_detect_swift_from_package_swift(fixtures_dir: Path) -> None:
    assert detect_stacks(fixtures_dir / "swift_repo") == ("swift",)


def test_detect_unknown_returns_empty(fixtures_dir: Path) -> None:
    assert detect_stacks(fixtures_dir / "empty_repo") == ()


def test_repo_dataclass(fixtures_dir: Path) -> None:
    repo = Repo.from_path(fixtures_dir / "python_repo")
    assert repo.path == fixtures_dir / "python_repo"
    assert repo.stacks == ("python",)
    assert repo.mode == "auto"


def test_repo_unknown_stack_yields_empty_stacks_in_auto_mode(fixtures_dir: Path) -> None:
    repo = Repo.from_path(fixtures_dir / "empty_repo")
    assert repo.stacks == ()
    assert repo.mode == "auto"


def test_detect_stacks_raises_for_missing_path(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        detect_stacks(tmp_path / "does_not_exist")


def test_repo_can_have_name_for_subproject() -> None:
    """Subproject Repos carry a name; root meta-Repo has name=None."""
    sub = Repo(path=Path("/tmp"), stacks=("python",), mode="manual", name="backend")
    assert sub.name == "backend"

    root = Repo(path=Path("/tmp"), stacks=(), mode="manual")
    assert root.name is None
