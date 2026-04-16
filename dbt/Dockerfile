FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Install dependencies first for better layer caching
COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev --frozen

# Copy dbt project files
COPY dbt_project.yml profiles.yml ./
COPY models-m1/ ./models-m1/
COPY models-m2/ ./models-m2/
COPY analyses/ ./analyses/
COPY tests/ ./tests/
COPY seeds/ ./seeds/
COPY entrypoint.sh start_mcp.py ./
RUN chmod +x entrypoint.sh

CMD ["./entrypoint.sh"]
