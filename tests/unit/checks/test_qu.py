"""Tests for QU (quality coherence) transverse rules."""

from pathlib import Path

from intendant.checks.qu import QU001ConfiguredToolsRunInCI
from intendant.core.repo import Repo


def _repo(path: Path) -> Repo:
    return Repo(path=path, stacks=("python",))


def _write_wf(path: Path, body: str) -> None:
    wf = path / ".github" / "workflows"
    wf.mkdir(parents=True, exist_ok=True)
    (wf / "ci.yml").write_text(body)


def test_qu001_fail_swiftformat_config_never_run(tmp_path: Path) -> None:
    """The champinium case: a nested .swiftformat that no workflow executes."""
    _write_wf(tmp_path, "jobs:\n  mac:\n    steps:\n      - run: swift build\n")
    mac = tmp_path / "apps" / "macos"
    mac.mkdir(parents=True)
    (mac / ".swiftformat").write_text("--indent 4\n")
    result = QU001ConfiguredToolsRunInCI().check(_repo(tmp_path))
    assert result.passing is False
    assert "swiftformat" in result.evidence
    assert "apps/macos" in result.evidence


def test_qu001_pass_swiftformat_run_in_ci(tmp_path: Path) -> None:
    _write_wf(tmp_path, "jobs:\n  mac:\n    steps:\n      - run: swiftformat --lint .\n")
    (tmp_path / ".swiftformat").write_text("--indent 4\n")
    assert QU001ConfiguredToolsRunInCI().check(_repo(tmp_path)).passing is True


def test_qu001_fail_ruff_configured_not_run(tmp_path: Path) -> None:
    _write_wf(tmp_path, "jobs:\n  a:\n    steps:\n      - run: pytest\n")
    (tmp_path / "pyproject.toml").write_text("[tool.ruff]\nline-length = 100\n")
    result = QU001ConfiguredToolsRunInCI().check(_repo(tmp_path))
    assert result.passing is False
    assert "ruff" in result.evidence


def test_qu001_pass_ruff_run_in_ci(tmp_path: Path) -> None:
    _write_wf(tmp_path, "jobs:\n  a:\n    steps:\n      - run: uv run ruff check .\n")
    (tmp_path / "pyproject.toml").write_text("[tool.ruff]\nline-length = 100\n")
    assert QU001ConfiguredToolsRunInCI().check(_repo(tmp_path)).passing is True


def test_qu001_pass_deny_toml_with_cargo_deny_action(tmp_path: Path) -> None:
    _write_wf(
        tmp_path,
        "jobs:\n  deny:\n    steps:\n      - uses: EmbarkStudios/cargo-deny-action@abc\n",
    )
    (tmp_path / "deny.toml").write_text("[advisories]\n")
    assert QU001ConfiguredToolsRunInCI().check(_repo(tmp_path)).passing is True


def test_qu001_ignores_configs_in_build_dirs(tmp_path: Path) -> None:
    _write_wf(tmp_path, "jobs:\n  a:\n    steps:\n      - run: echo ok\n")
    dep = tmp_path / "node_modules" / "pkg"
    dep.mkdir(parents=True)
    (dep / ".swiftformat").write_text("--indent 4\n")
    assert QU001ConfiguredToolsRunInCI().check(_repo(tmp_path)).passing is True


def test_qu001_pass_no_known_configs(tmp_path: Path) -> None:
    _write_wf(tmp_path, "jobs:\n  a:\n    steps:\n      - run: echo ok\n")
    assert QU001ConfiguredToolsRunInCI().check(_repo(tmp_path)).passing is True


def test_qu001_skipped_when_no_workflows_dir(tmp_path: Path) -> None:
    (tmp_path / ".swiftformat").write_text("--indent 4\n")
    assert QU001ConfiguredToolsRunInCI().check(_repo(tmp_path)).skipped is True


def test_qu001_metadata() -> None:
    rule = QU001ConfiguredToolsRunInCI()
    assert rule.id == "QU001"
    assert rule.severity == "recommended"
    assert rule.stacks == ("*",)
