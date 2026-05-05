"""Tests for Go adapter inspectors."""

from __future__ import annotations

from pathlib import Path

from intendant.adapters.go.inspectors import find_test_files, has_go_mod, load_go_mod


def test_has_go_mod(tmp_path: Path) -> None:
    assert has_go_mod(tmp_path) is False
    (tmp_path / "go.mod").write_text("module x\n")
    assert has_go_mod(tmp_path) is True


def test_load_go_mod_returns_none_when_missing(tmp_path: Path) -> None:
    assert load_go_mod(tmp_path) is None


def test_load_go_mod_parses_module_and_go_directive(tmp_path: Path) -> None:
    (tmp_path / "go.mod").write_text("module example.com/foo\n\ngo 1.22\n")
    mod = load_go_mod(tmp_path)
    assert mod is not None
    assert mod.module == "example.com/foo"
    assert mod.go_version == "1.22"


def test_load_go_mod_handles_missing_go_directive(tmp_path: Path) -> None:
    (tmp_path / "go.mod").write_text("module example.com/foo\n")
    mod = load_go_mod(tmp_path)
    assert mod is not None
    assert mod.module == "example.com/foo"
    assert mod.go_version is None


def test_find_test_files_finds_test_funcs(tmp_path: Path) -> None:
    (tmp_path / "main_test.go").write_text(
        'package main\nimport "testing"\nfunc TestX(t *testing.T) {}\n'
    )
    hits = find_test_files(tmp_path)
    assert len(hits) == 1
    assert hits[0].name == "main_test.go"


def test_find_test_files_skips_vendor(tmp_path: Path) -> None:
    vendor = tmp_path / "vendor" / "pkg"
    vendor.mkdir(parents=True)
    (vendor / "x_test.go").write_text(
        'package pkg\nimport "testing"\nfunc TestVendor(t *testing.T) {}\n'
    )
    assert find_test_files(tmp_path) == []


def test_find_test_files_ignores_files_without_test_func(tmp_path: Path) -> None:
    (tmp_path / "x_test.go").write_text("package x\n// no test funcs\n")
    assert find_test_files(tmp_path) == []
