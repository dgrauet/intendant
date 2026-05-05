"""Tests for `suzerain new`."""

import subprocess
import tomllib
from pathlib import Path

import pytest
from typer.testing import CliRunner

from suzerain.cli import app

runner = CliRunner()


def test_new_creates_python_project(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        [
            "new",
            "my-app",
            "--stack",
            "python",
            "--description",
            "Test app",
            "--author",
            "Test",
            "--path",
            str(tmp_path),
            "--no-git",
        ],
    )
    assert result.exit_code == 0, result.stdout
    target = tmp_path / "my-app"
    assert target.is_dir()
    assert (target / "pyproject.toml").is_file()
    assert (target / "src" / "my_app" / "__init__.py").is_file()


def test_new_refuses_existing_target(tmp_path: Path) -> None:
    target = tmp_path / "exists"
    target.mkdir()
    result = runner.invoke(
        app,
        ["new", "exists", "--stack", "python", "--path", str(tmp_path), "--no-git"],
    )
    assert result.exit_code == 1
    assert "exists" in result.stdout.lower() or "already" in result.stdout.lower()


def test_new_unknown_stack(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        ["new", "x", "--stack", "haskell", "--path", str(tmp_path), "--no-git"],
    )
    assert result.exit_code == 1
    assert "haskell" in result.stdout.lower() or "stack" in result.stdout.lower()


def test_new_with_git_inits_repo(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        [
            "new",
            "git-test",
            "--stack",
            "python",
            "--description",
            "x",
            "--author",
            "T",
            "--path",
            str(tmp_path),
        ],
    )
    assert result.exit_code == 0, result.stdout
    target = tmp_path / "git-test"
    assert (target / ".git").is_dir()
    log = subprocess.run(
        ["git", "log", "--format=%s"],
        cwd=target,
        capture_output=True,
        text=True,
        check=True,
    )
    assert "scaffold from suzerain" in log.stdout


def test_new_claude_skill_creates_skill_md_at_nested_path(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        [
            "new",
            "test-skill",
            "--stack",
            "claude-skill",
            "--path",
            str(tmp_path),
            "--no-git",
        ],
    )
    assert result.exit_code == 0, result.stdout
    target = tmp_path / "test-skill"
    assert (target / "test-skill" / "SKILL.md").is_file()
    assert not (target / "SKILL.md").exists()


def test_new_claude_skill_creates_evals_with_placeholder(tmp_path: Path) -> None:
    runner.invoke(
        app,
        [
            "new",
            "test-skill",
            "--stack",
            "claude-skill",
            "--path",
            str(tmp_path),
            "--no-git",
        ],
    )
    evals_dir = tmp_path / "test-skill" / "test-skill" / "evals"
    assert evals_dir.is_dir()
    files = [f for f in evals_dir.iterdir() if f.is_file()]
    assert len(files) >= 1


def test_new_claude_skill_readme_mentions_install_path(tmp_path: Path) -> None:
    runner.invoke(
        app,
        [
            "new",
            "test-skill",
            "--stack",
            "claude-skill",
            "--path",
            str(tmp_path),
            "--no-git",
        ],
    )
    readme = tmp_path / "test-skill" / "README.md"
    assert readme.is_file()
    assert "~/.claude/skills/" in readme.read_text()


def test_new_claude_skill_suzerain_toml_has_strict_mode_and_exemptions(tmp_path: Path) -> None:
    runner.invoke(
        app,
        [
            "new",
            "test-skill",
            "--stack",
            "claude-skill",
            "--path",
            str(tmp_path),
            "--no-git",
        ],
    )
    cfg = tmp_path / "test-skill" / ".suzerain.toml"
    assert cfg.is_file()
    data = tomllib.loads(cfg.read_text())
    assert data["suzerain"]["enforcement"] == "strict"
    assert data["suzerain"]["stack"] == "claude-skill"
    # CI002 exemption removed: claude-skill CI now runs suzerain audit (CI002 passes natively)
    assert "CI003" in data.get("exemptions", {})
    assert "CI004" in data.get("exemptions", {})


def test_new_claude_skill_default_description_is_non_empty(tmp_path: Path) -> None:
    """Without --description, the skill should still get a placeholder description >= 10 chars."""
    runner.invoke(
        app,
        [
            "new",
            "test-skill",
            "--stack",
            "claude-skill",
            "--path",
            str(tmp_path),
            "--no-git",
        ],
    )
    skill_md = tmp_path / "test-skill" / "test-skill" / "SKILL.md"
    assert skill_md.is_file()
    text = skill_md.read_text()
    # extract description line from frontmatter
    for line in text.splitlines():
        if line.startswith("description:"):
            desc = line.removeprefix("description:").strip()
            assert len(desc) >= 10, f"description too short: {desc!r}"
            break
    else:
        pytest.fail("no description field found in SKILL.md frontmatter")


def test_new_substitutes_placeholders(tmp_path: Path) -> None:
    runner.invoke(
        app,
        [
            "new",
            "subtest",
            "--stack",
            "python",
            "--description",
            "Substitution test",
            "--author",
            "Tester",
            "--path",
            str(tmp_path),
            "--no-git",
        ],
    )
    target = tmp_path / "subtest"
    pyproject = tomllib.loads((target / "pyproject.toml").read_text())
    assert pyproject["project"]["name"] == "subtest"
    assert pyproject["project"]["description"] == "Substitution test"
    license_text = (target / "LICENSE").read_text()
    assert "Tester" in license_text


# ---------------------------------------------------------------------------
# Node stack tests (palier 5.1)
# ---------------------------------------------------------------------------


def _invoke_node_scaffold(tmp_path: Path, name: str = "my-node-app") -> Path:
    result = runner.invoke(
        app,
        [
            "new",
            name,
            "--stack",
            "node",
            "--description",
            "A Node test project",
            "--path",
            str(tmp_path),
            "--no-git",
        ],
    )
    assert result.exit_code == 0, result.stdout
    return tmp_path / name


def test_new_node_creates_package_json(tmp_path: Path) -> None:
    target = _invoke_node_scaffold(tmp_path)
    pkg = target / "package.json"
    assert pkg.is_file()
    import json

    data = json.loads(pkg.read_text())
    assert data["name"] == "my-node-app"
    assert data["type"] == "module"
    assert "vitest" in data["devDependencies"]
    assert "typescript" in data["devDependencies"]
    assert "eslint" in data["devDependencies"]


def test_new_node_creates_src_and_tests(tmp_path: Path) -> None:
    target = _invoke_node_scaffold(tmp_path)
    assert (target / "src" / "index.ts").is_file()
    assert (target / "tests" / "index.test.ts").is_file()


def test_new_node_suzerain_toml_has_strict_mode_and_exemptions(tmp_path: Path) -> None:
    target = _invoke_node_scaffold(tmp_path)
    cfg = target / ".suzerain.toml"
    assert cfg.is_file()
    data = tomllib.loads(cfg.read_text())
    assert data["suzerain"]["enforcement"] == "strict"
    assert data["suzerain"]["stack"] == "node"
    exemptions = data.get("exemptions", {})
    assert "NODE_PK002" in exemptions
    # CI002 exemption removed: node CI now runs eslint/tsc/vitest (CI002 passes natively)


def test_new_node_eslint_config_present(tmp_path: Path) -> None:
    target = _invoke_node_scaffold(tmp_path)
    assert (target / "eslint.config.js").is_file()


def test_new_node_tsconfig_present(tmp_path: Path) -> None:
    target = _invoke_node_scaffold(tmp_path)
    assert (target / "tsconfig.json").is_file()


# ---------------------------------------------------------------------------
# Rust scaffolder
# ---------------------------------------------------------------------------


def _invoke_rust_scaffold(tmp_path: Path, name: str = "my-rust-app") -> Path:
    result = runner.invoke(
        app,
        [
            "new",
            name,
            "--stack",
            "rust",
            "--description",
            "A Rust test project",
            "--path",
            str(tmp_path),
            "--no-git",
        ],
    )
    assert result.exit_code == 0, result.stdout
    return tmp_path / name


def test_new_rust_creates_cargo_toml_with_package(tmp_path: Path) -> None:
    target = _invoke_rust_scaffold(tmp_path)
    cargo = target / "Cargo.toml"
    assert cargo.is_file()
    data = tomllib.loads(cargo.read_text())
    assert data["package"]["name"] == "my-rust-app"
    assert data["package"]["edition"] == "2021"


def test_new_rust_creates_lib_rs_with_test(tmp_path: Path) -> None:
    target = _invoke_rust_scaffold(tmp_path)
    lib = target / "src" / "lib.rs"
    assert lib.is_file()
    assert "#[test]" in lib.read_text()


def test_new_rust_ships_toolchain_pin(tmp_path: Path) -> None:
    target = _invoke_rust_scaffold(tmp_path)
    assert (target / "rust-toolchain.toml").is_file()


def test_new_rust_ci_workflow_runs_fmt_clippy_test(tmp_path: Path) -> None:
    target = _invoke_rust_scaffold(tmp_path)
    ci = target / ".github" / "workflows" / "ci.yml"
    assert ci.is_file()
    content = ci.read_text()
    assert "cargo fmt" in content
    assert "cargo clippy" in content
    assert "cargo test" in content


def test_new_rust_gitignore_has_target(tmp_path: Path) -> None:
    target = _invoke_rust_scaffold(tmp_path)
    text = (target / ".gitignore").read_text()
    assert "target/" in text


def test_new_rust_suzerain_toml_has_strict_mode_and_exemption(tmp_path: Path) -> None:
    target = _invoke_rust_scaffold(tmp_path)
    cfg = target / ".suzerain.toml"
    assert cfg.is_file()
    data = tomllib.loads(cfg.read_text())
    assert data["suzerain"]["enforcement"] == "strict"
    assert data["suzerain"]["stack"] == "rust"
    assert "RUST_PK002" in data.get("exemptions", {})


# ---------------------------------------------------------------------------
# Go scaffolder
# ---------------------------------------------------------------------------


def _invoke_go_scaffold(tmp_path: Path, name: str = "my-go-app") -> Path:
    result = runner.invoke(
        app,
        [
            "new",
            name,
            "--stack",
            "go",
            "--description",
            "A Go test project",
            "--path",
            str(tmp_path),
            "--no-git",
        ],
    )
    assert result.exit_code == 0, result.stdout
    return tmp_path / name


def test_new_go_creates_go_mod_with_module(tmp_path: Path) -> None:
    target = _invoke_go_scaffold(tmp_path)
    gomod = target / "go.mod"
    assert gomod.is_file()
    text = gomod.read_text()
    assert "module example.com/my-go-app" in text
    assert "go 1.22" in text


def test_new_go_creates_main_and_test(tmp_path: Path) -> None:
    target = _invoke_go_scaffold(tmp_path)
    assert (target / "main.go").is_file()
    test_file = target / "main_test.go"
    assert test_file.is_file()
    assert "func TestAdd" in test_file.read_text()


def test_new_go_ships_golangci_config(tmp_path: Path) -> None:
    target = _invoke_go_scaffold(tmp_path)
    assert (target / ".golangci.yml").is_file()


def test_new_go_ci_workflow_runs_vet_test_lint(tmp_path: Path) -> None:
    target = _invoke_go_scaffold(tmp_path)
    ci = target / ".github" / "workflows" / "ci.yml"
    assert ci.is_file()
    content = ci.read_text()
    assert "go vet" in content
    assert "go test" in content
    assert "golangci-lint" in content


def test_new_go_gitignore_has_test_pattern(tmp_path: Path) -> None:
    target = _invoke_go_scaffold(tmp_path)
    text = (target / ".gitignore").read_text()
    assert "*.test" in text


def test_new_go_suzerain_toml_has_strict_mode_and_exemption(tmp_path: Path) -> None:
    target = _invoke_go_scaffold(tmp_path)
    cfg = target / ".suzerain.toml"
    assert cfg.is_file()
    data = tomllib.loads(cfg.read_text())
    assert data["suzerain"]["enforcement"] == "strict"
    assert data["suzerain"]["stack"] == "go"
    assert "GO_PK002" in data.get("exemptions", {})


# ---------------------------------------------------------------------------
# Swift scaffold
# ---------------------------------------------------------------------------


def _invoke_swift_scaffold(tmp_path: Path, name: str = "my-swift-app") -> Path:
    result = runner.invoke(
        app,
        [
            "new",
            name,
            "--stack",
            "swift",
            "--description",
            "A Swift test project",
            "--path",
            str(tmp_path),
            "--no-git",
        ],
    )
    assert result.exit_code == 0, result.stdout
    return tmp_path / name


def test_new_swift_creates_package_swift_with_module(tmp_path: Path) -> None:
    target = _invoke_swift_scaffold(tmp_path)
    pkg = target / "Package.swift"
    assert pkg.is_file()
    text = pkg.read_text()
    # kebab-case → PascalCase: my-swift-app → MySwiftApp
    assert 'name: "MySwiftApp"' in text
    assert "// swift-tools-version:" in text


def test_new_swift_creates_sources_and_tests(tmp_path: Path) -> None:
    target = _invoke_swift_scaffold(tmp_path)
    src = target / "Sources" / "MySwiftApp" / "MySwiftApp.swift"
    test = target / "Tests" / "MySwiftAppTests" / "MySwiftAppTests.swift"
    assert src.is_file()
    assert test.is_file()
    assert "public struct MySwiftApp" in src.read_text()
    assert "func testAdd" in test.read_text()
    assert "XCTestCase" in test.read_text()


def test_new_swift_ships_swiftlint_config(tmp_path: Path) -> None:
    target = _invoke_swift_scaffold(tmp_path)
    assert (target / ".swiftlint.yml").is_file()


def test_new_swift_ci_workflow_runs_build_test_lint(tmp_path: Path) -> None:
    target = _invoke_swift_scaffold(tmp_path)
    ci = target / ".github" / "workflows" / "ci.yml"
    assert ci.is_file()
    content = ci.read_text()
    assert "swift build" in content
    assert "swift test" in content
    assert "swiftlint" in content


def test_new_swift_gitignore_has_baseline_patterns(tmp_path: Path) -> None:
    target = _invoke_swift_scaffold(tmp_path)
    text = (target / ".gitignore").read_text()
    assert ".build/" in text
    assert "xcuserdata/" in text


def test_new_swift_suzerain_toml_has_strict_enforcement_and_exemption(tmp_path: Path) -> None:
    target = _invoke_swift_scaffold(tmp_path)
    cfg = target / ".suzerain.toml"
    assert cfg.is_file()
    data = tomllib.loads(cfg.read_text())
    assert data["suzerain"]["enforcement"] == "strict"
    assert data["suzerain"]["stack"] == "swift"
    assert "SWIFT_PK002" in data.get("exemptions", {})
