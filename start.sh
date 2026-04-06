#!/usr/bin/env bash
set -e
source .venv/bin/activate
echo "Migrating DB..."
PYTHONPATH=. alembic upgrade head
echo "Starting FastAPI on :8000..."
PYTHONPATH=. uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
