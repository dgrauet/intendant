"""Tests for skill adapter SK rules."""

from __future__ import annotations

from pathlib import Path

from suzerain.core.repo import Repo


def _skill_repo(path: Path) -> Repo:
    return Repo(path=path, stack="skill")


def _make_skill(tmp_path: Path, body: str) -> Path:
    """Create a `my-skill/SKILL.md` with the given body and return tmp_path."""
    sub = tmp_path / "my-skill"
    sub.mkdir()
    (sub / "SKILL.md").write_text(body)
    return tmp_path


def test_sk001_passes_when_skill_md_exists(tmp_path: Path) -> None:
    from suzerain.adapters.skill.sk import SK001SkillMdExists

    sub = tmp_path / "my-skill"
    sub.mkdir()
    (sub / "SKILL.md").write_text("---\nname: my-skill\n---\nbody\n")
    result = SK001SkillMdExists().check(_skill_repo(tmp_path))
    assert result.passing is True
    assert "my-skill/SKILL.md" in result.evidence


def test_sk001_fails_when_no_skill_md(tmp_path: Path) -> None:
    from suzerain.adapters.skill.sk import SK001SkillMdExists

    result = SK001SkillMdExists().check(_skill_repo(tmp_path))
    assert result.passing is False
    assert "no SKILL.md found" in result.evidence
