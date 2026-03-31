# Setting Up and Running the dbt MCP Server Demo

This guide walks you through starting the dbt MCP server locally, verifying it's working, and running the Python demo client script.

---

## Prerequisites

Before you begin, make sure you have:

- [x] Milestones 1 and 2 complete (dbt models building, data flowing, tests passing)
- [x] `uv` installed ([install guide](https://docs.astral.sh/uv/getting-started/installation/))
- [x] `dbt-snowflake` installed and on your PATH (e.g., `uv tool install dbt-snowflake`)
- [x] Python 3.11 or 3.12 available
- [x] Valid Snowflake credentials in your `.env` file
- [x] Your dbt project builds successfully (`cd dbt && dbt build`)
- [x] A `profiles.yml` file exists in your `dbt/` directory (copy from `~/.dbt/profiles.yml` if needed)

---

## Step 1: Start the dbt MCP Server

The dbt MCP server runs **locally** (not in Docker). It's distributed as a Python package and launched via `uvx`. You must run it from inside your `dbt/` directory:

```bash
# From your dbt directory (not project root):
cd dbt
MCP_TRANSPORT=sse \
DBT_PROJECT_DIR=. \
DBT_PROFILES_DIR=. \
uvx dbt-mcp
```

> [!IMPORTANT]
> The server must be started from the `dbt/` directory. Some MCP tools (like lineage) look for `target/manifest.json` relative to the current working directory.

You should see output like:

```
INFO [dbt_mcp.mcp.server] Registering dbt cli tools
INFO [dbt_mcp.mcp.server] Registering dbt codegen tools
INFO:     Uvicorn running on http://127.0.0.1:8000
```

Leave this terminal running. Open a new terminal for the next steps.

> [!TIP]
> If you see `BinaryExecutionError: Cannot execute binary dbt`, make sure `dbt` is on your PATH. Run `which dbt` to check. If not found, install it with `uv tool install dbt-snowflake`.

---

## Step 2: Verify Server is Running

From a **separate terminal**, test the SSE endpoint:

```bash
curl -s http://localhost:8000/sse | head -3
```

You should see an SSE event stream like:

```
event: endpoint
data: /messages/?session_id=abc123...
```

If you get "Connection refused", the server hasn't finished starting yet. Wait a few seconds and try again.

---

## Step 3: Install Demo Client Dependencies

The demo client is a Python script that uses the MCP SDK to connect to the server. Set up a virtual environment:

```bash
mkdir -p mcp
cd mcp

# Copy the pyproject.toml for MCP dependencies
cp ../templates/m3/mcp_pyproject.toml pyproject.toml

# Create venv and install dependencies
uv sync
```

This installs:
- `mcp` — The MCP Python client library
- `httpx` — HTTP client for SSE transport
- `python-dotenv` — Environment variable loading

---

## Step 4: Run the Demo Script

With the MCP server running in another terminal and dependencies installed:

```bash
uv run python demo_client.py
```

The script connects to the MCP server and runs through six demonstration steps:

1. Connects to the server via SSE
2. Lists all available MCP tools (this is the discovery step)
3. Lists dbt models in your project
4. Gets detailed information about a specific model
5. Compiles SQL for a model
6. Explores model lineage (upstream and downstream dependencies)

All output goes to both the console and `demo_output.log`.

> [!IMPORTANT]
> **Step 2 (tool discovery) is the most important step.** Tool names may change between dbt-mcp versions. Always run the discovery step first and verify the actual tool names before hardcoding them in subsequent calls.

---

## Step 5: Review Output

Check the log file to see the full output:

```bash
cat demo_output.log
```

You should see:
- A successful connection message
- A list of available tools (e.g., `list`, `get_node_details_dev`, `compile`, `get_lineage_dev`, `show`)
- Your dbt models listed
- Detailed node info for at least one model
- Compiled SQL showing the fully resolved query
- Lineage showing upstream and downstream dependencies

---

## Troubleshooting

### "Connection refused" when curling SSE endpoint

The server may still be starting. Wait a few seconds and try again. Check the terminal where the server is running for error messages.

### Snowflake authentication errors

Your credentials aren't working. Verify by testing dbt directly:

```bash
cd dbt
dbt debug
```

If `dbt debug` fails, fix your Snowflake credentials first.

### "Cannot execute binary dbt"

The `dbt` CLI is not on your PATH. Install it:

```bash
uv tool install dbt-snowflake
```

Then verify: `which dbt` should return a path.

### "DBT_PROJECT_DIR environment variable is required"

You forgot to set the environment variables. Make sure to include all three:

```bash
cd dbt
MCP_TRANSPORT=sse DBT_PROJECT_DIR=. DBT_PROFILES_DIR=. uvx dbt-mcp
```

### "No such file or directory: './target/manifest.json'"

You started the server from the project root instead of the `dbt/` directory. Run `cd dbt` first, then start the server with `DBT_PROJECT_DIR=.`.

### Demo script hangs on connection

The SSE endpoint URL may be wrong. The default is `http://localhost:8000/sse`. Verify the server is running and check what port it reports in its startup output.

### Demo script can't find tools or models

The MCP server may have started but failed to parse your dbt project. Check:

1. Are you running from inside the `dbt/` directory?
2. Does `dbt_project.yml` exist in the current directory?
3. Does `profiles.yml` exist and contain valid Snowflake config?
4. Are there any YAML syntax errors in your model files? Run `dbt parse` to check.

---

## Stopping the MCP Server

Press `Ctrl+C` in the terminal where the server is running.
