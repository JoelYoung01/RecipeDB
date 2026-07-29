#!/bin/sh
set -eu

# Apply schema changes to the persistent SQLite volume before serving traffic.
# Deploy pulls a new image and restarts the container; this is the migrate step.
echo "Running Alembic migrations..."
uv run --no-dev alembic upgrade head
echo "Alembic migrations complete."

exec "$@"
