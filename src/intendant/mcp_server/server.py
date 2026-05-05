"""FastMCP server exposing intendant governance tools over stdio.

Run via ``intendant mcp`` (see :mod:`intendant.commands.mcp`). Requires the
optional ``mcp`` extra: ``uv tool install 'intendant[mcp]'``.
"""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from intendant.mcp_server import handlers

mcp = FastMCP("intendant")


@mcp.tool()
def audit_repo(path: str, severity: str | None = None) -> dict[str, Any]:
    """Audit a single repo against its `.intendant.toml` configuration.

    Args:
        path: Absolute path to the repo root.
        severity: Optional filter — "required", "recommended", or "optional".
    """
    return handlers.audit_repo(path, severity=severity)


@mcp.tool()
def explain_rule(rule_id: str) -> dict[str, Any]:
    """Return the handbook entry for a rule (e.g., "RL002", "PYTHON_LO001")."""
    return handlers.explain_rule(rule_id)


@mcp.tool()
def list_rules(stack: str | None = None, severity: str | None = None) -> dict[str, Any]:
    """List registered governance rules, optionally filtered by stack and severity."""
    return handlers.list_rules(stack=stack, severity=severity)


@mcp.tool()
def report_portfolio(path: str, maxdepth: int = 2) -> dict[str, Any]:
    """Scan a directory for governed repos and return a per-repo portfolio report."""
    return handlers.report_portfolio(path, maxdepth=maxdepth)


@mcp.tool()
def diff_portfolio(path: str, against: str | None = None, maxdepth: int = 2) -> dict[str, Any]:
    """Diff the current portfolio scan against a snapshot (latest by default)."""
    return handlers.diff_portfolio(path, against=against, maxdepth=maxdepth)


def run() -> None:
    """Launch the MCP server over stdio."""
    mcp.run()


if __name__ == "__main__":
    run()
