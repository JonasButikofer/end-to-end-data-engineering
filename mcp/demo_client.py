#!/usr/bin/env python3
"""
dbt MCP Server Demo Client

Connects to the dbt MCP server running in Docker and demonstrates how an
AI agent can discover and interact with the Adventure Works data models.

Usage:
    uv run python demo_client.py

Requirements:
    uv sync  (from pyproject.toml in this directory)

The MCP server must be running:
    docker compose up -d dbt-mcp
"""

import asyncio
import json
import sys
from datetime import datetime

# -------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------
MCP_SERVER_URL = "http://localhost:8000/sse"
OUTPUT_LOG = "demo_output.log"


# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------
log_lines = []

def log(message: str = ""):
    timestamp = datetime.now().strftime("%H:%M:%S")
    line = f"[{timestamp}] {message}"
    print(line)
    log_lines.append(line)


def save_log():
    with open(OUTPUT_LOG, "w") as f:
        f.write(f"dbt MCP Demo Output - {datetime.now().isoformat()}\n")
        f.write("=" * 60 + "\n\n")
        for line in log_lines:
            f.write(line + "\n")
    log(f"Output saved to {OUTPUT_LOG}")


def parse_content(result):
    """
    Extract text from an MCP tool result and attempt JSON parsing.
    MCP tools return result.content as a list of content blocks.
    Some tools return JSON, others return plain text — this handles both.
    Returns (text, parsed_dict_or_None).
    Also prints ALL content blocks raw so we can see the full response shape.
    """
    all_text = "\n".join(
        block.text for block in result.content if hasattr(block, "text")
    )
    try:
        return all_text, json.loads(all_text)
    except (json.JSONDecodeError, AttributeError):
        return all_text, None


def log_raw(result):
    """Print every content block so we can see the actual response shape."""
    for i, block in enumerate(result.content):
        text = getattr(block, "text", repr(block))
        log(f"  [block {i}]: {text[:300]}")


# -------------------------------------------------------------------
# Demo
# -------------------------------------------------------------------

async def run_demo():
    # Imported here — only available after `uv sync` in the mcp/ directory
    from mcp.client.sse import sse_client
    from mcp.client.session import ClientSession

    log("=" * 60)
    log("dbt MCP Server Demo — Adventure Works Pipeline")
    log("=" * 60)

    # ----- STEP 1: Connect -----
    # sse_client opens a persistent HTTP connection to the SSE endpoint.
    # ClientSession wraps it in the MCP protocol (handshake, framing, matching).
    # All steps live inside both context managers — exiting either closes the connection.
    log()
    log("Step 1: Connecting to dbt MCP server...")

    async with sse_client(MCP_SERVER_URL) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            log("Connected successfully!")

            # ----- STEP 2: List available tools -----
            # list_tools() returns the server's full tool catalog.
            # We run this first to confirm exact tool names for steps 3-6.
            log()
            log("Step 2: Listing available tools...")
            try:
                tools = await session.list_tools()
                log(f"  {len(tools.tools)} tools available:")
                for tool in tools.tools:
                    # description is multi-line — just show the first line
                    first_line = tool.description.strip().splitlines()[0]
                    log(f"  - {tool.name}: {first_line}")
            except Exception as e:
                log(f"  Step 2 failed: {e}")

            # ----- STEP 3: Discover all dbt models with descriptions -----
            # The "list" tool maps to `dbt ls`. It returns a plain-text
            # newline-separated list of resource names — NOT JSON.
            # We ask for models only via resource_type, then call
            # get_node_details_dev on each to retrieve the description.
            log()
            log("Step 3: Discovering dbt models with descriptions...")
            try:
                # resource_type must be a list, not a string
                result = await session.call_tool("list", {"resource_type": ["model"]})
                raw, _ = parse_content(result)

                # The response is "project.model_name" per line — strip the prefix
                model_lines = [line.strip() for line in raw.strip().splitlines() if line.strip()]
                model_names = [m.split(".")[-1] for m in model_lines]
                log(f"  Found {len(model_names)} models:")

                for name in model_names:
                    # Fetch the description for each model from its node details
                    try:
                        detail_result = await session.call_tool(
                            "get_node_details_dev", {"node_id": name}
                        )
                        _, detail = parse_content(detail_result)
                        if detail:
                            desc = detail.get("description", "").strip()
                            first_sentence = desc.split(".")[0] + "." if desc else "(no description)"
                            log(f"  - {name}: {first_sentence}")
                        else:
                            log(f"  - {name}: (could not fetch description)")
                    except Exception as e:
                        log(f"  - {name}: (error: {e})")
            except Exception as e:
                log(f"  Step 3 failed: {e}")

            # ----- STEP 4: Detailed info on a specific model -----
            # get_node_details_dev returns full metadata for a node:
            # description, column definitions with their descriptions,
            # and data tests. We use int_sales_orders_with_campaign
            # because it's the central campaign-attribution model.
            log()
            log("Step 4: Full details for int_sales_orders_with_campaign...")
            try:
                result = await session.call_tool(
                    "get_node_details_dev",
                    {"node_id": "int_sales_orders_with_campaign"}
                )
                _, details = parse_content(result)

                if details:
                    log(f"  Model: int_sales_orders_with_campaign")

                    desc = details.get("description", "").strip()
                    if desc:
                        log(f"  Description:")
                        for line in desc.splitlines():
                            log(f"    {line}")
                    else:
                        # Description missing — show raw keys so we know the structure
                        log(f"  (description field empty — raw top-level keys: {list(details.keys())})")

                    # Columns may be a dict or list depending on dbt-mcp version
                    columns = details.get("columns", details.get("column_info", {}))
                    log(f"  Columns ({len(columns)}):")
                    items = columns.items() if isinstance(columns, dict) else enumerate(columns)
                    for col_name, col_info in items:
                        desc = ""
                        if isinstance(col_info, dict):
                            desc = col_info.get("description", col_info.get("comment", ""))
                        elif isinstance(col_info, str):
                            desc = col_info
                        log(f"    - {col_name}: {desc}")

                    depends_on = details.get("depends_on", {}).get("nodes", [])
                    if depends_on:
                        log(f"  Depends on:")
                        for dep in depends_on:
                            log(f"    <- {dep.split('.')[-1]}")
                else:
                    log("  (could not parse JSON — raw response blocks:)")
                    log_raw(result)
            except Exception as e:
                log(f"  Step 4 failed: {e}")

            # ----- STEP 5: Compile SQL for a model -----
            # The "compile" tool resolves all Jinja templating in a model
            # and returns the raw SQL that dbt would execute against Snowflake.
            # ref() and source() calls are replaced with real schema.table names.
            # We compile int_sales_order_with_customers — the dashboard model —
            # to show its 30-day filter and customer join in plain SQL.
            log()
            log("Step 5: Compiled SQL for int_sales_order_with_customers...")
            try:
                # The "compile" tool runs dbt compile and writes SQL to files inside
                # the container — it returns "OK" on success, not the SQL text.
                # Instead, we use the "show" tool which compiles AND executes the
                # model query, returning real rows from Snowflake. This is more
                # useful for a demo: it proves the full pipeline works end to end.
                result = await session.call_tool(
                    "show",
                    {
                        "sql_query": "select * from {{ ref('int_sales_order_with_customers') }}",
                        "limit": 5,
                    }
                )
                raw, _ = parse_content(result)
                lines = raw.strip().splitlines()
                log(f"  Sample rows from int_sales_order_with_customers ({len(lines)} lines):")
                for line in lines[:30]:
                    log(f"    {line}")
                if len(lines) > 30:
                    log(f"    ... ({len(lines) - 30} more lines)")
            except Exception as e:
                log(f"  Step 5 failed: {e}")

            # ----- STEP 6: Explore model lineage -----
            # get_lineage_dev traces the dependency graph for a node.
            # unique_id format: "model.<project_name>.<model_name>"
            # Our dbt project is named "adventure" (dbt_project.yml).
            # depth=2 follows the graph 2 hops in each direction, showing
            # grandparent sources as well as direct parents.
            log()
            log("Step 6: Lineage for int_sales_order_with_customers (depth=2)...")
            try:
                result = await session.call_tool(
                    "get_lineage_dev",
                    {
                        "unique_id": "model.adventure.int_sales_order_with_customers",
                        "depth": 2,
                    }
                )
                raw, lineage = parse_content(result)

                if lineage:
                    # Response keys are "parents" and "children", each a list of
                    # nested objects: {"model_id": "model.adventure.X", "parents": [...]}
                    def extract_ids(nodes):
                        ids = []
                        for node in nodes:
                            if isinstance(node, dict):
                                ids.append(node.get("model_id", str(node)).split(".")[-1])
                            else:
                                ids.append(str(node).split(".")[-1])
                        return ids

                    parents = extract_ids(lineage.get("parents", []))
                    children = extract_ids(lineage.get("children", []))

                    log(f"  Upstream ({len(parents)} nodes):")
                    for node in parents:
                        log(f"    <- {node}")
                    log(f"  Downstream ({len(children)} nodes):")
                    if children:
                        for node in children:
                            log(f"    -> {node}")
                    else:
                        log("    (none — this is the final model in the pipeline)")
                else:
                    log("  (could not parse JSON — raw blocks:)")
                    log_raw(result)
            except Exception as e:
                log(f"  Step 6 failed: {e}")

    # ----- WRAP UP -----
    log()
    log("=" * 60)
    log("Demo complete!")
    log("=" * 60)


# -------------------------------------------------------------------
# Entry point
# -------------------------------------------------------------------

if __name__ == "__main__":
    try:
        asyncio.run(run_demo())
    except KeyboardInterrupt:
        log("\nDemo interrupted by user.")
    except Exception as e:
        log(f"\nError: {e}")
        log("Make sure the dbt MCP server is running: docker compose up -d dbt-mcp")
        sys.exit(1)
    finally:
        save_log()
