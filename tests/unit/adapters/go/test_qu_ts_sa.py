"""Tests for Go QU/TS/SA rules."""

from __future__ import annotations

from pathlib import Path

import pytest

from intendant.adapters.go.qu import GoLinter
from intendant.adapters.go.sa import GO_SA001GitignoreBaseline
from intendant.adapters.go.ts import GoTestFiles
from intendant.core.repo import Repo


def _repo(path: Path) -> Repo:
    return Repo(path=path, stacks=("go",))


@pytest.mark.parametrize(
    "name", [".golangci.yml", ".golangci.yaml", ".golangci.toml", ".golangci.json"]
)
def test_qu001_pass_each_extension(tmp_path: Path, name: str) -> None:
    (tmp_path / name).write_text("linters: {}\n")
    assert GoLinter().check(_repo(tmp_path)).passing is True


def test_qu001_fail_missing(tmp_path: Path) -> None:
    result = GoLinter().check(_repo(tmp_path))
    assert result.passing is False
    assert "golangci" in result.evidence


def test_qu001_metadata() -> None:
    rule = GoLinter()
    assert rule.id == "GO_QU001"
    assert rule.severity == "recommended"


def test_ts001_pass(tmp_path: Path) -> None:
    (tmp_path / "x_test.go").write_text(
        'package x\nimport "testing"\nfunc TestThing(t *testing.T) {}\n'
    )
    result = GoTestFiles().check(_repo(tmp_path))
    assert result.passing is True


def test_ts001_fail(tmp_path: Path) -> None:
    (tmp_path / "main.go").write_text("package main\n")
    assert GoTestFiles().check(_repo(tmp_path)).passing is False


def test_ts001_metadata() -> None:
    rule = GoTestFiles()
    assert rule.id == "GO_TS001"
    assert rule.severity == "recommended"


def test_sa001_pass(tmp_path: Path) -> None:
    (tmp_path / ".gitignore").write_text("*.test\n*.out\n")
    assert GO_SA001GitignoreBaseline().check(_repo(tmp_path)).passing is True


def test_sa001_fail_missing_pattern(tmp_path: Path) -> None:
    (tmp_path / ".gitignore").write_text("*.out\n")
    result = GO_SA001GitignoreBaseline().check(_repo(tmp_path))
    assert result.passing is False
    assert "*.test" in result.evidence


def test_sa001_skipped_when_gitignore_missing(tmp_path: Path) -> None:
    result = GO_SA001GitignoreBaseline().check(_repo(tmp_path))
    assert result.skipped is True


def test_sa001_metadata() -> None:
    rule = GO_SA001GitignoreBaseline()
    assert rule.id == "GO_SA001"
    assert rule.severity == "required"
