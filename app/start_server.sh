#!/bin/bash

set -e  # Exit on any error

echo "=== Running Alembic migrations ==="
alembic upgrade head

echo "=== Starting FastAPI application ==="
uvicorn app.main:app --host 0.0.0.0 --port 10000
