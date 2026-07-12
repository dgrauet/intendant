"""Tests for .NET adapter DOTNET_PK rules."""

from __future__ import annotations

from pathlib import Path

from intendant.adapters.dotnet.pk import DotnetLockfile, DotnetProject
from intendant.core.repo import Repo

_CSPROJ = """\
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <Nullable>enable</Nullable>
  </PropertyGroup>
</Project>
"""


def _repo(path: Path) -> Repo:
    return Repo(path=path, stacks=("dotnet",))


def test_pk001_pass(tmp_path: Path) -> None:
    (tmp_path / "App.csproj").write_text(_CSPROJ)
    result = DotnetProject().check(_repo(tmp_path))
    assert result.passing is True
    assert "net8.0" in result.evidence


def test_pk001_pass_nested_csproj(tmp_path: Path) -> None:
    nested = tmp_path / "src" / "App"
    nested.mkdir(parents=True)
    (nested / "App.csproj").write_text(_CSPROJ)
    assert DotnetProject().check(_repo(tmp_path)).passing is True


def test_pk001_pass_plural_target_frameworks(tmp_path: Path) -> None:
    (tmp_path / "App.csproj").write_text(
        "<Project><PropertyGroup>"
        "<TargetFrameworks>net8.0;net8.0-windows</TargetFrameworks>"
        "</PropertyGroup></Project>\n"
    )
    assert DotnetProject().check(_repo(tmp_path)).passing is True


def test_pk001_fail_missing(tmp_path: Path) -> None:
    result = DotnetProject().check(_repo(tmp_path))
    assert result.passing is False
    assert ".csproj" in result.evidence


def test_pk001_fail_no_target_framework(tmp_path: Path) -> None:
    (tmp_path / "App.csproj").write_text("<Project></Project>\n")
    result = DotnetProject().check(_repo(tmp_path))
    assert result.passing is False
    assert "TargetFramework" in result.evidence


def test_pk001_ignores_bin_obj(tmp_path: Path) -> None:
    hidden = tmp_path / "obj" / "gen"
    hidden.mkdir(parents=True)
    (hidden / "Cached.csproj").write_text(_CSPROJ)
    assert DotnetProject().check(_repo(tmp_path)).passing is False


def test_pk001_metadata() -> None:
    rule = DotnetProject()
    assert rule.id == "DOTNET_PK001"
    assert rule.severity == "required"
    assert "dotnet" in rule.stacks


def test_pk002_pass(tmp_path: Path) -> None:
    (tmp_path / "App.csproj").write_text(_CSPROJ)
    (tmp_path / "packages.lock.json").write_text("{}\n")
    assert DotnetLockfile().check(_repo(tmp_path)).passing is True


def test_pk002_pass_next_to_nested_csproj(tmp_path: Path) -> None:
    nested = tmp_path / "src" / "App"
    nested.mkdir(parents=True)
    (nested / "App.csproj").write_text(_CSPROJ)
    (nested / "packages.lock.json").write_text("{}\n")
    assert DotnetLockfile().check(_repo(tmp_path)).passing is True


def test_pk002_fail(tmp_path: Path) -> None:
    (tmp_path / "App.csproj").write_text(_CSPROJ)
    result = DotnetLockfile().check(_repo(tmp_path))
    assert result.passing is False
    assert "packages.lock.json" in result.evidence


def test_pk002_skipped_when_no_csproj(tmp_path: Path) -> None:
    result = DotnetLockfile().check(_repo(tmp_path))
    assert result.skipped is True


def test_pk002_metadata() -> None:
    rule = DotnetLockfile()
    assert rule.id == "DOTNET_PK002"
    assert rule.severity == "recommended"
