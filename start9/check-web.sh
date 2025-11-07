#!/bin/bash

set -e

# Health check script for Start9
# Returns JSON with health status

HEALTH_URL="http://localhost:8080/healthz"
MAX_RETRIES=5
RETRY_DELAY=2

for i in $(seq 1 $MAX_RETRIES); do
    if curl -sf "$HEALTH_URL" > /dev/null 2>&1; then
        # Health check passed
        cat <<EOF
{
  "version": "2",
  "data": {
    "result": "healthy",
    "message": "BXS API is running and responsive"
  }
}
EOF
        exit 0
    fi
    
    # Wait before retry
    if [ $i -lt $MAX_RETRIES ]; then
        sleep $RETRY_DELAY
    fi
done

# Health check failed after all retries
cat <<EOF
{
  "version": "2",
  "data": {
    "result": "unhealthy",
    "message": "BXS API is not responding. Check logs for details."
  }
}
EOF
exit 1

