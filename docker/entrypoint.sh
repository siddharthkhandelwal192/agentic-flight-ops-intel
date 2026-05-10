#!/usr/bin/env sh
set -e

export PYTHONPATH="${PYTHONPATH:-/app/src}"

echo "Running Alembic migrations..."
alembic upgrade head

echo "Starting uvicorn..."
exec uvicorn afos.api.app:app --host "${API_HOST:-0.0.0.0}" --port "${API_PORT:-8000}"
