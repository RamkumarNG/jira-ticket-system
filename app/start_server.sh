#!/bin/bash

set -e

echo "=== Current working directory: $(pwd) ==="
echo "=== Files in current directory ==="
ls -l app/alembic.ini

echo "=== Running Alembic migrations ==="
cd /app
python -m alembic -c app/alembic.ini upgrade head


echo "=== Starting FastAPI application ==="
uvicorn main:app --host 0.0.0.0 --port 10000
