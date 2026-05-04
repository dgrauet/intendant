"""Tests for Rust adapter RUST_CI rules."""

from __future__ import annotations

from pathlib import Path

from suzerain.adapters.rust.ci import RUST_CI001MinimumSteps
from suzerain.core.repo import Repo


def _repo(path: Path) -> Repo:
    return Repo(path=path, stacks=("rust",))


def _wf(tmp_path: Path, body: str) -> None:
    wf_dir = tmp_path / ".github" / "workflows"
    wf_dir.mkdir(parents=True)
    (wf_dir / "ci.yml").write_text(body)


def test_ci001_pass(tmp_path: Path) -> None:
    _wf(
        tmp_path,
        "jobs:\n  rust:\n    steps:\n"
        "      - run: cargo fmt --check\n"
        "      - run: cargo clippy -- -D warnings\n"
        "      - run: cargo test\n",
    )
    assert RUST_CI001MinimumSteps().check(_repo(tmp_path)).passing is True


def test_ci001_pass_with_nextest(tmp_path: Path) -> None:
    _wf(
        tmp_path,
        "jobs:\n  rust:\n    steps:\n"
        "      - run: cargo fmt --check\n"
        "      - run: cargo clippy\n"
        "      - run: cargo nextest run\n",
    )
    assert RUST_CI001MinimumSteps().check(_repo(tmp_path)).passing is True


def test_ci001_fail_missing_clippy(tmp_path: Path) -> None:
    _wf(
        tmp_path,
        "jobs:\n  rust:\n    steps:\n      - run: cargo fmt\n      - run: cargo test\n",
    )
    result = RUST_CI001MinimumSteps().check(_repo(tmp_path))
    assert result.passing is False
    assert "clippy" in result.evidence


def test_ci001_fail_missing_all(tmp_path: Path) -> None:
    _wf(tmp_path, "jobs:\n  noop:\n    steps:\n      - run: echo hi\n")
    result = RUST_CI001MinimumSteps().check(_repo(tmp_path))
    assert result.passing is False


def test_ci001_skipped_when_no_workflows(tmp_path: Path) -> None:
    result = RUST_CI001MinimumSteps().check(_repo(tmp_path))
    assert result.skipped is True


def test_ci001_metadata() -> None:
    rule = RUST_CI001MinimumSteps()
    assert rule.id == "RUST_CI001"
    assert rule.severity == "required"
