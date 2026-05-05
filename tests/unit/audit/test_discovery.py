"""Unit tests for repo discovery."""

from __future__ import annotations

from pathlib import Path

from suzerain.audit.discovery import find_suzerain_repos


def _touch_marker(parent: Path) -> None:
    parent.mkdir(parents=True, exist_ok=True)
    (parent / ".suzerain.toml").write_text(
        '[suzerain]\nversion = "1"\nstack = "auto"\nenforcement = "advisory"\n'
    )


def test_find_returns_empty_list_when_root_missing(tmp_path: Path) -> None:
    assert find_suzerain_repos(tmp_path / "nonexistent") == []


def test_find_returns_empty_list_when_no_marker(tmp_path: Path) -> None:
    (tmp_path / "some_dir").mkdir()
    assert find_suzerain_repos(tmp_path) == []


def test_find_returns_repo_at_depth_1(tmp_path: Path) -> None:
    _touch_marker(tmp_path / "repo_a")
    found = find_suzerain_repos(tmp_path)
    assert found == [tmp_path / "repo_a"]


def test_find_returns_repo_at_depth_2(tmp_path: Path) -> None:
    _touch_marker(tmp_path / "group" / "repo_b")
    found = find_suzerain_repos(tmp_path)
    assert found == [tmp_path / "group" / "repo_b"]


def test_find_excludes_repos_at_depth_3_with_default_maxdepth(tmp_path: Path) -> None:
    _touch_marker(tmp_path / "level1" / "level2" / "deep_repo")
    assert find_suzerain_repos(tmp_path) == []


def test_find_includes_depth_3_when_maxdepth_increased(tmp_path: Path) -> None:
    _touch_marker(tmp_path / "level1" / "level2" / "deep_repo")
    found = find_suzerain_repos(tmp_path, maxdepth=3)
    assert found == [tmp_path / "level1" / "level2" / "deep_repo"]


def test_find_returns_alphabetical_order(tmp_path: Path) -> None:
    _touch_marker(tmp_path / "zeta")
    _touch_marker(tmp_path / "alpha")
    _touch_marker(tmp_path / "mike")
    found = find_suzerain_repos(tmp_path)
    assert [p.name for p in found] == ["alpha", "mike", "zeta"]


def test_find_skips_dirs_without_marker_among_governed_ones(tmp_path: Path) -> None:
    _touch_marker(tmp_path / "governed")
    (tmp_path / "ungoverned").mkdir()
    found = find_suzerain_repos(tmp_path)
    assert found == [tmp_path / "governed"]


def test_find_returns_empty_when_root_is_not_a_directory(tmp_path: Path) -> None:
    file_path = tmp_path / "afile"
    file_path.write_text("not a dir")
    assert find_suzerain_repos(file_path) == []
