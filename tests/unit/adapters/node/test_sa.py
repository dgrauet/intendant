"""Tests for Node adapter SA rules."""

from pathlib import Path

from suzerain.adapters.node.sa import NODE_SA001GitignoreBaseline
from suzerain.core.repo import Repo


def test_node_sa001_skipped_when_no_gitignore(tmp_path: Path) -> None:
    repo = Repo(path=tmp_path, stack="node")
    result = NODE_SA001GitignoreBaseline().check(repo)
    assert result.passing is True
    assert result.skipped is True
    assert "SA004" in result.evidence


def test_node_sa001_passes_when_baseline_present(tmp_path: Path) -> None:
    (tmp_path / ".gitignore").write_text("node_modules/\n.DS_Store\ndist/\n")
    repo = Repo(path=tmp_path, stack="node")
    result = NODE_SA001GitignoreBaseline().check(repo)
    assert result.passing is True
    assert "Node baseline" in result.evidence


def test_node_sa001_fails_when_node_modules_missing(tmp_path: Path) -> None:
    (tmp_path / ".gitignore").write_text(".DS_Store\ndist/\n")
    repo = Repo(path=tmp_path, stack="node")
    result = NODE_SA001GitignoreBaseline().check(repo)
    assert result.passing is False
    assert "node_modules/" in result.evidence


def test_node_sa001_fails_when_dist_missing(tmp_path: Path) -> None:
    (tmp_path / ".gitignore").write_text("node_modules/\n.DS_Store\n")
    repo = Repo(path=tmp_path, stack="node")
    result = NODE_SA001GitignoreBaseline().check(repo)
    assert result.passing is False
    assert "dist/" in result.evidence


def test_node_sa001_fails_when_both_missing(tmp_path: Path) -> None:
    (tmp_path / ".gitignore").write_text(".DS_Store\n")
    repo = Repo(path=tmp_path, stack="node")
    result = NODE_SA001GitignoreBaseline().check(repo)
    assert result.passing is False
    assert "node_modules/" in result.evidence or "dist/" in result.evidence


def test_node_sa001_metadata() -> None:
    rule = NODE_SA001GitignoreBaseline()
    assert rule.id == "NODE_SA001"
    assert rule.severity == "required"
    assert "node" in rule.stacks
