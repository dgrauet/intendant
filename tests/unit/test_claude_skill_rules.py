"""Tests for skill adapter SK rules."""

from __future__ import annotations

from pathlib import Path

from suzerain.core.repo import Repo


def _skill_repo(path: Path) -> Repo:
    return Repo(path=path, stack="claude-skill")


def _make_skill(tmp_path: Path, body: str) -> Path:
    """Create a `my-skill/SKILL.md` with the given body and return tmp_path."""
    sub = tmp_path / "my-skill"
    sub.mkdir()
    (sub / "SKILL.md").write_text(body)
    return tmp_path


def test_sk001_passes_when_skill_md_exists(tmp_path: Path) -> None:
    from suzerain.adapters.claude_skill.sk import SK001SkillMdExists

    sub = tmp_path / "my-skill"
    sub.mkdir()
    (sub / "SKILL.md").write_text("---\nname: my-skill\n---\nbody\n")
    result = SK001SkillMdExists().check(_skill_repo(tmp_path))
    assert result.passing is True
    assert "my-skill/SKILL.md" in result.evidence


def test_sk001_fails_when_no_skill_md(tmp_path: Path) -> None:
    from suzerain.adapters.claude_skill.sk import SK001SkillMdExists

    result = SK001SkillMdExists().check(_skill_repo(tmp_path))
    assert result.passing is False
    assert "no SKILL.md found" in result.evidence


def test_sk002_passes_with_valid_frontmatter(tmp_path: Path) -> None:
    from suzerain.adapters.claude_skill.sk import SK002FrontmatterValid

    repo = _make_skill(tmp_path, "---\nname: my-skill\ndescription: useful tool\n---\nbody\n")
    result = SK002FrontmatterValid().check(_skill_repo(repo))
    assert result.passing is True
    assert "name='my-skill'" in result.evidence


def test_sk002_fails_when_no_frontmatter(tmp_path: Path) -> None:
    from suzerain.adapters.claude_skill.sk import SK002FrontmatterValid

    repo = _make_skill(tmp_path, "# just a body\nno frontmatter\n")
    result = SK002FrontmatterValid().check(_skill_repo(repo))
    assert result.passing is False
    assert "no frontmatter block found" in result.evidence


def test_sk002_fails_when_yaml_broken(tmp_path: Path) -> None:
    from suzerain.adapters.claude_skill.sk import SK002FrontmatterValid

    repo = _make_skill(tmp_path, "---\nkey: [unclosed\n---\nbody\n")
    result = SK002FrontmatterValid().check(_skill_repo(repo))
    assert result.passing is False
    assert "YAML parse error" in result.evidence


def test_sk002_fails_when_name_missing(tmp_path: Path) -> None:
    from suzerain.adapters.claude_skill.sk import SK002FrontmatterValid

    repo = _make_skill(tmp_path, "---\ndescription: x\n---\nbody\n")
    result = SK002FrontmatterValid().check(_skill_repo(repo))
    assert result.passing is False
    assert "missing required field: name" in result.evidence


def test_sk002_fails_when_description_missing(tmp_path: Path) -> None:
    from suzerain.adapters.claude_skill.sk import SK002FrontmatterValid

    repo = _make_skill(tmp_path, "---\nname: foo\n---\nbody\n")
    result = SK002FrontmatterValid().check(_skill_repo(repo))
    assert result.passing is False
    assert "missing required field: description" in result.evidence


def test_sk002_fails_when_name_empty(tmp_path: Path) -> None:
    from suzerain.adapters.claude_skill.sk import SK002FrontmatterValid

    repo = _make_skill(tmp_path, '---\nname: ""\ndescription: x\n---\nbody\n')
    result = SK002FrontmatterValid().check(_skill_repo(repo))
    assert result.passing is False
    assert "field 'name' is empty" in result.evidence


def test_sk002_fails_when_description_empty(tmp_path: Path) -> None:
    from suzerain.adapters.claude_skill.sk import SK002FrontmatterValid

    repo = _make_skill(tmp_path, '---\nname: foo\ndescription: ""\n---\nbody\n')
    result = SK002FrontmatterValid().check(_skill_repo(repo))
    assert result.passing is False
    assert "field 'description' is empty" in result.evidence


def test_sk002_fails_when_no_skill_md(tmp_path: Path) -> None:
    from suzerain.adapters.claude_skill.sk import SK002FrontmatterValid

    result = SK002FrontmatterValid().check(_skill_repo(tmp_path))
    assert result.passing is False


def test_sk003_passes_with_normal_description(tmp_path: Path) -> None:
    from suzerain.adapters.claude_skill.sk import SK003DescriptionQuality

    repo = _make_skill(
        tmp_path,
        "---\nname: foo\ndescription: a useful skill that does X\n---\nbody\n",
    )
    result = SK003DescriptionQuality().check(_skill_repo(repo))
    assert result.passing is True
    assert "description length:" in result.evidence


def test_sk003_fails_when_description_too_short(tmp_path: Path) -> None:
    from suzerain.adapters.claude_skill.sk import SK003DescriptionQuality

    repo = _make_skill(tmp_path, "---\nname: foo\ndescription: hi\n---\nbody\n")
    result = SK003DescriptionQuality().check(_skill_repo(repo))
    assert result.passing is False
    assert "too short" in result.evidence


def test_sk003_fails_when_description_too_long(tmp_path: Path) -> None:
    from suzerain.adapters.claude_skill.sk import SK003DescriptionQuality

    long_desc = "x" * 1100
    repo = _make_skill(tmp_path, f"---\nname: foo\ndescription: {long_desc}\n---\nbody\n")
    result = SK003DescriptionQuality().check(_skill_repo(repo))
    assert result.passing is False
    assert "too long" in result.evidence


def test_sk003_skipped_when_frontmatter_invalid(tmp_path: Path) -> None:
    from suzerain.adapters.claude_skill.sk import SK003DescriptionQuality

    repo = _make_skill(tmp_path, "no frontmatter at all\n")
    result = SK003DescriptionQuality().check(_skill_repo(repo))
    assert result.skipped is True


def test_sk003_skipped_when_no_skill_md(tmp_path: Path) -> None:
    from suzerain.adapters.claude_skill.sk import SK003DescriptionQuality

    result = SK003DescriptionQuality().check(_skill_repo(tmp_path))
    assert result.skipped is True


def test_sk004_passes_when_name_matches_dir(tmp_path: Path) -> None:
    from suzerain.adapters.claude_skill.sk import SK004NameMatchesDir

    repo = _make_skill(tmp_path, "---\nname: my-skill\ndescription: x\n---\n")
    result = SK004NameMatchesDir().check(_skill_repo(repo))
    assert result.passing is True
    assert "my-skill" in result.evidence


def test_sk004_fails_when_name_differs_from_dir(tmp_path: Path) -> None:
    from suzerain.adapters.claude_skill.sk import SK004NameMatchesDir

    repo = _make_skill(tmp_path, "---\nname: other-name\ndescription: x\n---\n")
    result = SK004NameMatchesDir().check(_skill_repo(repo))
    assert result.passing is False
    assert "other-name" in result.evidence
    assert "my-skill" in result.evidence


def test_sk004_skipped_when_no_skill_md(tmp_path: Path) -> None:
    from suzerain.adapters.claude_skill.sk import SK004NameMatchesDir

    result = SK004NameMatchesDir().check(_skill_repo(tmp_path))
    assert result.skipped is True


def test_sk004_skipped_when_name_missing(tmp_path: Path) -> None:
    from suzerain.adapters.claude_skill.sk import SK004NameMatchesDir

    repo = _make_skill(tmp_path, "---\ndescription: x\n---\n")
    result = SK004NameMatchesDir().check(_skill_repo(repo))
    assert result.skipped is True


def test_sk005_passes_when_evals_dir_has_files(tmp_path: Path) -> None:
    from suzerain.adapters.claude_skill.sk import SK005EvalsNonEmpty

    repo = _make_skill(tmp_path, "---\nname: my-skill\ndescription: x\n---\n")
    evals = repo / "my-skill" / "evals"
    evals.mkdir()
    (evals / "case-1.md").write_text("- input: foo\n- expected: bar\n")
    result = SK005EvalsNonEmpty().check(_skill_repo(repo))
    assert result.passing is True
    assert "1 file" in result.evidence


def test_sk005_fails_when_evals_dir_missing(tmp_path: Path) -> None:
    from suzerain.adapters.claude_skill.sk import SK005EvalsNonEmpty

    repo = _make_skill(tmp_path, "---\nname: my-skill\ndescription: x\n---\n")
    result = SK005EvalsNonEmpty().check(_skill_repo(repo))
    assert result.passing is False
    assert "missing" in result.evidence


def test_sk005_fails_when_evals_dir_empty(tmp_path: Path) -> None:
    from suzerain.adapters.claude_skill.sk import SK005EvalsNonEmpty

    repo = _make_skill(tmp_path, "---\nname: my-skill\ndescription: x\n---\n")
    (repo / "my-skill" / "evals").mkdir()
    result = SK005EvalsNonEmpty().check(_skill_repo(repo))
    assert result.passing is False
    assert "empty" in result.evidence


def test_sk005_ignores_non_eval_extensions(tmp_path: Path) -> None:
    from suzerain.adapters.claude_skill.sk import SK005EvalsNonEmpty

    repo = _make_skill(tmp_path, "---\nname: my-skill\ndescription: x\n---\n")
    evals = repo / "my-skill" / "evals"
    evals.mkdir()
    (evals / "ignored.png").write_bytes(b"\x89PNG\r\n")
    result = SK005EvalsNonEmpty().check(_skill_repo(repo))
    assert result.passing is False
    assert "empty" in result.evidence


def test_sk005_skipped_when_no_skill_md(tmp_path: Path) -> None:
    from suzerain.adapters.claude_skill.sk import SK005EvalsNonEmpty

    result = SK005EvalsNonEmpty().check(_skill_repo(tmp_path))
    assert result.skipped is True


def test_sk006_passes_when_no_dir_mentioned(tmp_path: Path) -> None:
    from suzerain.adapters.claude_skill.sk import SK006ReferencedDirsExist

    repo = _make_skill(
        tmp_path,
        "---\nname: my-skill\ndescription: x\n---\nNo references at all.\n",
    )
    result = SK006ReferencedDirsExist().check(_skill_repo(repo))
    assert result.passing is True
    assert "no references/ or scripts/ mentioned" in result.evidence


def test_sk006_passes_when_referenced_dirs_exist(tmp_path: Path) -> None:
    from suzerain.adapters.claude_skill.sk import SK006ReferencedDirsExist

    repo = _make_skill(
        tmp_path,
        "---\nname: my-skill\ndescription: x\n---\nSee references/api.md and scripts/run.sh\n",
    )
    (repo / "my-skill" / "references").mkdir()
    (repo / "my-skill" / "scripts").mkdir()
    result = SK006ReferencedDirsExist().check(_skill_repo(repo))
    assert result.passing is True
    assert "all referenced dirs present" in result.evidence


def test_sk006_fails_when_referenced_dir_missing(tmp_path: Path) -> None:
    from suzerain.adapters.claude_skill.sk import SK006ReferencedDirsExist

    repo = _make_skill(
        tmp_path,
        "---\nname: my-skill\ndescription: x\n---\nSee scripts/run.sh\n",
    )
    result = SK006ReferencedDirsExist().check(_skill_repo(repo))
    assert result.passing is False
    assert "scripts" in result.evidence


def test_sk006_does_not_flag_references_inside_code_block(tmp_path: Path) -> None:
    from suzerain.adapters.claude_skill.sk import SK006ReferencedDirsExist

    body = (
        "---\nname: my-skill\ndescription: x\n---\n"
        "Example only:\n"
        "```\n"
        "scripts/example.sh\n"
        "references/example.md\n"
        "```\n"
        "End.\n"
    )
    repo = _make_skill(tmp_path, body)
    # No actual scripts/ or references/ dirs created — should still pass because
    # mentions are inside a fenced code block.
    result = SK006ReferencedDirsExist().check(_skill_repo(repo))
    assert result.passing is True


def test_sk006_skipped_when_no_skill_md(tmp_path: Path) -> None:
    from suzerain.adapters.claude_skill.sk import SK006ReferencedDirsExist

    result = SK006ReferencedDirsExist().check(_skill_repo(tmp_path))
    assert result.skipped is True


def test_sk006_does_not_flag_external_path_substring(tmp_path: Path) -> None:
    """Cross-repo paths like 'upstream/scripts/foo.sh' must NOT be treated as
    references to the skill's own top-level dir.
    """
    from suzerain.adapters.claude_skill.sk import SK006ReferencedDirsExist

    repo = _make_skill(
        tmp_path,
        "---\nname: my-skill\ndescription: x\n---\n"
        "Compare with upstream-repo/scripts/build.sh and github.com/owner/references/api.md\n",
    )
    # No actual scripts/ or references/ dirs created — the rule must NOT flag,
    # because the mentions are inside other path prefixes.
    result = SK006ReferencedDirsExist().check(_skill_repo(repo))
    assert result.passing is True


def test_sk007_passes_when_readme_mentions_claude_skills_path(tmp_path: Path) -> None:
    from suzerain.adapters.claude_skill.sk import SK007ReadmeInstallPath

    repo = _make_skill(tmp_path, "---\nname: my-skill\ndescription: x\n---\n")
    (repo / "README.md").write_text("Install: ~/.claude/skills/my-skill\n")
    result = SK007ReadmeInstallPath().check(_skill_repo(repo))
    assert result.passing is True
    assert "documented" in result.evidence


def test_sk007_passes_when_readme_mentions_plugins_path(tmp_path: Path) -> None:
    from suzerain.adapters.claude_skill.sk import SK007ReadmeInstallPath

    repo = _make_skill(tmp_path, "---\nname: my-skill\ndescription: x\n---\n")
    (repo / "README.md").write_text("Bundled in claude/plugins/foo\n")
    result = SK007ReadmeInstallPath().check(_skill_repo(repo))
    assert result.passing is True


def test_sk007_fails_when_readme_lacks_install_path(tmp_path: Path) -> None:
    from suzerain.adapters.claude_skill.sk import SK007ReadmeInstallPath

    repo = _make_skill(tmp_path, "---\nname: my-skill\ndescription: x\n---\n")
    (repo / "README.md").write_text("Just a project, no install instructions.\n")
    result = SK007ReadmeInstallPath().check(_skill_repo(repo))
    assert result.passing is False
    assert "does not mention" in result.evidence


def test_sk007_skipped_when_no_readme_at_root(tmp_path: Path) -> None:
    from suzerain.adapters.claude_skill.sk import SK007ReadmeInstallPath

    repo = _make_skill(tmp_path, "---\nname: my-skill\ndescription: x\n---\n")
    result = SK007ReadmeInstallPath().check(_skill_repo(repo))
    assert result.skipped is True
    assert "DG003" in result.evidence


def test_sk007_fix_appends_install_block(tmp_path: Path) -> None:
    from suzerain.adapters.claude_skill.sk import SK007ReadmeInstallPath

    repo = _make_skill(tmp_path, "---\nname: my-skill\ndescription: x\n---\n")
    readme = repo / "README.md"
    readme.write_text("# my-skill\nA short description.\n")
    rule = SK007ReadmeInstallPath()
    result = rule.check(_skill_repo(repo))
    patch = rule.fix(_skill_repo(repo), result)
    assert patch is not None
    assert patch.safe is True
    assert "~/.claude/skills/my-skill" in patch.content
    assert "<repo-url>" in patch.content


def test_sk007_fix_idempotent_when_install_path_already_present(tmp_path: Path) -> None:
    from suzerain.adapters.claude_skill.sk import SK007ReadmeInstallPath

    repo = _make_skill(tmp_path, "---\nname: my-skill\ndescription: x\n---\n")
    (repo / "README.md").write_text("Install at ~/.claude/skills/my-skill\n")
    rule = SK007ReadmeInstallPath()
    result = rule.check(_skill_repo(repo))
    # Already passing; fix() should return None.
    patch = rule.fix(_skill_repo(repo), result)
    assert patch is None


def test_sk007_fix_returns_none_when_skipped(tmp_path: Path) -> None:
    from suzerain.adapters.claude_skill.sk import SK007ReadmeInstallPath

    repo = _make_skill(tmp_path, "---\nname: my-skill\ndescription: x\n---\n")
    rule = SK007ReadmeInstallPath()
    result = rule.check(_skill_repo(repo))
    assert result.skipped is True
    patch = rule.fix(_skill_repo(repo), result)
    assert patch is None
