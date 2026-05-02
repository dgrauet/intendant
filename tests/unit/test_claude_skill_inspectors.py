"""Unit tests for skill adapter inspectors."""

from __future__ import annotations

from pathlib import Path

from suzerain.adapters.claude_skill.inspectors import find_skill_md, parse_frontmatter


def test_find_skill_md_at_depth_1(tmp_path: Path) -> None:
    skill_md = tmp_path / "SKILL.md"
    skill_md.write_text("---\nname: foo\n---\nbody\n")
    assert find_skill_md(tmp_path) == skill_md


def test_find_skill_md_at_depth_2(tmp_path: Path) -> None:
    sub = tmp_path / "my-skill"
    sub.mkdir()
    skill_md = sub / "SKILL.md"
    skill_md.write_text("---\nname: my-skill\n---\nbody\n")
    assert find_skill_md(tmp_path) == skill_md


def test_find_skill_md_returns_none_when_absent(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("hi")
    assert find_skill_md(tmp_path) is None


def test_find_skill_md_ignores_excluded_dirs(tmp_path: Path) -> None:
    for excluded in (".git", "node_modules", "__pycache__", ".venv", ".tox", "dist", "build"):
        d = tmp_path / excluded
        d.mkdir()
        (d / "SKILL.md").write_text("ignored")
    assert find_skill_md(tmp_path) is None


def test_find_skill_md_depth_1_takes_precedence_over_depth_2(tmp_path: Path) -> None:
    root_skill = tmp_path / "SKILL.md"
    root_skill.write_text("---\nname: root\n---\n")
    sub = tmp_path / "nested"
    sub.mkdir()
    (sub / "SKILL.md").write_text("---\nname: nested\n---\n")
    assert find_skill_md(tmp_path) == root_skill


def test_find_skill_md_alphabetical_when_multiple_at_same_depth(tmp_path: Path) -> None:
    for name in ("zeta", "alpha", "mike"):
        d = tmp_path / name
        d.mkdir()
        (d / "SKILL.md").write_text(f"---\nname: {name}\n---\n")
    found = find_skill_md(tmp_path)
    assert found is not None
    assert found.parent.name == "alpha"


def test_find_skill_md_does_not_recurse_to_depth_3(tmp_path: Path) -> None:
    deep = tmp_path / "a" / "b"
    deep.mkdir(parents=True)
    (deep / "SKILL.md").write_text("---\nname: deep\n---\n")
    assert find_skill_md(tmp_path) is None


def _write_skill(tmp_path: Path, body: str) -> Path:
    p = tmp_path / "SKILL.md"
    p.write_text(body)
    return p


def test_parse_frontmatter_valid(tmp_path: Path) -> None:
    p = _write_skill(
        tmp_path,
        "---\nname: foo\ndescription: a useful skill\n---\nbody\n",
    )
    data = parse_frontmatter(p)
    assert data == {"name": "foo", "description": "a useful skill"}


def test_parse_frontmatter_no_frontmatter_returns_none(tmp_path: Path) -> None:
    p = _write_skill(tmp_path, "# Just a heading\nno frontmatter here\n")
    assert parse_frontmatter(p) is None


def test_parse_frontmatter_broken_yaml_returns_none(tmp_path: Path) -> None:
    # Truly malformed YAML: unclosed flow sequence triggers yaml.YAMLError.
    p = _write_skill(tmp_path, "---\nkey: [unclosed\n---\nbody\n")
    assert parse_frontmatter(p) is None


def test_parse_frontmatter_handles_utf8_bom(tmp_path: Path) -> None:
    p = tmp_path / "SKILL.md"
    p.write_bytes(b"\xef\xbb\xbf---\nname: foo\ndescription: bom\n---\nbody\n")
    data = parse_frontmatter(p)
    assert data is not None
    assert data["name"] == "foo"


def test_parse_frontmatter_with_list_values(tmp_path: Path) -> None:
    p = _write_skill(
        tmp_path,
        "---\nname: foo\ndescription: x\ntools: [bash, edit]\n---\nbody\n",
    )
    data = parse_frontmatter(p)
    assert data is not None
    assert data["tools"] == ["bash", "edit"]


def test_parse_frontmatter_with_multiline_description(tmp_path: Path) -> None:
    p = _write_skill(
        tmp_path,
        "---\nname: foo\ndescription: |\n  multi\n  line\n---\nbody\n",
    )
    data = parse_frontmatter(p)
    assert data is not None
    assert data["description"] == "multi\nline\n"


def test_parse_frontmatter_returns_none_for_non_dict_root(tmp_path: Path) -> None:
    # YAML root is a list, not a mapping
    p = _write_skill(tmp_path, "---\n- foo\n- bar\n---\nbody\n")
    assert parse_frontmatter(p) is None
