"""Tests for Swift adapter SWIFT_CI001."""

from __future__ import annotations

from pathlib import Path

from suzerain.adapters.swift.ci import SWIFT_CI001MinimumSteps
from suzerain.core.repo import Repo


def _repo(path: Path) -> Repo:
    return Repo(path=path, stack="swift")


def _write_workflow(repo: Path, body: str) -> None:
    wf = repo / ".github" / "workflows"
    wf.mkdir(parents=True)
    (wf / "ci.yml").write_text(body)


def test_ci001_pass(tmp_path: Path) -> None:
    body = (
        "jobs:\n  test:\n    steps:\n"
        "      - run: swift build\n"
        "      - run: swift test\n"
        "      - run: swiftlint\n"
    )
    _write_workflow(tmp_path, body)
    result = SWIFT_CI001MinimumSteps().check(_repo(tmp_path))
    assert result.passing is True


def test_ci001_skipped_when_no_workflows(tmp_path: Path) -> None:
    result = SWIFT_CI001MinimumSteps().check(_repo(tmp_path))
    assert result.skipped is True
    assert "covered by CI001" in result.evidence


def test_ci001_fail_missing_lint(tmp_path: Path) -> None:
    _write_workflow(
        tmp_path, "jobs:\n  t:\n    steps:\n      - run: swift build\n      - run: swift test\n"
    )
    result = SWIFT_CI001MinimumSteps().check(_repo(tmp_path))
    assert result.passing is False
    assert "lint" in result.evidence


def test_ci001_fail_missing_test(tmp_path: Path) -> None:
    _write_workflow(
        tmp_path, "jobs:\n  t:\n    steps:\n      - run: swift build\n      - run: swiftlint\n"
    )
    result = SWIFT_CI001MinimumSteps().check(_repo(tmp_path))
    assert result.passing is False
    assert "swift test" in result.evidence or "test" in result.evidence


def test_ci001_metadata() -> None:
    rule = SWIFT_CI001MinimumSteps()
    assert rule.id == "SWIFT_CI001"
    assert rule.severity == "required"
    assert "swift" in rule.stacks
