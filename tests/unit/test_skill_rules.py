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


def test_sk002_passes_with_valid_frontmatter(tmp_path: Path) -> None:
    from suzerain.adapters.skill.sk import SK002FrontmatterValid

    repo = _make_skill(tmp_path, "---\nname: my-skill\ndescription: useful tool\n---\nbody\n")
    result = SK002FrontmatterValid().check(_skill_repo(repo))
    assert result.passing is True
    assert "name='my-skill'" in result.evidence


def test_sk002_fails_when_no_frontmatter(tmp_path: Path) -> None:
    from suzerain.adapters.skill.sk import SK002FrontmatterValid

    repo = _make_skill(tmp_path, "# just a body\nno frontmatter\n")
    result = SK002FrontmatterValid().check(_skill_repo(repo))
    assert result.passing is False
    assert "no frontmatter block found" in result.evidence


def test_sk002_fails_when_yaml_broken(tmp_path: Path) -> None:
    from suzerain.adapters.skill.sk import SK002FrontmatterValid

    repo = _make_skill(tmp_path, "---\nkey: [unclosed\n---\nbody\n")
    result = SK002FrontmatterValid().check(_skill_repo(repo))
    assert result.passing is False
    assert "YAML parse error" in result.evidence


def test_sk002_fails_when_name_missing(tmp_path: Path) -> None:
    from suzerain.adapters.skill.sk import SK002FrontmatterValid

    repo = _make_skill(tmp_path, "---\ndescription: x\n---\nbody\n")
    result = SK002FrontmatterValid().check(_skill_repo(repo))
    assert result.passing is False
    assert "missing required field: name" in result.evidence


def test_sk002_fails_when_description_missing(tmp_path: Path) -> None:
    from suzerain.adapters.skill.sk import SK002FrontmatterValid

    repo = _make_skill(tmp_path, "---\nname: foo\n---\nbody\n")
    result = SK002FrontmatterValid().check(_skill_repo(repo))
    assert result.passing is False
    assert "missing required field: description" in result.evidence


def test_sk002_fails_when_name_empty(tmp_path: Path) -> None:
    from suzerain.adapters.skill.sk import SK002FrontmatterValid

    repo = _make_skill(tmp_path, '---\nname: ""\ndescription: x\n---\nbody\n')
    result = SK002FrontmatterValid().check(_skill_repo(repo))
    assert result.passing is False
    assert "field 'name' is empty" in result.evidence


def test_sk002_fails_when_description_empty(tmp_path: Path) -> None:
    from suzerain.adapters.skill.sk import SK002FrontmatterValid

    repo = _make_skill(tmp_path, '---\nname: foo\ndescription: ""\n---\nbody\n')
    result = SK002FrontmatterValid().check(_skill_repo(repo))
    assert result.passing is False
    assert "field 'description' is empty" in result.evidence


def test_sk002_fails_when_no_skill_md(tmp_path: Path) -> None:
    from suzerain.adapters.skill.sk import SK002FrontmatterValid

    result = SK002FrontmatterValid().check(_skill_repo(tmp_path))
    assert result.passing is False


def test_sk003_passes_with_normal_description(tmp_path: Path) -> None:
    from suzerain.adapters.skill.sk import SK003DescriptionQuality

    repo = _make_skill(
        tmp_path,
        "---\nname: foo\ndescription: a useful skill that does X\n---\nbody\n",
    )
    result = SK003DescriptionQuality().check(_skill_repo(repo))
    assert result.passing is True
    assert "description length:" in result.evidence


def test_sk003_fails_when_description_too_short(tmp_path: Path) -> None:
    from suzerain.adapters.skill.sk import SK003DescriptionQuality

    repo = _make_skill(tmp_path, "---\nname: foo\ndescription: hi\n---\nbody\n")
    result = SK003DescriptionQuality().check(_skill_repo(repo))
    assert result.passing is False
    assert "too short" in result.evidence


def test_sk003_fails_when_description_too_long(tmp_path: Path) -> None:
    from suzerain.adapters.skill.sk import SK003DescriptionQuality

    long_desc = "x" * 1100
    repo = _make_skill(tmp_path, f"---\nname: foo\ndescription: {long_desc}\n---\nbody\n")
    result = SK003DescriptionQuality().check(_skill_repo(repo))
    assert result.passing is False
    assert "too long" in result.evidence


def test_sk003_skipped_when_frontmatter_invalid(tmp_path: Path) -> None:
    from suzerain.adapters.skill.sk import SK003DescriptionQuality

    repo = _make_skill(tmp_path, "no frontmatter at all\n")
    result = SK003DescriptionQuality().check(_skill_repo(repo))
    assert result.skipped is True


def test_sk004_passes_when_name_matches_dir(tmp_path: Path) -> None:
    from suzerain.adapters.skill.sk import SK004NameMatchesDir

    repo = _make_skill(tmp_path, "---\nname: my-skill\ndescription: x\n---\n")
    result = SK004NameMatchesDir().check(_skill_repo(repo))
    assert result.passing is True
    assert "my-skill" in result.evidence


def test_sk004_fails_when_name_differs_from_dir(tmp_path: Path) -> None:
    from suzerain.adapters.skill.sk import SK004NameMatchesDir

    repo = _make_skill(tmp_path, "---\nname: other-name\ndescription: x\n---\n")
    result = SK004NameMatchesDir().check(_skill_repo(repo))
    assert result.passing is False
    assert "other-name" in result.evidence
    assert "my-skill" in result.evidence


def test_sk004_skipped_when_no_skill_md(tmp_path: Path) -> None:
    from suzerain.adapters.skill.sk import SK004NameMatchesDir

    result = SK004NameMatchesDir().check(_skill_repo(tmp_path))
    assert result.skipped is True


def test_sk004_skipped_when_name_missing(tmp_path: Path) -> None:
    from suzerain.adapters.skill.sk import SK004NameMatchesDir

    repo = _make_skill(tmp_path, "---\ndescription: x\n---\n")
    result = SK004NameMatchesDir().check(_skill_repo(repo))
    assert result.skipped is True


def test_sk005_passes_when_evals_dir_has_files(tmp_path: Path) -> None:
    from suzerain.adapters.skill.sk import SK005EvalsNonEmpty

    repo = _make_skill(tmp_path, "---\nname: my-skill\ndescription: x\n---\n")
    evals = repo / "my-skill" / "evals"
    evals.mkdir()
    (evals / "case-1.md").write_text("- input: foo\n- expected: bar\n")
    result = SK005EvalsNonEmpty().check(_skill_repo(repo))
    assert result.passing is True
    assert "1 file" in result.evidence


def test_sk005_fails_when_evals_dir_missing(tmp_path: Path) -> None:
    from suzerain.adapters.skill.sk import SK005EvalsNonEmpty

    repo = _make_skill(tmp_path, "---\nname: my-skill\ndescription: x\n---\n")
    result = SK005EvalsNonEmpty().check(_skill_repo(repo))
    assert result.passing is False
    assert "missing" in result.evidence


def test_sk005_fails_when_evals_dir_empty(tmp_path: Path) -> None:
    from suzerain.adapters.skill.sk import SK005EvalsNonEmpty

    repo = _make_skill(tmp_path, "---\nname: my-skill\ndescription: x\n---\n")
    (repo / "my-skill" / "evals").mkdir()
    result = SK005EvalsNonEmpty().check(_skill_repo(repo))
    assert result.passing is False
    assert "empty" in result.evidence


def test_sk005_ignores_non_eval_extensions(tmp_path: Path) -> None:
    from suzerain.adapters.skill.sk import SK005EvalsNonEmpty

    repo = _make_skill(tmp_path, "---\nname: my-skill\ndescription: x\n---\n")
    evals = repo / "my-skill" / "evals"
    evals.mkdir()
    (evals / "ignored.png").write_bytes(b"\x89PNG\r\n")
    result = SK005EvalsNonEmpty().check(_skill_repo(repo))
    assert result.passing is False
    assert "empty" in result.evidence


def test_sk005_skipped_when_no_skill_md(tmp_path: Path) -> None:
    from suzerain.adapters.skill.sk import SK005EvalsNonEmpty

    result = SK005EvalsNonEmpty().check(_skill_repo(tmp_path))
    assert result.skipped is True
