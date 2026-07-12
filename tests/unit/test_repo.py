"""Tests for stack detection."""

from pathlib import Path

import pytest

from intendant.core.repo import Repo, detect_stacks, find_nested_stack_roots


def test_detect_python_from_pyproject(fixtures_dir: Path) -> None:
    assert detect_stacks(fixtures_dir / "python_repo") == ("python",)


def test_detect_node_from_package_json(fixtures_dir: Path) -> None:
    assert detect_stacks(fixtures_dir / "node_repo") == ("node",)


def test_detect_rust_from_cargo_toml(fixtures_dir: Path) -> None:
    assert detect_stacks(fixtures_dir / "rust_repo") == ("rust",)


def test_detect_swift_from_package_swift(fixtures_dir: Path) -> None:
    assert detect_stacks(fixtures_dir / "swift_repo") == ("swift",)


def test_detect_dotnet_from_csproj(tmp_path: Path) -> None:
    (tmp_path / "App.csproj").write_text('<Project Sdk="Microsoft.NET.Sdk"></Project>\n')
    assert detect_stacks(tmp_path) == ("dotnet",)


def test_detect_dotnet_from_sln(tmp_path: Path) -> None:
    (tmp_path / "App.sln").write_text("Microsoft Visual Studio Solution File\n")
    assert detect_stacks(tmp_path) == ("dotnet",)


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


# --- find_nested_stack_roots ---


def test_nested_roots_finds_markers_below_root(tmp_path: Path) -> None:
    (tmp_path / "Cargo.toml").write_text("[workspace]\n")
    win = tmp_path / "apps" / "windows" / "App"
    win.mkdir(parents=True)
    (win / "App.csproj").write_text("<Project/>\n")
    mac = tmp_path / "apps" / "macos"
    mac.mkdir(parents=True)
    (mac / "Package.swift").write_text("// swift-tools-version:5.9\n")
    assert find_nested_stack_roots(tmp_path) == (
        ("apps/macos", "swift"),
        ("apps/windows/App", "dotnet"),
    )


def test_nested_roots_excludes_root_itself(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text("[project]\n")
    assert find_nested_stack_roots(tmp_path) == ()


def test_nested_roots_skips_build_and_hidden_dirs(tmp_path: Path) -> None:
    for skip in ("node_modules/pkg", "target/debug", ".venv/lib", ".git/x"):
        d = tmp_path / skip
        d.mkdir(parents=True)
        (d / "package.json").write_text("{}\n")
    assert find_nested_stack_roots(tmp_path) == ()


def test_nested_roots_respects_max_depth(tmp_path: Path) -> None:
    deep = tmp_path / "a" / "b" / "c" / "d" / "e" / "f"
    deep.mkdir(parents=True)
    (deep / "go.mod").write_text("module x\n")
    assert find_nested_stack_roots(tmp_path, max_depth=5) == ()
    assert find_nested_stack_roots(tmp_path, max_depth=6) == (("a/b/c/d/e/f", "go"),)
