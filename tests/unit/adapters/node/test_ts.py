"""Tests for Node adapter NODE_TS rules."""

import json
from pathlib import Path

from suzerain.adapters.node.ts import NodeTestFramework
from suzerain.core.repo import Repo


def _write_pkg(path: Path, pkg: dict) -> None:
    (path / "package.json").write_text(json.dumps(pkg))


# ---------------------------------------------------------------------------
# NODE_TS001 — test framework or test script
# ---------------------------------------------------------------------------


def test_ts001_pass_vitest(tmp_path: Path) -> None:
    _write_pkg(tmp_path, {"devDependencies": {"vitest": "^2.0.0"}})
    repo = Repo(path=tmp_path, stack="node")
    result = NodeTestFramework().check(repo)
    assert result.passing is True
    assert "vitest" in result.evidence


def test_ts001_pass_jest(tmp_path: Path) -> None:
    _write_pkg(tmp_path, {"devDependencies": {"jest": "^29.0.0"}})
    repo = Repo(path=tmp_path, stack="node")
    result = NodeTestFramework().check(repo)
    assert result.passing is True


def test_ts001_pass_mocha(tmp_path: Path) -> None:
    _write_pkg(tmp_path, {"devDependencies": {"mocha": "^10.0.0"}})
    repo = Repo(path=tmp_path, stack="node")
    result = NodeTestFramework().check(repo)
    assert result.passing is True


def test_ts001_pass_ava(tmp_path: Path) -> None:
    _write_pkg(tmp_path, {"devDependencies": {"ava": "^6.0.0"}})
    repo = Repo(path=tmp_path, stack="node")
    result = NodeTestFramework().check(repo)
    assert result.passing is True


def test_ts001_pass_test_script_fallback(tmp_path: Path) -> None:
    # bun test — no recognized framework dep, but has a test script
    _write_pkg(tmp_path, {"scripts": {"test": "bun test"}})
    repo = Repo(path=tmp_path, stack="node")
    result = NodeTestFramework().check(repo)
    assert result.passing is True
    assert "bun test" in result.evidence


def test_ts001_fail_no_framework_no_script(tmp_path: Path) -> None:
    _write_pkg(tmp_path, {"devDependencies": {"eslint": "^9.0.0"}})
    repo = Repo(path=tmp_path, stack="node")
    result = NodeTestFramework().check(repo)
    assert result.passing is False
    assert "test" in result.evidence.lower()


def test_ts001_fail_scripts_without_test_key(tmp_path: Path) -> None:
    _write_pkg(tmp_path, {"scripts": {"build": "tsc"}})
    repo = Repo(path=tmp_path, stack="node")
    result = NodeTestFramework().check(repo)
    assert result.passing is False


def test_ts001_skipped_when_no_package_json(tmp_path: Path) -> None:
    repo = Repo(path=tmp_path, stack="node")
    result = NodeTestFramework().check(repo)
    assert result.passing is True
    assert result.skipped is True


def test_ts001_skipped_on_malformed_json(tmp_path: Path) -> None:
    (tmp_path / "package.json").write_text("{bad")
    repo = Repo(path=tmp_path, stack="node")
    result = NodeTestFramework().check(repo)
    assert result.passing is True
    assert result.skipped is True


def test_ts001_metadata() -> None:
    rule = NodeTestFramework()
    assert rule.id == "NODE_TS001"
    assert rule.severity == "required"
    assert "node" in rule.stacks
