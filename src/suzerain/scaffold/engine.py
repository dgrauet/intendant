"""Scaffold engine — copies templates with substitution to produce a new repo."""

from __future__ import annotations

import shutil
import tomllib
from pathlib import Path

import tomli_w

from suzerain.core.paths import templates_root
from suzerain.scaffold.substitutions import SubstitutionContext, resolve_placeholders

_KNOWN_STACKS = {"python"}


def scaffold_project(target: Path, stack: str, context: SubstitutionContext) -> None:
    """Generate a new conformant suzerain project at `target`.

    Copies templates from ``templates/_common/``, ``templates/<stack>/``,
    and ``templates/github/``, applies placeholder substitutions, renames
    ``.template``/``.skeleton.md`` suffixes, and adds programmatic files
    (src/, tests/, .python-version) to satisfy the baseline rules.

    Raises:
        FileExistsError: if `target` already exists.
        ValueError: if `stack` is not supported.
    """
    if stack not in _KNOWN_STACKS:
        raise ValueError(f"unknown stack: {stack!r} (supported: {sorted(_KNOWN_STACKS)})")
    if target.exists():
        raise FileExistsError(f"target already exists: {target}")

    target.mkdir(parents=True)
    troot = templates_root()

    _copy_common(troot / "_common", target, context)
    _copy_github(troot / "github", target, context)
    _copy_stack(troot / stack, target, context)
    _create_programmatic_files(target, stack, context)
    _strict_mode_in_suzerain_toml(target, context)


def _copy_common(src: Path, dst: Path, context: SubstitutionContext) -> None:
    for entry in sorted(src.iterdir()):
        if not entry.is_file():
            continue
        if entry.name == "0000-record-architecture-decisions.md.template":
            target = dst / "docs" / "adr" / "0000-record-architecture-decisions.md"
        elif entry.name == "adr.md":
            target = dst / "docs" / "adr-template.md"
        else:
            target = dst / _strip_template_suffix(entry.name)
        _copy_file_with_substitution(entry, target, context)


def _copy_github(src: Path, dst: Path, context: SubstitutionContext) -> None:
    workflows = dst / ".github" / "workflows"
    for entry in sorted(src.iterdir()):
        if not entry.is_file():
            continue
        if entry.suffix == ".yml":
            target = workflows / entry.name
        elif entry.name.endswith(".json.template"):
            target = dst / entry.name.removesuffix(".template")
        else:
            target = dst / _strip_template_suffix(entry.name)
        _copy_file_with_substitution(entry, target, context)


def _copy_stack(src: Path, dst: Path, context: SubstitutionContext) -> None:
    if not src.is_dir():
        return
    for entry in sorted(src.iterdir()):
        if not entry.is_file():
            continue
        target = dst / _strip_template_suffix(entry.name)
        _copy_file_with_substitution(entry, target, context)


def _strip_template_suffix(name: str) -> str:
    if name.endswith(".skeleton.md"):
        return name.removesuffix(".skeleton.md") + ".md"
    if name.endswith(".template"):
        return name.removesuffix(".template")
    return name


def _copy_file_with_substitution(src: Path, dst: Path, context: SubstitutionContext) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    try:
        text = src.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        shutil.copy2(src, dst)
        return
    out = resolve_placeholders(text, context)
    dst.write_text(out, encoding="utf-8")


def _create_programmatic_files(target: Path, stack: str, context: SubstitutionContext) -> None:
    if stack != "python":
        return
    pkg_dir = target / "src" / context.package_name
    pkg_dir.mkdir(parents=True, exist_ok=True)
    (pkg_dir / "__init__.py").write_text("", encoding="utf-8")
    tests_dir = target / "tests"
    tests_dir.mkdir(parents=True, exist_ok=True)
    (tests_dir / "__init__.py").write_text("", encoding="utf-8")
    (tests_dir / "conftest.py").write_text("", encoding="utf-8")
    (target / ".python-version").write_text("3.13\n", encoding="utf-8")


def _strict_mode_in_suzerain_toml(target: Path, context: SubstitutionContext) -> None:
    cfg = target / ".suzerain.toml"
    if not cfg.is_file():
        return
    data = tomllib.loads(cfg.read_text(encoding="utf-8"))
    data.setdefault("suzerain", {})
    data["suzerain"]["mode"] = "strict"
    data["suzerain"]["stack"] = context.stack
    cfg.write_text(tomli_w.dumps(data), encoding="utf-8")
