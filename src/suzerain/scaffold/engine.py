"""Scaffold engine — copies templates with substitution to produce a new repo."""

from __future__ import annotations

import shutil
import tomllib
from pathlib import Path

import tomli_w

from suzerain.core.paths import templates_root
from suzerain.scaffold.substitutions import SubstitutionContext, resolve_placeholders

_KNOWN_STACKS = {"python", "claude-skill", "node", "rust"}


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
    _copy_stack_recursive(src, src, dst, context)


def _copy_stack_recursive(
    stack_root: Path, src_dir: Path, dst_dir: Path, context: SubstitutionContext
) -> None:
    """Recursively copy a stack template directory, applying substitutions.

    For the ``claude-skill`` stack, files inside the skill-content subdirs
    (``SKILL.md``, ``evals/``) are remapped into ``<project_name>/`` so
    the final layout satisfies SK001 and SK005.
    """
    for entry in sorted(src_dir.iterdir()):
        rel = entry.relative_to(stack_root)
        if entry.is_dir():
            _copy_stack_recursive(stack_root, entry, dst_dir, context)
        elif entry.is_file():
            target = _remap_stack_path(rel, dst_dir, context)
            _copy_file_with_substitution(entry, target, context)


# Files (or directories) under these names are remapped into the skill
# subdirectory (<project_name>/) for the claude-skill stack.
_CLAUDE_SKILL_NESTED = {"SKILL.md.template", "evals"}


def _remap_stack_path(rel: Path, dst: Path, context: SubstitutionContext) -> Path:
    """Compute the destination path for a stack template file.

    For ``claude-skill``, ``SKILL.md`` and anything inside ``evals/`` land
    inside ``<project_name>/`` instead of at the repo root.
    """
    parts = rel.parts
    # If the top-level component is one of the nested dirs/files, remap into
    # the skill subdirectory.
    if parts[0] in _CLAUDE_SKILL_NESTED:
        skill_dir = dst / context.project_name
        return skill_dir / Path(*[_strip_template_suffix(p) for p in parts])
    # .github/workflows/ are handled by _copy_github normally; but if the
    # stack ships its own ci.yml we route it correctly.
    if parts[0] == ".github" and len(parts) >= 3 and parts[1] == "workflows":
        workflows = dst / ".github" / "workflows"
        return workflows / _strip_template_suffix(parts[-1])
    # Default: flat placement at repo root (strip template suffix from last part).
    return dst / Path(*[*parts[:-1], _strip_template_suffix(parts[-1])])


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
    if stack == "python":
        pkg_dir = target / "src" / context.package_name
        pkg_dir.mkdir(parents=True, exist_ok=True)
        (pkg_dir / "__init__.py").write_text("", encoding="utf-8")
        tests_dir = target / "tests"
        tests_dir.mkdir(parents=True, exist_ok=True)
        (tests_dir / "__init__.py").write_text("", encoding="utf-8")
        (tests_dir / "conftest.py").write_text("", encoding="utf-8")
        (tests_dir / "test_placeholder.py").write_text(
            '"""Placeholder test — replace with real tests."""\n'
            "\n"
            "\n"
            "def test_placeholder() -> None:\n"
            '    """This passes by default. Delete when real tests are added."""\n',
            encoding="utf-8",
        )
        (target / ".python-version").write_text("3.13\n", encoding="utf-8")
    elif stack == "claude-skill":
        # Skill subdirectory — same name as repo
        skill_dir = target / context.project_name
        skill_dir.mkdir(parents=True, exist_ok=True)
        (skill_dir / "evals").mkdir(parents=True, exist_ok=True)
        (skill_dir / "references").mkdir(parents=True, exist_ok=True)
        (skill_dir / "scripts").mkdir(parents=True, exist_ok=True)
        # .gitkeep so empty dirs persist in git
        (skill_dir / "references" / ".gitkeep").write_text("", encoding="utf-8")
        (skill_dir / "scripts" / ".gitkeep").write_text("", encoding="utf-8")
    elif stack == "node":
        # src/index.ts and tests/index.test.ts as starter files
        src_dir = target / "src"
        src_dir.mkdir(parents=True, exist_ok=True)
        (src_dir / "index.ts").write_text(
            "export const greet = (name: string): string => `Hello, ${name}!`;\n"
        )
        tests_dir = target / "tests"
        tests_dir.mkdir(parents=True, exist_ok=True)
        (tests_dir / "index.test.ts").write_text(
            'import { describe, it, expect } from "vitest";\n'
            'import { greet } from "../src/index.js";\n\n'
            'describe("greet", () => {\n'
            '  it("returns a greeting", () => {\n'
            '    expect(greet("world")).toBe("Hello, world!");\n'
            "  });\n"
            "});\n"
        )
    elif stack == "rust":
        # src/lib.rs with one #[test] satisfies RUST_TS001 out of the box.
        src_dir = target / "src"
        src_dir.mkdir(parents=True, exist_ok=True)
        (src_dir / "lib.rs").write_text(
            "pub fn add(a: i32, b: i32) -> i32 {\n"
            "    a + b\n"
            "}\n"
            "\n"
            "#[cfg(test)]\n"
            "mod tests {\n"
            "    use super::*;\n"
            "\n"
            "    #[test]\n"
            "    fn it_adds() {\n"
            "        assert_eq!(add(2, 3), 5);\n"
            "    }\n"
            "}\n"
        )


def _strict_mode_in_suzerain_toml(target: Path, context: SubstitutionContext) -> None:
    cfg = target / ".suzerain.toml"
    if not cfg.is_file():
        return
    data = tomllib.loads(cfg.read_text(encoding="utf-8"))
    data.setdefault("suzerain", {})
    data["suzerain"]["mode"] = "strict"
    data["suzerain"]["stack"] = context.stack
    data.setdefault("exemptions", {})
    if context.stack == "python":
        data["exemptions"]["PYTHON_PK002"] = (
            "fresh scaffold; run `uv lock` then remove this exemption"
        )
    cfg.write_text(tomli_w.dumps(data), encoding="utf-8")
