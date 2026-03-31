#!/usr/bin/env python3
"""
dbt MCP Server Demo Client

This script connects to the dbt MCP server running locally via uvx
and demonstrates how an AI agent can discover and interact with your
data models programmatically.

Usage:
    uv run python demo_client.py

Requirements:
    uv sync  (from pyproject.toml)

The MCP server must be running locally:
    cd dbt && MCP_TRANSPORT=sse DBT_PROJECT_DIR=. DBT_PROFILES_DIR=. uvx dbt-mcp
"""

import asyncio
import json
import sys
from datetime import datetime

# -------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------
MCP_SERVER_URL = "http://localhost:8000/sse"  # Default dbt-mcp SSE endpoint
OUTPUT_LOG = "demo_output.log"


# -------------------------------------------------------------------
# Helper: log to both console and file
# -------------------------------------------------------------------
log_lines = []

def log(message: str):
    """Print to console and capture for log file."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    line = f"[{timestamp}] {message}"
    print(line)
    log_lines.append(line)


def save_log():
    """Write all captured output to the log file."""
    with open(OUTPUT_LOG, "w") as f:
        f.write(f"dbt MCP Demo Output - {datetime.now().isoformat()}\n")
        f.write("=" * 60 + "\n\n")
        for line in log_lines:
            f.write(line + "\n")
    log(f"Output saved to {OUTPUT_LOG}")


# -------------------------------------------------------------------
# Demo Steps
# -------------------------------------------------------------------

async def run_demo():
    """
    Connect to the dbt MCP server and run a series of demonstrations.

    TODO: Students should complete the implementation below using the
    MCP Python SDK. The steps are outlined with descriptions of what
    each section should do.
    """

    # Step 0: Import MCP client library
    # You'll need: from mcp.client.sse import sse_client
    #              from mcp.client.session import ClientSession

    log("=" * 60)
    log("dbt MCP Server Demo")
    log("=" * 60)
    log("")

    # ----- STEP 1: Connect to the MCP server -----
    #
    # Use the SSE client transport to connect to the server.
    # The connection URL should match MCP_SERVER_URL above.
    #
    # Example pattern:
    #   async with sse_client(MCP_SERVER_URL) as (read, write):
    #       async with ClientSession(read, write) as session:
    #           await session.initialize()
    #           ... rest of demo ...
    #
    log("Step 1: Connecting to dbt MCP server...")
    # TODO: Implement connection
    # log("Connected successfully!")


    # ----- STEP 2: List available tools -----
    #
    # IMPORTANT: Run this step first! Tool names may change between
    # dbt-mcp versions. Use the output here to discover the actual
    # tool names for Steps 3-6.
    #
    # Call session.list_tools() to see what capabilities the MCP server exposes.
    # Print each tool's name and description.
    #
    # As of dbt-mcp 0.2.x, common tools include:
    #   - list: List dbt resources (models, sources, etc.)
    #   - get_node_details_dev: Get detailed info about a specific node
    #   - compile: Compile SQL for a model
    #   - get_lineage_dev: Get upstream/downstream dependencies
    #   - show: Execute a SQL query against the database
    #
    log("")
    log("Step 2: Listing available tools...")
    # TODO: Implement tool listing
    # tools = await session.list_tools()
    # for tool in tools.tools:
    #     log(f"  - {tool.name}: {tool.description[:100]}")


    # ----- STEP 3: List all dbt models -----
    #
    # Use the "list" tool to list all models in the dbt project.
    # Print model names and their descriptions.
    #
    # Hint: result = await session.call_tool("list", {"resource_type": "model"})
    #
    log("")
    log("Step 3: Discovering dbt models...")
    # TODO: Implement model listing


    # ----- STEP 4: Get details on a specific model -----
    #
    # Pick one of your staging or intermediate models and request
    # its full details: columns, tests, upstream/downstream dependencies.
    #
    # Hint: result = await session.call_tool("get_node_details_dev", {"node_id": "stg_ecom__sales_orders"})
    #
    log("")
    log("Step 4: Getting details for a specific model...")
    # TODO: Implement model detail retrieval


    # ----- STEP 5: Compile SQL for a model -----
    #
    # Ask the MCP server to compile the SQL for one of your models.
    # This shows the fully resolved SQL that dbt would execute.
    #
    # Hint: result = await session.call_tool("compile", {"models": "int_sales_order_line_items"})
    #
    log("")
    log("Step 5: Compiling SQL for a model...")
    # TODO: Implement SQL compilation


    # ----- STEP 6: Explore model lineage -----
    #
    # Use get_lineage_dev to trace the lineage of a model:
    # what are its upstream sources and downstream dependents?
    #
    # Hint: result = await session.call_tool("get_lineage_dev", {
    #     "unique_id": "model.adventure.stg_ecom__sales_orders",
    #     "depth": 2,
    # })
    # Note: unique_id format is "model.<project_name>.<model_name>"
    #
    log("")
    log("Step 6: Exploring model lineage...")
    # TODO: Implement lineage exploration


    # ----- WRAP UP -----
    log("")
    log("=" * 60)
    log("Demo complete!")
    log("=" * 60)


# -------------------------------------------------------------------
# Main
# -------------------------------------------------------------------

if __name__ == "__main__":
    try:
        asyncio.run(run_demo())
    except KeyboardInterrupt:
        log("\nDemo interrupted by user.")
    except Exception as e:
        log(f"\nError: {e}")
        log("Make sure the dbt MCP server is running locally.")
        log("Start it with: cd dbt && MCP_TRANSPORT=sse DBT_PROJECT_DIR=. DBT_PROFILES_DIR=. uvx dbt-mcp")
        sys.exit(1)
    finally:
        save_log()
