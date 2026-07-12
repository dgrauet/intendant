"""Tests for .NET adapter DOTNET_CI rules."""

from __future__ import annotations

from pathlib import Path

from intendant.adapters.dotnet.ci import DOTNET_CI001MinimumSteps
from intendant.core.repo import Repo


def _repo(path: Path) -> Repo:
    return Repo(path=path, stacks=("dotnet",))


def _write_workflow(path: Path, body: str) -> None:
    wf_dir = path / ".github" / "workflows"
    wf_dir.mkdir(parents=True)
    (wf_dir / "ci.yml").write_text(body)


def test_ci001_pass(tmp_path: Path) -> None:
    _write_workflow(
        tmp_path,
        "jobs:\n  windows:\n    steps:\n"
        "      - run: dotnet format --verify-no-changes\n"
        "      - run: dotnet build\n"
        "      - run: dotnet test\n",
    )
    result = DOTNET_CI001MinimumSteps().check(_repo(tmp_path))
    assert result.passing is True


def test_ci001_fail_build_only(tmp_path: Path) -> None:
    _write_workflow(tmp_path, "jobs:\n  windows:\n    steps:\n      - run: dotnet build\n")
    result = DOTNET_CI001MinimumSteps().check(_repo(tmp_path))
    assert result.passing is False
    assert "test" in result.evidence
    assert "format" in result.evidence


def test_ci001_skipped_when_no_workflows_dir(tmp_path: Path) -> None:
    result = DOTNET_CI001MinimumSteps().check(_repo(tmp_path))
    assert result.skipped is True


def test_ci001_metadata() -> None:
    rule = DOTNET_CI001MinimumSteps()
    assert rule.id == "DOTNET_CI001"
    assert rule.severity == "required"
    assert "dotnet" in rule.stacks
