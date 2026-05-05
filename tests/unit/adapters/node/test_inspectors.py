"""Tests for Node inspector helpers."""

from pathlib import Path

from intendant.adapters.node.inspectors import (
    collect_dep_names,
    has_package_json,
    load_package_json,
)


def test_has_package_json_true(tmp_path: Path) -> None:
    (tmp_path / "package.json").write_text('{"name": "x"}')
    assert has_package_json(tmp_path) is True


def test_has_package_json_false(tmp_path: Path) -> None:
    assert has_package_json(tmp_path) is False


def test_load_package_json_returns_dict(tmp_path: Path) -> None:
    (tmp_path / "package.json").write_text('{"name": "x", "version": "1.0.0"}')
    data = load_package_json(tmp_path)
    assert data is not None
    assert data["name"] == "x"
    assert data["version"] == "1.0.0"


def test_load_package_json_returns_none_if_missing(tmp_path: Path) -> None:
    assert load_package_json(tmp_path) is None


def test_load_package_json_returns_none_on_parse_error(tmp_path: Path) -> None:
    (tmp_path / "package.json").write_text("{not valid json")
    assert load_package_json(tmp_path) is None


def test_collect_dep_names_all_sections(tmp_path: Path) -> None:
    pkg: dict = {
        "dependencies": {"express": "^4.0.0"},
        "devDependencies": {"eslint": "^9.0.0"},
        "peerDependencies": {"react": "^18.0.0"},
        "optionalDependencies": {"fsevents": "^2.0.0"},
    }
    names = collect_dep_names(pkg)
    assert names == {"express", "eslint", "react", "fsevents"}


def test_collect_dep_names_lowercases(tmp_path: Path) -> None:
    pkg: dict = {"dependencies": {"Express": "^4.0.0", "TypeScript": "^5.0.0"}}
    names = collect_dep_names(pkg)
    assert "express" in names
    assert "typescript" in names
    assert "Express" not in names


def test_collect_dep_names_empty_pkg(tmp_path: Path) -> None:
    assert collect_dep_names({}) == set()


def test_collect_dep_names_non_dict_section_skipped(tmp_path: Path) -> None:
    pkg: dict = {"dependencies": ["express"]}  # wrong type — should be skipped
    assert collect_dep_names(pkg) == set()
