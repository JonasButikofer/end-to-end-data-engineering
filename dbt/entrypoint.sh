#!/usr/bin/env bash
set -e

echo "==> Seeding dbt project..."
uv run dbt seed --profiles-dir . --project-dir . || echo "==> Seed failed (warehouse quota may be exceeded) — continuing with existing seed tables."

echo "==> Compiling dbt project to generate target/manifest.json..."
uv run dbt compile --profiles-dir . --project-dir .

echo "==> Starting dbt MCP server on port 8000..."
exec uv run python start_mcp.py
