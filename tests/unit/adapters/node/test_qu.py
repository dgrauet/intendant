"""Tests for Node adapter NODE_QU rules."""

import json
from pathlib import Path

from suzerain.adapters.node.qu import NodeLinter, NodeTypeScript
from suzerain.core.repo import Repo


def _write_pkg(path: Path, pkg: dict) -> None:
    (path / "package.json").write_text(json.dumps(pkg))


# ---------------------------------------------------------------------------
# NODE_QU001 — linter declared
# ---------------------------------------------------------------------------


def test_qu001_pass_eslint(tmp_path: Path) -> None:
    _write_pkg(tmp_path, {"devDependencies": {"eslint": "^9.0.0"}})
    repo = Repo(path=tmp_path, stack="node")
    result = NodeLinter().check(repo)
    assert result.passing is True
    assert "eslint" in result.evidence


def test_qu001_pass_biome(tmp_path: Path) -> None:
    _write_pkg(tmp_path, {"devDependencies": {"@biomejs/biome": "^1.0.0"}})
    repo = Repo(path=tmp_path, stack="node")
    result = NodeLinter().check(repo)
    assert result.passing is True


def test_qu001_pass_prettier(tmp_path: Path) -> None:
    _write_pkg(tmp_path, {"devDependencies": {"prettier": "^3.0.0"}})
    repo = Repo(path=tmp_path, stack="node")
    result = NodeLinter().check(repo)
    assert result.passing is True


def test_qu001_pass_linter_in_dependencies(tmp_path: Path) -> None:
    # Linter in regular dependencies should still count
    _write_pkg(tmp_path, {"dependencies": {"eslint": "^9.0.0"}})
    repo = Repo(path=tmp_path, stack="node")
    result = NodeLinter().check(repo)
    assert result.passing is True


def test_qu001_fail_no_linter(tmp_path: Path) -> None:
    _write_pkg(tmp_path, {"devDependencies": {"typescript": "^5.0.0"}})
    repo = Repo(path=tmp_path, stack="node")
    result = NodeLinter().check(repo)
    assert result.passing is False
    assert "linter" in result.evidence.lower()


def test_qu001_skipped_when_no_package_json(tmp_path: Path) -> None:
    repo = Repo(path=tmp_path, stack="node")
    result = NodeLinter().check(repo)
    assert result.passing is True
    assert result.skipped is True


def test_qu001_skipped_on_malformed_json(tmp_path: Path) -> None:
    (tmp_path / "package.json").write_text("{bad")
    repo = Repo(path=tmp_path, stack="node")
    result = NodeLinter().check(repo)
    assert result.passing is True
    assert result.skipped is True


def test_qu001_metadata() -> None:
    rule = NodeLinter()
    assert rule.id == "NODE_QU001"
    assert rule.severity == "required"
    assert "node" in rule.stacks


# ---------------------------------------------------------------------------
# NODE_QU002 — TypeScript present
# ---------------------------------------------------------------------------


def test_qu002_pass_typescript_dep(tmp_path: Path) -> None:
    _write_pkg(tmp_path, {"devDependencies": {"typescript": "^5.0.0"}})
    repo = Repo(path=tmp_path, stack="node")
    result = NodeTypeScript().check(repo)
    assert result.passing is True
    assert "typescript" in result.evidence


def test_qu002_pass_tsconfig(tmp_path: Path) -> None:
    _write_pkg(tmp_path, {"name": "x"})
    (tmp_path / "tsconfig.json").write_text('{"compilerOptions": {}}')
    repo = Repo(path=tmp_path, stack="node")
    result = NodeTypeScript().check(repo)
    assert result.passing is True
    assert "tsconfig.json" in result.evidence


def test_qu002_fail_no_ts_signal(tmp_path: Path) -> None:
    _write_pkg(tmp_path, {"devDependencies": {"eslint": "^9.0.0"}})
    repo = Repo(path=tmp_path, stack="node")
    result = NodeTypeScript().check(repo)
    assert result.passing is False
    assert "TypeScript" in result.evidence or "typescript" in result.evidence.lower()


def test_qu002_skipped_when_no_package_json(tmp_path: Path) -> None:
    repo = Repo(path=tmp_path, stack="node")
    result = NodeTypeScript().check(repo)
    assert result.passing is True
    assert result.skipped is True


def test_qu002_metadata() -> None:
    rule = NodeTypeScript()
    assert rule.id == "NODE_QU002"
    assert rule.severity == "recommended"
    assert "node" in rule.stacks
