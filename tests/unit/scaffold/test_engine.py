"""Tests for the scaffold engine."""

import tomllib
from pathlib import Path

import pytest

from suzerain.scaffold.engine import scaffold_project
from suzerain.scaffold.substitutions import SubstitutionContext


@pytest.fixture()
def context() -> SubstitutionContext:
    return SubstitutionContext(
        project_name="my-test",
        package_name="my_test",
        description="A scaffolded test project",
        author="Test Author",
        year="2026",
        stack="python",
        release_type="python",
    )


def test_scaffold_creates_target_dir(tmp_path: Path, context: SubstitutionContext) -> None:
    target = tmp_path / "my-test"
    scaffold_project(target, "python", context)
    assert target.is_dir()


def test_scaffold_refuses_existing_target(tmp_path: Path, context: SubstitutionContext) -> None:
    target = tmp_path / "exists"
    target.mkdir()
    with pytest.raises(FileExistsError):
        scaffold_project(target, "python", context)


def test_scaffold_creates_python_layout(tmp_path: Path, context: SubstitutionContext) -> None:
    target = tmp_path / "my-test"
    scaffold_project(target, "python", context)
    assert (target / "src" / "my_test" / "__init__.py").is_file()
    assert (target / "tests" / "__init__.py").is_file()
    assert (target / "tests" / "conftest.py").is_file()


def test_scaffold_creates_pinned_python_version(
    tmp_path: Path, context: SubstitutionContext
) -> None:
    target = tmp_path / "my-test"
    scaffold_project(target, "python", context)
    py_ver = target / ".python-version"
    assert py_ver.is_file()
    assert py_ver.read_text().strip() == "3.13"


def test_scaffold_writes_substituted_pyproject(
    tmp_path: Path, context: SubstitutionContext
) -> None:
    target = tmp_path / "my-test"
    scaffold_project(target, "python", context)
    pyproject = target / "pyproject.toml"
    assert pyproject.is_file()
    data = tomllib.loads(pyproject.read_text())
    assert data["project"]["name"] == "my-test"
    assert data["project"]["description"] == "A scaffolded test project"


def test_scaffold_writes_substituted_license(tmp_path: Path, context: SubstitutionContext) -> None:
    target = tmp_path / "my-test"
    scaffold_project(target, "python", context)
    license_file = target / "LICENSE"
    assert license_file.is_file()
    text = license_file.read_text()
    assert "Test Author" in text
    assert "2026" in text


def test_scaffold_writes_baseline_adr(tmp_path: Path, context: SubstitutionContext) -> None:
    target = tmp_path / "my-test"
    scaffold_project(target, "python", context)
    adr = target / "docs" / "adr" / "0000-record-architecture-decisions.md"
    assert adr.is_file()
    text = adr.read_text()
    assert "ADR-0000" in text
    assert "my-test" in text  # placeholder substituted


def test_scaffold_writes_changelog_with_keep_format(
    tmp_path: Path, context: SubstitutionContext
) -> None:
    target = tmp_path / "my-test"
    scaffold_project(target, "python", context)
    changelog = target / "CHANGELOG.md"
    assert changelog.is_file()
    assert "Keep a Changelog" in changelog.read_text()


def test_scaffold_writes_strict_mode_suzerain_toml(
    tmp_path: Path, context: SubstitutionContext
) -> None:
    target = tmp_path / "my-test"
    scaffold_project(target, "python", context)
    cfg = target / ".suzerain.toml"
    assert cfg.is_file()
    data = tomllib.loads(cfg.read_text())
    assert data["suzerain"]["enforcement"] == "strict"
    assert data["suzerain"]["stack"] == "python"


def test_scaffold_writes_ci_workflow(tmp_path: Path, context: SubstitutionContext) -> None:
    target = tmp_path / "my-test"
    scaffold_project(target, "python", context)
    assert (target / ".github" / "workflows" / "ci.yml").is_file()
    assert (target / ".github" / "workflows" / "release-please.yml").is_file()


def test_scaffold_writes_pre_commit_config(tmp_path: Path, context: SubstitutionContext) -> None:
    target = tmp_path / "my-test"
    scaffold_project(target, "python", context)
    assert (target / ".pre-commit-config.yaml").is_file()


def test_scaffold_drops_template_suffix(tmp_path: Path, context: SubstitutionContext) -> None:
    """Files like .gitignore.template are renamed to .gitignore."""
    target = tmp_path / "my-test"
    scaffold_project(target, "python", context)
    assert (target / ".gitignore").is_file()
    assert not (target / ".gitignore.template").exists()


def test_scaffold_unknown_stack_raises(tmp_path: Path, context: SubstitutionContext) -> None:
    target = tmp_path / "my-test"
    with pytest.raises(ValueError, match="unknown stack"):
        scaffold_project(target, "haskell", context)


def test_scaffold_creates_placeholder_test(tmp_path: Path, context: SubstitutionContext) -> None:
    target = tmp_path / "my-test"
    scaffold_project(target, "python", context)
    placeholder = target / "tests" / "test_placeholder.py"
    assert placeholder.is_file()
    assert "test_placeholder" in placeholder.read_text()


# ---------------------------------------------------------------------------
# claude-skill stack tests
# ---------------------------------------------------------------------------


@pytest.fixture()
def skill_context() -> SubstitutionContext:
    return SubstitutionContext(
        project_name="my-skill",
        package_name="my_skill",
        description="Use this skill when [TODO: describe trigger condition for the skill]",
        author="Test Author",
        year="2026",
        stack="claude-skill",
        release_type="simple",
    )


def test_scaffold_claude_skill_creates_target_dir(
    tmp_path: Path, skill_context: SubstitutionContext
) -> None:
    target = tmp_path / "my-skill"
    scaffold_project(target, "claude-skill", skill_context)
    assert target.is_dir()


def test_scaffold_claude_skill_creates_skill_md_at_nested_path(
    tmp_path: Path, skill_context: SubstitutionContext
) -> None:
    """SKILL.md must live at <name>/<name>/SKILL.md, not at <name>/SKILL.md."""
    target = tmp_path / "my-skill"
    scaffold_project(target, "claude-skill", skill_context)
    assert (target / "my-skill" / "SKILL.md").is_file()
    assert not (target / "SKILL.md").exists()


def test_scaffold_claude_skill_creates_evals_dir_with_placeholder(
    tmp_path: Path, skill_context: SubstitutionContext
) -> None:
    """evals/ must contain at least one file (satisfies SK005)."""
    target = tmp_path / "my-skill"
    scaffold_project(target, "claude-skill", skill_context)
    evals_dir = target / "my-skill" / "evals"
    assert evals_dir.is_dir()
    files = [f for f in evals_dir.iterdir() if f.is_file()]
    assert len(files) >= 1


def test_scaffold_claude_skill_creates_references_and_scripts_dirs(
    tmp_path: Path, skill_context: SubstitutionContext
) -> None:
    target = tmp_path / "my-skill"
    scaffold_project(target, "claude-skill", skill_context)
    assert (target / "my-skill" / "references").is_dir()
    assert (target / "my-skill" / "scripts").is_dir()
    assert (target / "my-skill" / "references" / ".gitkeep").is_file()
    assert (target / "my-skill" / "scripts" / ".gitkeep").is_file()


def test_scaffold_claude_skill_readme_mentions_install_path(
    tmp_path: Path, skill_context: SubstitutionContext
) -> None:
    """README.md must mention ~/.claude/skills/ (satisfies SK007)."""
    target = tmp_path / "my-skill"
    scaffold_project(target, "claude-skill", skill_context)
    readme = target / "README.md"
    assert readme.is_file()
    assert "~/.claude/skills/" in readme.read_text()


def test_scaffold_claude_skill_suzerain_toml_has_strict_mode_and_exemptions(
    tmp_path: Path, skill_context: SubstitutionContext
) -> None:
    """`.suzerain.toml` must declare strict mode + claude-skill stack + CI exemptions."""
    import tomllib

    target = tmp_path / "my-skill"
    scaffold_project(target, "claude-skill", skill_context)
    cfg = target / ".suzerain.toml"
    assert cfg.is_file()
    data = tomllib.loads(cfg.read_text())
    assert data["suzerain"]["enforcement"] == "strict"
    assert data["suzerain"]["stack"] == "claude-skill"
    exemptions = data.get("exemptions", {})
    # CI002 exemption removed: claude-skill CI now runs suzerain audit (CI002 passes natively)
    assert "CI003" in exemptions
    assert "CI004" in exemptions


def test_scaffold_claude_skill_skill_md_has_valid_frontmatter(
    tmp_path: Path, skill_context: SubstitutionContext
) -> None:
    """SKILL.md frontmatter must have name + non-empty description."""
    target = tmp_path / "my-skill"
    scaffold_project(target, "claude-skill", skill_context)
    skill_md = target / "my-skill" / "SKILL.md"
    text = skill_md.read_text()
    assert "name: my-skill" in text
    assert "description:" in text
