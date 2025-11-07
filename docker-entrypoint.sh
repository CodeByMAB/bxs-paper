#!/bin/bash
set -e

# Ensure we're in the app directory (WORKDIR is /app, but be explicit)
cd /app || exit 1

# Load environment variables from .env if it exists
if [ -f /app/.env ]; then
    export $(cat /app/.env | grep -v '^#' | xargs)
fi

# Set defaults (8080 for Start9, can be overridden)
API_PORT=${API_PORT:-8080}
PIPELINE_INTERVAL_SECONDS=${PIPELINE_INTERVAL_SECONDS:-600}
DB_PATH=${DB_PATH:-/app/data/bxs.sqlite}

# Initialize database if it doesn't exist
if [ ! -f "$DB_PATH" ]; then
    echo "Initializing database at $DB_PATH..."
    echo "Current directory: $(pwd)"
    
    # Copy schema file from /app/schema.sql to /app/data/schema.sql
    # (Volume mount at /app/data overwrites the directory, so we copy it at runtime)
    mkdir -p "$(dirname "$DB_PATH")"
    if [ -f /app/schema.sql ]; then
        cp /app/schema.sql /app/data/schema.sql
        echo "Copied schema file from /app/schema.sql to /app/data/schema.sql"
    else
        echo "ERROR: Schema file not found at /app/schema.sql"
        exit 1
    fi
    
    python3 code/cli.py --init --db "$DB_PATH" --schema /app/data/schema.sql || echo "Database initialization failed, continuing..."
fi

# Function to handle shutdown
cleanup() {
    echo "Shutting down..."
    kill $PIPELINE_PID $API_PID 2>/dev/null || true
    wait $PIPELINE_PID $API_PID 2>/dev/null || true
    exit 0
}

# Trap signals for graceful shutdown
trap cleanup SIGTERM SIGINT

# Start data pipeline as background process (runs periodically)
echo "Starting data pipeline runner..."
python3 code/pipeline_runner.py &
PIPELINE_PID=$!

# Start FastAPI server
echo "Starting BXS API on port $API_PORT..."
python3 -m uvicorn code.app.main:app --host 0.0.0.0 --port "$API_PORT" &
API_PID=$!

# Wait for either process to exit
wait -n

# If we get here, one process died
cleanup

