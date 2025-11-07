// Embassy.js for Bitcoin Seconds
// Standalone file with no imports - all code inlined
// Config spec is defined inline matching working packages' pattern

// Minimal compat.getConfig implementation
// compat.getConfig takes a config spec object and returns a function
// that Start9 can call to get the config spec
// The function must return the spec object directly (not stringified, not wrapped)
function createGetConfig(spec) {
  // Return a function that matches Start9's expected signature
  // Start9 calls this function and expects the spec object directly
  // Try both async and sync versions - Start9 might expect sync
  return function getConfigFunction(effects) {
    // Return the config spec object directly
    // CRITICAL: Must return the object itself, not JSON.stringify(spec)
    // Start9 will handle serialization internally
    return spec;
  };
}

// Config specification inline (from config_spec.yaml)
const configSpec = {
  "mock-mode": {
    "type": "boolean",
    "name": "Mock Mode",
    "description": "Use synthetic data instead of real Bitcoin node data.\nEnable for testing, disable to use real Bitcoin Core/Knots and Mempool data.",
    "default": true
  },
  "bitcoin-rpc-user": {
    "type": "pointer",
    "name": "Bitcoin RPC Username",
    "description": "RPC username from Bitcoin Core/Knots service (auto-filled when dependency is connected)",
    "subtype": "package",
    "package-id": "bitcoind",
    "target": "config",
    "selector": "rpc.username"
  },
  "bitcoin-rpc-password": {
    "type": "pointer",
    "name": "Bitcoin RPC Password",
    "description": "RPC password from Bitcoin Core/Knots service (auto-filled when dependency is connected)",
    "subtype": "package",
    "package-id": "bitcoind",
    "target": "config",
    "selector": "rpc.password"
  },
  "mempool-api-url": {
    "type": "pointer",
    "name": "Mempool API URL",
    "description": "API URL from Mempool service (auto-filled when dependency is connected)",
    "subtype": "package",
    "package-id": "mempool",
    "target": "interface",
    "selector": "main.url"
  },
  "alert-drop-pct": {
    "type": "number",
    "name": "Alert Drop Percentage",
    "description": "Trigger alert when flow rate f(t) drops by this percentage (0-100)",
    "nullable": false,
    "integral": false,
    "units": "percent",
    "range": "[0, 100]",
    "default": 20
  },
  "alert-window-days": {
    "type": "number",
    "name": "Alert Window",
    "description": "Time period for monitoring flow changes (days)",
    "nullable": false,
    "integral": true,
    "units": "days",
    "range": "[1, 90]",
    "default": 14
  },
  "t-min-secs": {
    "type": "number",
    "name": "Minimum Time (t_min)",
    "description": "Floor for elapsed time in SSR calculation (seconds)",
    "nullable": false,
    "integral": true,
    "units": "seconds",
    "range": "[1, 2592000]",
    "default": 1000
  },
  "mu-min-sats-per-s": {
    "type": "number",
    "name": "Minimum Spend Rate (μ_min)",
    "description": "Floor for spend rate in SSR calculation (sats/s)",
    "nullable": false,
    "integral": false,
    "units": "sats/s",
    "range": "[0.0000001, 1.0]",
    "default": 0.000001
  },
  "pipeline-interval-seconds": {
    "type": "number",
    "name": "Pipeline Interval",
    "description": "How often to run the data pipeline (seconds)",
    "nullable": false,
    "integral": true,
    "units": "seconds",
    "range": "[60, 3600]",
    "default": 600
  }
};

// Export getConfig as const (matching working packages pattern)
// When using type: script with config-spec in assets, Start9 reads the spec from YAML
// However, getConfig is still required and should return the spec object
// compat.getConfig({...}) returns a function, so getConfig is a const holding that function
// The function must return the spec object directly (not stringified, not wrapped)
export const getConfig = createGetConfig(configSpec);

// Export setConfig (not used when type: script)
export async function setConfig() {
  return {};
}

// Export other required functions
export const properties = {};
export const dependencies = {};
export const migration = null;
