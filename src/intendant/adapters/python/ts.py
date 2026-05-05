"""Python adapter TS (testing) rules."""

from __future__ import annotations

from intendant.adapters.python.inspectors import has_pyproject, pyproject_tool_section
from intendant.core.repo import Repo
from intendant.core.rule import CheckResult, Rule


class TS001Pytest(Rule):
    """Pytest is configured via pyproject.toml, pytest.ini, or tests/conftest.py."""

    id = "PYTHON_TS001"
    title = "pytest configured ([tool.pytest.ini_options], pytest.ini, or tests/conftest.py)"
    severity = "required"
    stacks = ("python",)
    handbook_ref = "docs/handbook/05-testing.md#python_ts001"

    def check(self, repo: Repo) -> CheckResult:
        # 1. [tool.pytest.ini_options] in pyproject.toml
        pytest_section = pyproject_tool_section(repo.path, "pytest")
        if isinstance(pytest_section, dict) and "ini_options" in pytest_section:
            return CheckResult(
                passing=True,
                evidence="[tool.pytest.ini_options] in pyproject.toml",
            )

        # 2. pytest.ini at root with [pytest] section
        pytest_ini = repo.path / "pytest.ini"
        if pytest_ini.is_file():
            content = pytest_ini.read_text()
            if "[pytest]" in content:
                return CheckResult(passing=True, evidence="pytest.ini with [pytest] section")

        # 3. tests/conftest.py present
        conftest = repo.path / "tests" / "conftest.py"
        if conftest.is_file():
            return CheckResult(passing=True, evidence="tests/conftest.py present")

        return CheckResult(
            passing=False,
            evidence=(
                "no pytest configuration found"
                " (need [tool.pytest.ini_options] in pyproject.toml,"
                " pytest.ini with [pytest], or tests/conftest.py)"
            ),
        )


class TS003CoverageConfigured(Rule):
    """[tool.coverage] section (or sub-section) exists in pyproject.toml."""

    id = "PYTHON_TS003"
    title = "[tool.coverage] configured in pyproject.toml"
    severity = "recommended"
    stacks = ("python",)
    handbook_ref = "docs/handbook/05-tests.md#python_ts003"

    def check(self, repo: Repo) -> CheckResult:
        if not has_pyproject(repo.path):
            return CheckResult(passing=True, evidence="no pyproject.toml — skip")
        coverage_section = pyproject_tool_section(repo.path, "coverage")
        if coverage_section:
            return CheckResult(passing=True)
        return CheckResult(
            passing=False,
            evidence="no [tool.coverage] section found in pyproject.toml",
        )
