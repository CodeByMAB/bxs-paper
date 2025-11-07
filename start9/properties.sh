#!/bin/bash

set -e

# Read current configuration
MOCK_MODE="${MOCK_MODE:-true}"
ALERT_DROP_PCT="${ALERT_DROP_PCT:-0.2}"
ALERT_WINDOW_DAYS="${ALERT_WINDOW_DAYS:-14}"
T_MIN_SECS="${T_MIN_SECS:-1000}"
MU_MIN_SATS_PER_S="${MU_MIN_SATS_PER_S:-0.000001}"
PIPELINE_INTERVAL_SECONDS="${PIPELINE_INTERVAL_SECONDS:-600}"

# Output properties in YAML format
cat <<EOF
version: 2
data:
  MOCK_MODE:
    type: boolean
    value: ${MOCK_MODE}
    description: Use internal data generators instead of real node RPC
    copyable: false
    qr: false
    masked: false
  ALERT_DROP_PCT:
    type: string
    value: "${ALERT_DROP_PCT}"
    description: Trigger alert when f(t) falls by this fraction
    copyable: false
    qr: false
    masked: false
  ALERT_WINDOW_DAYS:
    type: string
    value: "${ALERT_WINDOW_DAYS}"
    description: Alert monitoring window in days
    copyable: false
    qr: false
    masked: false
  T_MIN_SECS:
    type: string
    value: "${T_MIN_SECS}"
    description: Floor for elapsed time in SSR calculation
    copyable: false
    qr: false
    masked: false
  MU_MIN_SATS_PER_S:
    type: string
    value: "${MU_MIN_SATS_PER_S}"
    description: Floor for spend rate in SSR calculation
    copyable: false
    qr: false
    masked: false
  PIPELINE_INTERVAL_SECONDS:
    type: string
    value: "${PIPELINE_INTERVAL_SECONDS}"
    description: How often to run the data pipeline (seconds)
    copyable: false
    qr: false
    masked: false
  API_URL:
    type: string
    value: "http://bitcoin-seconds.embassy:8080"
    description: API endpoint URL
    copyable: true
    qr: false
    masked: false
EOF

