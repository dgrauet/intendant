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


def test_find_test_annotations_finds_in_workspace_members(tmp_path: Path) -> None:
    """A Cargo workspace with glob members must be scanned crate by crate."""
    (tmp_path / "Cargo.toml").write_text('[workspace]\nmembers = ["crates/*"]\nresolver = "2"\n')
    foo_src = tmp_path / "crates" / "foo" / "src"
    foo_src.mkdir(parents=True)
    (foo_src / "lib.rs").write_text("#[test]\nfn foo_test() {}\n")
    bar_tests = tmp_path / "crates" / "bar" / "tests"
    bar_tests.mkdir(parents=True)
    (bar_tests / "it.rs").write_text("#[test]\nfn bar_test() {}\n")
    hits = find_test_annotations(tmp_path)
    names = {p.name for p in hits}
    assert names == {"lib.rs", "it.rs"}


def test_find_test_annotations_finds_explicit_member(tmp_path: Path) -> None:
    """Explicitly-listed (non-glob) workspace members are scanned too."""
    (tmp_path / "Cargo.toml").write_text('[workspace]\nmembers = ["app", "lib"]\n')
    app_tests = tmp_path / "app" / "tests"
    app_tests.mkdir(parents=True)
    (app_tests / "e2e.rs").write_text("#[test]\nfn e2e() {}\n")
    hits = find_test_annotations(tmp_path)
    assert {p.name for p in hits} == {"e2e.rs"}


def test_find_test_annotations_no_duplicate_across_root_and_member(tmp_path: Path) -> None:
    """A file reachable from both the root scan and a member scan is listed once."""
    (tmp_path / "Cargo.toml").write_text('[workspace]\nmembers = ["."]\n')
    src = tmp_path / "src"
    src.mkdir()
    (src / "lib.rs").write_text("#[test]\nfn t() {}\n")
    hits = find_test_annotations(tmp_path)
    assert len(hits) == 1
