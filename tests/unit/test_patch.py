"""Tests for Patch dataclass and apply primitives."""

from pathlib import Path

import pytest

from suzerain.core.patch import Patch, apply_patch


def test_patch_create_file_safe(tmp_path: Path) -> None:
    target = tmp_path / "new_file.txt"
    p = Patch(
        target_path=target,
        kind="create",
        content="hello\n",
        diff="--- /dev/null\n+++ new_file.txt\n@@ -0,0 +1 @@\n+hello\n",
        safe=True,
    )
    assert p.kind == "create"
    assert p.safe is True


def test_apply_create_writes_file(tmp_path: Path) -> None:
    target = tmp_path / "new_file.txt"
    p = Patch(
        target_path=target,
        kind="create",
        content="hello\n",
        diff="...",
        safe=True,
    )
    apply_patch(p)
    assert target.read_text() == "hello\n"


def test_apply_overwrite_replaces_file(tmp_path: Path) -> None:
    target = tmp_path / "existing.txt"
    target.write_text("old content\n")
    p = Patch(
        target_path=target,
        kind="overwrite",
        content="new content\n",
        diff="...",
        safe=True,
    )
    apply_patch(p)
    assert target.read_text() == "new content\n"


def test_apply_creates_parent_dirs(tmp_path: Path) -> None:
    target = tmp_path / "nested" / "sub" / "file.txt"
    p = Patch(
        target_path=target,
        kind="create",
        content="x\n",
        diff="...",
        safe=True,
    )
    apply_patch(p)
    assert target.read_text() == "x\n"
    assert target.parent.is_dir()


def test_apply_unsafe_patch_raises(tmp_path: Path) -> None:
    target = tmp_path / "any.txt"
    p = Patch(
        target_path=target,
        kind="overwrite",
        content="dangerous\n",
        diff="...",
        safe=False,
    )
    with pytest.raises(ValueError, match="not safe"):
        apply_patch(p)


def test_apply_merge_toml_preserves_custom_sections(tmp_path: Path) -> None:
    target = tmp_path / "pyproject.toml"
    target.write_text('[project]\nname = "x"\nversion = "0.0.0"\n\n[tool.custom]\nfoo = 1\n')
    p = Patch(
        target_path=target,
        kind="merge_toml",
        content="[tool.ruff]\nline-length = 100\n",
        diff="...",
        safe=True,
    )
    apply_patch(p)
    text = target.read_text()
    import tomllib

    data = tomllib.loads(text)
    assert data["project"]["name"] == "x"
    assert data["tool"]["custom"]["foo"] == 1  # preserved
    assert data["tool"]["ruff"]["line-length"] == 100  # added
