"""Tests for .NET adapter DOTNET_QU, DOTNET_TS, and DOTNET_SA rules."""

from __future__ import annotations

from pathlib import Path

from intendant.adapters.dotnet.qu import DotnetEditorconfig, DotnetNullable
from intendant.adapters.dotnet.sa import DOTNET_SA001GitignoreBaseline
from intendant.adapters.dotnet.ts import DotnetTestProject
from intendant.core.repo import Repo

_CSPROJ_NULLABLE = """\
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <Nullable>enable</Nullable>
  </PropertyGroup>
</Project>
"""

_CSPROJ_NO_NULLABLE = """\
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
  </PropertyGroup>
</Project>
"""

_CSPROJ_TESTS = """\
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <Nullable>enable</Nullable>
  </PropertyGroup>
  <ItemGroup>
    <PackageReference Include="Microsoft.NET.Test.Sdk" Version="17.9.0" />
    <PackageReference Include="xunit" Version="2.7.0" />
  </ItemGroup>
</Project>
"""


def _repo(path: Path) -> Repo:
    return Repo(path=path, stacks=("dotnet",))


# --- DOTNET_QU001 (Nullable) ---


def test_qu001_pass(tmp_path: Path) -> None:
    (tmp_path / "App.csproj").write_text(_CSPROJ_NULLABLE)
    result = DotnetNullable().check(_repo(tmp_path))
    assert result.passing is True


def test_qu001_fail(tmp_path: Path) -> None:
    (tmp_path / "App.csproj").write_text(_CSPROJ_NO_NULLABLE)
    result = DotnetNullable().check(_repo(tmp_path))
    assert result.passing is False
    assert "Nullable" in result.evidence
    assert "App.csproj" in result.evidence


def test_qu001_pass_via_directory_build_props(tmp_path: Path) -> None:
    (tmp_path / "Directory.Build.props").write_text(
        "<Project><PropertyGroup><Nullable>enable</Nullable></PropertyGroup></Project>\n"
    )
    nested = tmp_path / "src" / "App"
    nested.mkdir(parents=True)
    (nested / "App.csproj").write_text(_CSPROJ_NO_NULLABLE)
    assert DotnetNullable().check(_repo(tmp_path)).passing is True


def test_qu001_skipped_when_no_csproj(tmp_path: Path) -> None:
    assert DotnetNullable().check(_repo(tmp_path)).skipped is True


def test_qu001_metadata() -> None:
    rule = DotnetNullable()
    assert rule.id == "DOTNET_QU001"
    assert rule.severity == "required"
    assert "dotnet" in rule.stacks


# --- DOTNET_QU002 (.editorconfig) ---


def test_qu002_pass(tmp_path: Path) -> None:
    (tmp_path / ".editorconfig").write_text("root = true\n")
    assert DotnetEditorconfig().check(_repo(tmp_path)).passing is True


def test_qu002_fail(tmp_path: Path) -> None:
    result = DotnetEditorconfig().check(_repo(tmp_path))
    assert result.passing is False
    assert ".editorconfig" in result.evidence


def test_qu002_metadata() -> None:
    rule = DotnetEditorconfig()
    assert rule.id == "DOTNET_QU002"
    assert rule.severity == "recommended"


# --- DOTNET_TS001 (test project) ---


def test_ts001_pass(tmp_path: Path) -> None:
    tests = tmp_path / "App.Tests"
    tests.mkdir()
    (tests / "App.Tests.csproj").write_text(_CSPROJ_TESTS)
    result = DotnetTestProject().check(_repo(tmp_path))
    assert result.passing is True
    assert "App.Tests" in result.evidence


def test_ts001_fail_no_test_project(tmp_path: Path) -> None:
    (tmp_path / "App.csproj").write_text(_CSPROJ_NULLABLE)
    result = DotnetTestProject().check(_repo(tmp_path))
    assert result.passing is False


def test_ts001_metadata() -> None:
    rule = DotnetTestProject()
    assert rule.id == "DOTNET_TS001"
    assert rule.severity == "recommended"


# --- DOTNET_SA001 (.gitignore baseline) ---


def test_sa001_pass(tmp_path: Path) -> None:
    (tmp_path / ".gitignore").write_text("bin/\nobj/\n")
    assert DOTNET_SA001GitignoreBaseline().check(_repo(tmp_path)).passing is True


def test_sa001_pass_bracket_variants(tmp_path: Path) -> None:
    (tmp_path / ".gitignore").write_text("[Bb]in/\n[Oo]bj/\n")
    assert DOTNET_SA001GitignoreBaseline().check(_repo(tmp_path)).passing is True


def test_sa001_fail_missing_patterns(tmp_path: Path) -> None:
    (tmp_path / ".gitignore").write_text(".DS_Store\n")
    result = DOTNET_SA001GitignoreBaseline().check(_repo(tmp_path))
    assert result.passing is False
    assert "bin/" in result.evidence


def test_sa001_skipped_when_no_gitignore(tmp_path: Path) -> None:
    assert DOTNET_SA001GitignoreBaseline().check(_repo(tmp_path)).skipped is True


def test_sa001_metadata() -> None:
    rule = DOTNET_SA001GitignoreBaseline()
    assert rule.id == "DOTNET_SA001"
    assert rule.severity == "required"
