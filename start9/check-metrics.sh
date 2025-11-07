#!/bin/bash

# Health check script for Metrics API endpoint
# Returns JSON with health status
# Accepts 503 as valid (service running but initializing)

METRICS_URL="http://localhost:8080/metrics/latest"
MAX_RETRIES=5
RETRY_DELAY=2

for i in $(seq 1 $MAX_RETRIES); do
    # Get HTTP status code (don't fail on 503)
    http_code=$(curl -s -o /dev/null -w "%{http_code}" "$METRICS_URL" 2>/dev/null || echo "000")
    
    # If we get a response (200 or 503), service is running
    # 200 = ready, 503 = initializing (both are healthy states)
    if [ "$http_code" = "200" ] || [ "$http_code" = "503" ]; then
        # Health check passed - service is running
        ready_status="false"
        if [ "$http_code" = "200" ]; then
            ready_status="true"
        fi
        
        cat <<EOF
{
  "version": "2",
  "data": {
    "result": "healthy",
    "message": "Metrics API is running (ready: $ready_status)"
  }
}
EOF
        exit 0
    fi
    
    # Connection error (000) or other error - wait and retry
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
    "message": "Metrics API is not responding. Check logs for details."
  }
}
EOF
exit 1

