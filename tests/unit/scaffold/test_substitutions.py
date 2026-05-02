"""Tests for placeholder substitution helpers."""

from datetime import date

from suzerain.scaffold.substitutions import (
    SubstitutionContext,
    derive_package_name,
    resolve_placeholders,
)


def test_derive_package_name_simple() -> None:
    assert derive_package_name("myproject") == "myproject"


def test_derive_package_name_hyphenated() -> None:
    assert derive_package_name("my-cool-project") == "my_cool_project"


def test_derive_package_name_dotted() -> None:
    assert derive_package_name("my.module") == "my_module"


def test_derive_package_name_uppercase() -> None:
    assert derive_package_name("MyProject") == "myproject"


def test_resolve_placeholders_basic() -> None:
    ctx = SubstitutionContext(
        project_name="my-project",
        package_name="my_project",
        description="A test",
        author="Test Author",
        year="2026",
        stack="python",
        release_type="python",
    )
    text = "name = {{ project_name }} pkg = {{ package_name }} year = {{ year }}"
    out = resolve_placeholders(text, ctx)
    assert out == "name = my-project pkg = my_project year = 2026"


def test_resolve_placeholders_missing_key_left_as_is() -> None:
    """Unknown keys are left alone (forward-compatible with future template tokens)."""
    ctx = SubstitutionContext(
        project_name="x",
        package_name="x",
        description="",
        author="",
        year="2026",
        stack="python",
        release_type="python",
    )
    text = "{{ unknown_token }} stays"
    out = resolve_placeholders(text, ctx)
    assert out == "{{ unknown_token }} stays"


def test_resolve_placeholders_handles_spaces_around_token() -> None:
    """Both `{{ key }}` and `{{key}}` (no spaces) supported."""
    ctx = SubstitutionContext(
        project_name="x",
        package_name="x",
        description="",
        author="",
        year="2026",
        stack="python",
        release_type="python",
    )
    assert resolve_placeholders("{{project_name}}", ctx) == "x"
    assert resolve_placeholders("{{ project_name }}", ctx) == "x"
    assert resolve_placeholders("{{  project_name  }}", ctx) == "x"


def test_substitution_context_from_minimal() -> None:
    ctx = SubstitutionContext.from_minimal(
        project_name="my-project",
        stack="python",
    )
    assert ctx.project_name == "my-project"
    assert ctx.package_name == "my_project"  # derived
    assert ctx.year == str(date.today().year)
    assert ctx.stack == "python"
    assert ctx.release_type == "python"
    assert ctx.description == ""
    # author may be empty or from git config; just verify it's a string
    assert isinstance(ctx.author, str)
