FROM python:3.11-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Install dependencies first for better layer caching
COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev --frozen

# Copy flow files
COPY flows/ flows/

# Default command: run the flow directly
# Override this in compose.yml if using Prefect deployments
CMD ["uv", "run", "python", "-m", "flows.web_analytics_flow"]
