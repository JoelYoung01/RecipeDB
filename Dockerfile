FROM python:3.12-slim

# Install uv (copy the static binary from the official image)
COPY --from=ghcr.io/astral-sh/uv:0.11.32 /uv /uvx /bin/

WORKDIR /app

# Compile bytecode and copy (rather than link) packages into the environment
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# Install python dependencies from the lockfile (runtime only, no dev group)
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY dist ./dist
COPY api ./api
COPY alembic ./alembic
COPY alembic.ini ./alembic.ini

# Wire up db location
RUN mkdir -p /app/data
VOLUME /app/data

EXPOSE 8000

CMD ["uv", "run", "--no-dev", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
