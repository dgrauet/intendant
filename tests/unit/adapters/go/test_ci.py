"""Tests for Go adapter GO_CI rules."""

from __future__ import annotations

from pathlib import Path

from intendant.adapters.go.ci import GO_CI001MinimumSteps
from intendant.core.repo import Repo


def _repo(path: Path) -> Repo:
    return Repo(path=path, stacks=("go",))


def _wf(tmp_path: Path, body: str) -> None:
    wf_dir = tmp_path / ".github" / "workflows"
    wf_dir.mkdir(parents=True)
    (wf_dir / "ci.yml").write_text(body)


def test_ci001_pass(tmp_path: Path) -> None:
    _wf(
        tmp_path,
        "jobs:\n  go:\n    steps:\n"
        "      - run: go vet ./...\n"
        "      - run: go test ./...\n"
        "      - uses: golangci/golangci-lint-action@v6\n",
    )
    assert GO_CI001MinimumSteps().check(_repo(tmp_path)).passing is True


def test_ci001_pass_with_gofmt_lint(tmp_path: Path) -> None:
    _wf(
        tmp_path,
        "jobs:\n  go:\n    steps:\n"
        "      - run: go build ./...\n"
        "      - run: go test ./...\n"
        "      - run: gofmt -l .\n",
    )
    assert GO_CI001MinimumSteps().check(_repo(tmp_path)).passing is True


def test_ci001_fail_missing_lint(tmp_path: Path) -> None:
    _wf(
        tmp_path,
        "jobs:\n  go:\n    steps:\n      - run: go vet ./...\n      - run: go test ./...\n",
    )
    result = GO_CI001MinimumSteps().check(_repo(tmp_path))
    assert result.passing is False
    assert "lint" in result.evidence


def test_ci001_skipped_when_no_workflows(tmp_path: Path) -> None:
    assert GO_CI001MinimumSteps().check(_repo(tmp_path)).skipped is True


def test_ci001_metadata() -> None:
    rule = GO_CI001MinimumSteps()
    assert rule.id == "GO_CI001"
    assert rule.severity == "required"
