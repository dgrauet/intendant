"""Tests for skill stack detection precedence."""

from __future__ import annotations

from pathlib import Path

from suzerain.core.repo import detect_stacks


def test_detect_skill_at_depth_1(tmp_path: Path) -> None:
    (tmp_path / "SKILL.md").write_text("---\nname: foo\n---\n")
    assert detect_stacks(tmp_path) == ("claude-skill",)


def test_detect_skill_at_depth_2(tmp_path: Path) -> None:
    sub = tmp_path / "my-skill"
    sub.mkdir()
    (sub / "SKILL.md").write_text("---\nname: my-skill\n---\n")
    assert detect_stacks(tmp_path) == ("claude-skill",)


def test_both_stacks_detected_when_both_present(tmp_path: Path) -> None:
    """When both pyproject.toml and SKILL.md exist, both are returned."""
    (tmp_path / "pyproject.toml").write_text("[project]\nname='x'\n")
    sub = tmp_path / "my-skill"
    sub.mkdir()
    (sub / "SKILL.md").write_text("---\nname: my-skill\n---\n")
    detected = detect_stacks(tmp_path)
    assert "claude-skill" in detected
    assert "python" in detected


def test_python_still_detected_when_no_skill(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text("[project]\nname='x'\n")
    assert detect_stacks(tmp_path) == ("python",)


def test_no_skill_no_pyproject_falls_through(tmp_path: Path) -> None:
    assert detect_stacks(tmp_path) == ()
