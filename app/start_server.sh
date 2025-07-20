#!/bin/bash

set -e

echo "=== Current working directory: $(pwd) ==="
echo "=== Files in current directory ==="
ls -l

echo "=== Running Alembic migrations ==="
# alembic -c app/alembic.ini upgrade head
(cd /app/ && alembic upgrade head)

echo "=== Starting FastAPI application ==="
uvicorn app.main:app --host 0.0.0.0 --port 10000
