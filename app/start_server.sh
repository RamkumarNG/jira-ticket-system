#!/bin/bash

set -e

echo "=== Running Alembic migrations ==="
# alembic -c app/alembic.ini upgrade head
(cd /app/ && alembic upgrade head)

echo "=== Starting FastAPI application ==="
uvicorn app.main:app --host 0.0.0.0 --port 10000
