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
    assert rule.title == "Première règle de test"
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
    assert "Décision de test" in adr


def test_get_adr_unknown_returns_none(mini_handbook: Handbook) -> None:
    assert mini_handbook.get_adr("0000-does-not-exist") is None


def test_handbook_root_must_exist(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        Handbook(root=tmp_path / "no_handbook")


def test_handbook_indexes_all_sk_rules() -> None:
    from suzerain.core.handbook import Handbook
    from suzerain.core.paths import docs_root

    handbook = Handbook(root=docs_root())
    rule_ids = handbook.list_rules()
    for sk_id in ("SK001", "SK002", "SK003", "SK004", "SK005", "SK006", "SK007"):
        assert sk_id in rule_ids, f"{sk_id} missing from handbook"
        section = handbook.get_rule(sk_id)
        assert section is not None
        assert section.severity in ("required", "recommended")
        assert "skill" in section.stacks
