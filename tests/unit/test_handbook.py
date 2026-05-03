"""Tests for the handbook loader."""

from pathlib import Path

import pytest

from suzerain.core.handbook import Handbook


@pytest.fixture()
def mini_handbook(fixtures_dir: Path) -> Handbook:
    return Handbook(root=fixtures_dir / "handbook_mini")


def test_list_rules_returns_all_ids(mini_handbook: Handbook) -> None:
    ids = mini_handbook.list_rules()
    assert sorted(ids) == ["XX001", "XX002", "XX003"]


def test_get_rule_returns_section(mini_handbook: Handbook) -> None:
    rule = mini_handbook.get_rule("XX001")
    assert rule is not None
    assert rule.rule_id == "XX001"
    assert rule.title == "First test rule"
    assert rule.severity == "required"
    assert rule.stacks == ("python",)
    assert rule.adr_ref == "9999-test-decision"
    assert "marker.txt" in rule.body


def test_get_rule_without_adr(mini_handbook: Handbook) -> None:
    rule = mini_handbook.get_rule("XX002")
    assert rule is not None
    assert rule.severity == "recommended"
    assert rule.stacks == ("*",)
    assert rule.adr_ref is None


def test_get_rule_multistack(mini_handbook: Handbook) -> None:
    rule = mini_handbook.get_rule("XX003")
    assert rule is not None
    assert rule.severity == "optional"
    assert rule.stacks == ("node", "python")
    assert rule.adr_ref == "9999-test-decision"


def test_get_rule_unknown_returns_none(mini_handbook: Handbook) -> None:
    assert mini_handbook.get_rule("ZZ999") is None


def test_get_adr_returns_content(mini_handbook: Handbook) -> None:
    adr = mini_handbook.get_adr("9999-test-decision")
    assert adr is not None
    assert "ADR-9999" in adr
    assert "Test decision" in adr


def test_get_adr_unknown_returns_none(mini_handbook: Handbook) -> None:
    assert mini_handbook.get_adr("0000-does-not-exist") is None


def test_handbook_root_must_exist(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        Handbook(root=tmp_path / "no_handbook")


def test_handbook_regex_accepts_node_prefix(tmp_path: Path) -> None:
    """_RULE_HEADING_RE must match NODE_PK001-style IDs (new) and XX001-style (legacy)."""
    from suzerain.core.handbook import _RULE_HEADING_RE

    # Legacy 2-letter prefix (backward compat)
    assert _RULE_HEADING_RE.match("### XX001 — Some rule")
    assert _RULE_HEADING_RE.match("### PYTHON_LO001 — Layout rule")
    assert _RULE_HEADING_RE.match("### CLAUDE_SKILL_SK007 — Skill rule")
    # New NODE_ prefix
    assert _RULE_HEADING_RE.match("### NODE_PK001 — package.json present")
    assert _RULE_HEADING_RE.match("### NODE_QU002 — TypeScript present")
    assert _RULE_HEADING_RE.match("### NODE_TS001 — test framework")
    # Should NOT match missing title
    assert not _RULE_HEADING_RE.match("### NODE_PK001 —")
    # Should NOT match lowercase
    assert not _RULE_HEADING_RE.match("### node_pk001 — title")


def test_handbook_indexes_node_rules() -> None:
    """The real handbook must contain all 6 Node rules after 10-node.md is added."""
    from suzerain.core.handbook import Handbook
    from suzerain.core.paths import docs_root

    handbook = Handbook(root=docs_root())
    rule_ids = handbook.list_rules()
    node_ids = ("NODE_PK001", "NODE_PK002", "NODE_PK003", "NODE_QU001", "NODE_QU002", "NODE_TS001")
    for node_id in node_ids:
        assert node_id in rule_ids, f"{node_id} missing from handbook"
        section = handbook.get_rule(node_id)
        assert section is not None
        assert section.severity in ("required", "recommended")
        assert "node" in section.stacks


def test_handbook_indexes_all_sk_rules() -> None:
    from suzerain.core.handbook import Handbook
    from suzerain.core.paths import docs_root

    handbook = Handbook(root=docs_root())
    rule_ids = handbook.list_rules()
    for sk_id in (
        "CLAUDE_SKILL_SK001",
        "CLAUDE_SKILL_SK002",
        "CLAUDE_SKILL_SK003",
        "CLAUDE_SKILL_SK004",
        "CLAUDE_SKILL_SK005",
        "CLAUDE_SKILL_SK006",
        "CLAUDE_SKILL_SK007",
    ):
        assert sk_id in rule_ids, f"{sk_id} missing from handbook"
        section = handbook.get_rule(sk_id)
        assert section is not None
        assert section.severity in ("required", "recommended")
        assert "claude-skill" in section.stacks
