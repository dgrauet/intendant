"""Unit tests for the `intendant mcp` CLI command."""

from __future__ import annotations

import sys
from unittest.mock import patch

from typer.testing import CliRunner

from intendant.cli import app

cli_runner = CliRunner()


def test_mcp_command_registered() -> None:
    """`intendant mcp` appears in the help output."""
    result = cli_runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "mcp" in result.output


def test_mcp_command_friendly_error_when_extra_missing() -> None:
    """When the mcp package import fails, the command exits 1 with a helpful message."""
    with patch.dict(sys.modules, {"intendant.mcp_server.server": None}):
        result = cli_runner.invoke(app, ["mcp"])
    assert result.exit_code == 1
    assert "[mcp]" in result.output or "mcp" in result.output.lower()
