#!/bin/bash

# Read .env file and convert to JSON format for Start9 config get
# Outputs JSON matching the config_spec.yaml structure

python3 <<PYTHON_SCRIPT
import json
import os
import sys

# Default values (kebab-case keys to match config_spec.yaml)
config = {
    "mock-mode": True,
    "alert-drop-pct": 0.2,
    "alert-window-days": 14,
    "t-min-secs": 1000,
    "mu-min-sats-per-s": 0.000001,
    "pipeline-interval-seconds": 600,
    "bitcoin-rpc-user": "",
    "bitcoin-rpc-password": "",
    "mempool-api-url": ""
}

# Mapping from .env keys (UPPER_SNAKE_CASE) to config spec keys (kebab-case)
key_mapping = {
    "MOCK_MODE": "mock-mode",
    "ALERT_DROP_PCT": "alert-drop-pct",
    "ALERT_WINDOW_DAYS": "alert-window-days",
    "T_MIN_SECS": "t-min-secs",
    "MU_MIN_SATS_PER_S": "mu-min-sats-per-s",
    "PIPELINE_INTERVAL_SECONDS": "pipeline-interval-seconds",
    "BITCOIN_RPC_USER": "bitcoin-rpc-user",
    "BITCOIN_RPC_PASSWORD": "bitcoin-rpc-password",
    "MEMPOOL_API_URL": "mempool-api-url"
}

# Read .env file if it exists
# When using type: script, Start9 provides EMBASSY_DATA_DIR environment variable
# The .env file is in the service's data directory
import os
data_dir = os.environ.get("EMBASSY_DATA_DIR", "/mnt/data")
env_file = os.path.join(data_dir, ".env")
if os.path.exists(env_file):
    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                
                # Map .env key to config spec key
                config_key = key_mapping.get(key)
                if config_key:
                    # Convert to appropriate types
                    if key == "MOCK_MODE":
                        config[config_key] = value.lower() == "true"
                    elif key in ["ALERT_DROP_PCT", "MU_MIN_SATS_PER_S"]:
                        try:
                            config[config_key] = float(value)
                        except ValueError:
                            pass
                    elif key in ["ALERT_WINDOW_DAYS", "T_MIN_SECS", "PIPELINE_INTERVAL_SECONDS"]:
                        try:
                            config[config_key] = int(value)
                        except ValueError:
                            pass
                    else:
                        config[config_key] = value

# Output as JSON
print(json.dumps(config, indent=2))
PYTHON_SCRIPT

