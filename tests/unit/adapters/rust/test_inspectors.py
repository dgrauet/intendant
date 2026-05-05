"""Tests for Rust adapter inspectors."""

from __future__ import annotations

from pathlib import Path

from intendant.adapters.rust.inspectors import (
    find_test_annotations,
    has_cargo_toml,
    load_cargo_toml,
)


def test_has_cargo_toml(tmp_path: Path) -> None:
    assert has_cargo_toml(tmp_path) is False
    (tmp_path / "Cargo.toml").write_text("")
    assert has_cargo_toml(tmp_path) is True


def test_load_cargo_toml_returns_none_when_missing(tmp_path: Path) -> None:
    assert load_cargo_toml(tmp_path) is None


def test_load_cargo_toml_parses_valid(tmp_path: Path) -> None:
    (tmp_path / "Cargo.toml").write_text('[package]\nname = "x"\n')
    cargo = load_cargo_toml(tmp_path)
    assert cargo is not None
    assert cargo["package"]["name"] == "x"


def test_load_cargo_toml_returns_none_when_unparseable(tmp_path: Path) -> None:
    (tmp_path / "Cargo.toml").write_text("nope { [")
    assert load_cargo_toml(tmp_path) is None


def test_find_test_annotations_finds_in_src(tmp_path: Path) -> None:
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "lib.rs").write_text("#[test]\nfn t() {}\n")
    hits = find_test_annotations(tmp_path)
    assert len(hits) == 1
    assert hits[0].name == "lib.rs"


def test_find_test_annotations_finds_in_tests(tmp_path: Path) -> None:
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "i.rs").write_text("#[test]\nfn t() {}\n")
    assert len(find_test_annotations(tmp_path)) == 1


def test_find_test_annotations_empty_when_no_dirs(tmp_path: Path) -> None:
    assert find_test_annotations(tmp_path) == []
