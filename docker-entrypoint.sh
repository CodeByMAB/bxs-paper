#!/bin/bash
set -e

# Load environment variables from .env if it exists
if [ -f /app/.env ]; then
    export $(cat /app/.env | grep -v '^#' | xargs)
fi

# Set defaults
API_PORT=${API_PORT:-9090}
PIPELINE_INTERVAL_SECONDS=${PIPELINE_INTERVAL_SECONDS:-600}
DB_PATH=${DB_PATH:-/app/data/bxs.sqlite}

# Initialize database if it doesn't exist
if [ ! -f "$DB_PATH" ]; then
    echo "Initializing database at $DB_PATH..."
    mkdir -p "$(dirname "$DB_PATH")"
    python3 code/cli.py --init --db "$DB_PATH" || echo "Database initialization failed, continuing..."
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

