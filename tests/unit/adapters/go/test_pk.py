"""Tests for Go adapter GO_PK rules."""

from __future__ import annotations

from pathlib import Path

from intendant.adapters.go.pk import GoMod, GoSum, GoVersion
from intendant.core.repo import Repo


def _repo(path: Path) -> Repo:
    return Repo(path=path, stacks=("go",))


def test_pk001_pass(tmp_path: Path) -> None:
    (tmp_path / "go.mod").write_text("module example.com/x\n\ngo 1.22\n")
    result = GoMod().check(_repo(tmp_path))
    assert result.passing is True
    assert "example.com/x" in result.evidence


def test_pk001_fail_missing(tmp_path: Path) -> None:
    result = GoMod().check(_repo(tmp_path))
    assert result.passing is False
    assert "go.mod" in result.evidence


def test_pk001_fail_no_module_directive(tmp_path: Path) -> None:
    (tmp_path / "go.mod").write_text("go 1.22\n")
    result = GoMod().check(_repo(tmp_path))
    assert result.passing is False
    assert "module" in result.evidence


def test_pk001_metadata() -> None:
    rule = GoMod()
    assert rule.id == "GO_PK001"
    assert rule.severity == "required"
    assert "go" in rule.stacks


def test_pk002_pass(tmp_path: Path) -> None:
    (tmp_path / "go.sum").write_text("# checksums\n")
    assert GoSum().check(_repo(tmp_path)).passing is True


def test_pk002_fail(tmp_path: Path) -> None:
    result = GoSum().check(_repo(tmp_path))
    assert result.passing is False
    assert "go.sum" in result.evidence


def test_pk003_pass(tmp_path: Path) -> None:
    (tmp_path / "go.mod").write_text("module x\n\ngo 1.22\n")
    result = GoVersion().check(_repo(tmp_path))
    assert result.passing is True
    assert "1.22" in result.evidence


def test_pk003_fail_no_directive(tmp_path: Path) -> None:
    (tmp_path / "go.mod").write_text("module x\n")
    result = GoVersion().check(_repo(tmp_path))
    assert result.passing is False


def test_pk003_skipped_when_go_mod_missing(tmp_path: Path) -> None:
    result = GoVersion().check(_repo(tmp_path))
    assert result.skipped is True


def test_pk003_metadata() -> None:
    rule = GoVersion()
    assert rule.id == "GO_PK003"
    assert rule.severity == "recommended"
