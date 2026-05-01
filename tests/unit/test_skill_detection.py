"""Tests for skill stack detection precedence."""

from __future__ import annotations

from pathlib import Path

from suzerain.core.repo import detect_stack


def test_detect_skill_at_depth_1(tmp_path: Path) -> None:
    (tmp_path / "SKILL.md").write_text("---\nname: foo\n---\n")
    assert detect_stack(tmp_path) == "skill"


def test_detect_skill_at_depth_2(tmp_path: Path) -> None:
    sub = tmp_path / "my-skill"
    sub.mkdir()
    (sub / "SKILL.md").write_text("---\nname: my-skill\n---\n")
    assert detect_stack(tmp_path) == "skill"


def test_skill_takes_precedence_over_python(tmp_path: Path) -> None:
    """When both pyproject.toml and SKILL.md exist, skill wins."""
    (tmp_path / "pyproject.toml").write_text("[project]\nname='x'\n")
    sub = tmp_path / "my-skill"
    sub.mkdir()
    (sub / "SKILL.md").write_text("---\nname: my-skill\n---\n")
    assert detect_stack(tmp_path) == "skill"


def test_python_still_detected_when_no_skill(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text("[project]\nname='x'\n")
    assert detect_stack(tmp_path) == "python"


def test_no_skill_no_pyproject_falls_through(tmp_path: Path) -> None:
    assert detect_stack(tmp_path) is None
