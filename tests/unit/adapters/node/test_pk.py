"""Tests for Node adapter NODE_PK rules."""

from pathlib import Path

from suzerain.adapters.node.pk import NodeEnginesNode, NodeLockfile, NodePackageJson
from suzerain.core.repo import Repo

# ---------------------------------------------------------------------------
# NODE_PK001 — package.json present
# ---------------------------------------------------------------------------


def test_pk001_pass(tmp_path: Path) -> None:
    (tmp_path / "package.json").write_text('{"name": "x"}')
    repo = Repo(path=tmp_path, stacks=("node",))
    assert NodePackageJson().check(repo).passing is True


def test_pk001_pass_evidence(tmp_path: Path) -> None:
    (tmp_path / "package.json").write_text('{"name": "x"}')
    repo = Repo(path=tmp_path, stacks=("node",))
    result = NodePackageJson().check(repo)
    assert "package.json" in result.evidence


def test_pk001_fail_missing(tmp_path: Path) -> None:
    repo = Repo(path=tmp_path, stacks=("node",))
    result = NodePackageJson().check(repo)
    assert result.passing is False
    assert "package.json" in result.evidence


def test_pk001_metadata() -> None:
    rule = NodePackageJson()
    assert rule.id == "NODE_PK001"
    assert rule.severity == "required"
    assert "node" in rule.stacks


# ---------------------------------------------------------------------------
# NODE_PK002 — lockfile present
# ---------------------------------------------------------------------------


def test_pk002_pass_npm(tmp_path: Path) -> None:
    (tmp_path / "package-lock.json").write_text("{}")
    repo = Repo(path=tmp_path, stacks=("node",))
    assert NodeLockfile().check(repo).passing is True


def test_pk002_pass_pnpm(tmp_path: Path) -> None:
    (tmp_path / "pnpm-lock.yaml").write_text("lockfileVersion: '6.0'")
    repo = Repo(path=tmp_path, stacks=("node",))
    assert NodeLockfile().check(repo).passing is True


def test_pk002_pass_yarn(tmp_path: Path) -> None:
    (tmp_path / "yarn.lock").write_text("# yarn lockfile v1")
    repo = Repo(path=tmp_path, stacks=("node",))
    assert NodeLockfile().check(repo).passing is True


def test_pk002_pass_bun(tmp_path: Path) -> None:
    (tmp_path / "bun.lockb").write_bytes(b"\x00\x01")
    repo = Repo(path=tmp_path, stacks=("node",))
    assert NodeLockfile().check(repo).passing is True


def test_pk002_fail_no_lockfile(tmp_path: Path) -> None:
    repo = Repo(path=tmp_path, stacks=("node",))
    result = NodeLockfile().check(repo)
    assert result.passing is False
    assert "lockfile" in result.evidence.lower()


def test_pk002_metadata() -> None:
    rule = NodeLockfile()
    assert rule.id == "NODE_PK002"
    assert rule.severity == "required"
    assert "node" in rule.stacks


# ---------------------------------------------------------------------------
# NODE_PK003 — engines.node declared
# ---------------------------------------------------------------------------


def test_pk003_pass(tmp_path: Path) -> None:
    (tmp_path / "package.json").write_text('{"name": "x", "engines": {"node": ">=18"}}')
    repo = Repo(path=tmp_path, stacks=("node",))
    result = NodeEnginesNode().check(repo)
    assert result.passing is True
    assert ">=18" in result.evidence


def test_pk003_fail_no_engines_field(tmp_path: Path) -> None:
    (tmp_path / "package.json").write_text('{"name": "x"}')
    repo = Repo(path=tmp_path, stacks=("node",))
    result = NodeEnginesNode().check(repo)
    assert result.passing is False
    assert "engines.node" in result.evidence


def test_pk003_fail_engines_without_node(tmp_path: Path) -> None:
    (tmp_path / "package.json").write_text('{"name": "x", "engines": {"npm": ">=8"}}')
    repo = Repo(path=tmp_path, stacks=("node",))
    result = NodeEnginesNode().check(repo)
    assert result.passing is False


def test_pk003_skipped_when_no_package_json(tmp_path: Path) -> None:
    repo = Repo(path=tmp_path, stacks=("node",))
    result = NodeEnginesNode().check(repo)
    assert result.passing is True
    assert result.skipped is True


def test_pk003_skipped_on_malformed_json(tmp_path: Path) -> None:
    (tmp_path / "package.json").write_text("{bad json")
    repo = Repo(path=tmp_path, stacks=("node",))
    result = NodeEnginesNode().check(repo)
    assert result.passing is True
    assert result.skipped is True


def test_pk003_metadata() -> None:
    rule = NodeEnginesNode()
    assert rule.id == "NODE_PK003"
    assert rule.severity == "recommended"
    assert "node" in rule.stacks
