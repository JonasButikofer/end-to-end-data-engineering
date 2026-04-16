"""Wrapper to start dbt-mcp with configurable host binding.

The upstream dbt-mcp hardcodes host=127.0.0.1 in the FastMCP constructor,
which prevents Docker port mapping from working. This wrapper overrides
server.settings.host after creation so FASTMCP_HOST is respected.
"""

import asyncio
import os

from dbt_mcp.config.config import load_config
from dbt_mcp.config.transport import validate_transport
from dbt_mcp.mcp.server import create_dbt_mcp


def main() -> None:
    config = load_config()
    server = asyncio.run(create_dbt_mcp(config))

    host = os.environ.get("FASTMCP_HOST")
    if host:
        server.settings.host = host

    transport = validate_transport(os.environ.get("MCP_TRANSPORT", "stdio"))
    server.run(transport=transport)


if __name__ == "__main__":
    main()