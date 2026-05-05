"""`intendant mcp` — launch the MCP server (stdio transport).

Requires the optional ``mcp`` extra. Install with::

    uv tool install 'intendant[mcp]'
"""

from __future__ import annotations

import typer
from rich.console import Console

console = Console(stderr=True)


def mcp() -> None:
    """Launch the intendant MCP server (stdio). Requires the [mcp] extra."""
    try:
        from intendant.mcp_server.server import run
    except ImportError:
        console.print(
            "[red]Error:[/red] the `mcp` extra is not installed.\n"
            "Install it with: [cyan]uv tool install 'intendant[mcp]'[/cyan] "
            "(or [cyan]uv pip install 'intendant[mcp]'[/cyan])"
        )
        raise typer.Exit(code=1) from None
    run()
