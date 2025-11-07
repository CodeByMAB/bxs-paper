# Bitcoin Seconds (BXS)

## Overview

Bitcoin Seconds (BXS) measures the **durable accumulation of time-shifted energy claims** in a Bitcoin-denominated economy. 

This service computes:
- **Durability-adjusted Bitcoin flow** `f(t)` [sats/s]
- **Cumulative stock** `S(T)` [sats]
- **Persistence** `BXS(T)` [sats·s]

## What It Does

The BXS service continuously:
1. Collects Bitcoin network data (block height, UTXO age, wallet state)
2. Computes durability metrics using the SSR (Surplus-to-Spending Ratio) framework
3. Stores results in a local SQLite database
4. Displays metrics in an interactive web dashboard
5. Exposes a REST API for querying metrics and alerts

## Accessing the Dashboard

Click "Launch UI" in the Start9 interface or navigate to:
- **LAN**: `https://bitcoin-seconds.local`
- **Tor**: Your unique `.onion` address (shown in Start9)

The dashboard automatically refreshes every 60 seconds and shows:
- All current BXS metrics with descriptions
- Key formulas from the whitepaper
- Real-time status indicators
- Last update timestamp

## API Endpoints

Access the BXS API through your Start9 interface or directly via LAN/Tor:

### Health Check
```bash
GET /healthz
```
Returns `200 OK` if the service is healthy.

### Latest Metrics
```bash
GET /metrics/latest
```
Returns the most recent BXS calculations including:
- Current balance `W`
- Coin age `A`
- Flow rate `f(t)`
- Cumulative stock `S(t)`
- BXS persistence

**Example Response:**
```json
{
  "timestamp": "2024-01-15T12:00:00Z",
  "balance_sats": 100000000,
  "coin_age_seconds": 15552000,
  "flow_rate": 0.00123,
  "cumulative_stock": 100000000,
  "bxs_persistence": 1555200000000
}
```

### Time Range Query
```bash
GET /metrics/range?start=<timestamp>&end=<timestamp>
```
Returns metrics for a specific time period.

Parameters:
- `start`: Unix timestamp or ISO8601 date
- `end`: Unix timestamp or ISO8601 date

### Recent Alerts
```bash
GET /alerts/recent?limit=10
```
Returns recent alerts triggered by significant drops in durability flow.

## Configuration

### Mock Mode

**Default: Enabled**

When mock mode is enabled, the service uses synthetic data for testing without requiring a Bitcoin node connection. This is perfect for:
- Testing the service functionality
- Developing integrations
- Learning how BXS metrics work

### Connecting to Real Bitcoin Data

**No SSH Required!** Configure everything through the Start9 UI:

1. **Install Dependencies** (if not already installed):
   - Go to **Services** → **Marketplace** in Start9 UI
   - Install **Bitcoin Core** (or **Bitcoin Knots**)
   - Install **Mempool.space**
   - Wait for both services to be fully synced and running

2. **Connect Dependencies**:
   - Go to **Services** → **Bitcoin Seconds** → **Dependencies**
   - Connect **Bitcoin Core/Knots** (bitcoind)
   - Connect **Mempool.space** (mempool)
   - This makes the services available to Bitcoin Seconds

3. **Configure Bitcoin Seconds**:
   - Go to **Services** → **Bitcoin Seconds** → **Configure**
   - Set **Mock Mode** to `false` (toggle off)
   - The following fields will **automatically populate** from your dependencies:
     - **Bitcoin RPC Username** (from Bitcoin Core/Knots)
     - **Bitcoin RPC Password** (from Bitcoin Core/Knots)
     - **Mempool API URL** (from Mempool service)
   - Adjust other settings as needed:
     - **Alert Drop Percentage** (default: 20%)
     - **Alert Window** (default: 14 days)
     - **Pipeline Interval** (default: 600 seconds)
   - Click **Save**

4. **Start the Service**:
   - The service will automatically restart with the new configuration
   - Go to **Services** → **Bitcoin Seconds** → **Logs**
   - Look for: "Fetching block data from mempool.space..."
   - Look for: "Fetching wallet data from Bitcoin RPC..."
   - Should NOT see: "Using mock data"

**That's it!** No SSH or manual file editing required.

📖 **Full Guide**: See `CONNECTING_TO_REAL_DATA.md` for troubleshooting and advanced configuration options.

### Alert Settings

**Alert Drop Percentage** (default: 20%)
- Triggers an alert when flow rate `f(t)` drops by this percentage
- Range: 0-100%
- Use lower values for more sensitive alerts

**Alert Window** (default: 14 days)
- Time period for monitoring flow changes
- Range: 1-90 days
- Longer windows smooth out short-term volatility

### Advanced Parameters

**t_min** (default: 1000 seconds)
- Floor for elapsed time in SSR calculation
- Prevents division by zero for new wallets
- Typically set to 1-30 days in seconds

**mu_min** (default: 0.000001 sats/s)
- Floor for spend rate in SSR calculation
- Prevents division by zero for inactive wallets
- Should be set very small but non-zero

**Pipeline Interval** (default: 600 seconds / 10 minutes)
- How often the data pipeline runs
- Range: 60-3600 seconds
- Shorter intervals = more frequent updates, higher resource use

## Understanding BXS Metrics

### Durability Drivers

BXS measures three multiplicative factors:

1. **HODLing Strength**: `A(t)/A₀`
   - Value-weighted coin age vs. baseline
   - Higher = coins held longer = more durable

2. **Protocol Era Context**: `I(t)/I₀`
   - Mechanical expansion rate (inflation)
   - Accounts for Bitcoin's issuance schedule

3. **Financial Runway**: `SSR(t)`
   - Surplus-to-Spending Ratio
   - Formula: `SSR(t) = (s(t) + r·i(t) - CP(t)) / (max{t, t_min} · max{μ(t), μ_min})`
   - Measures how long holdings can sustain current spending, adjusted for future income
   - Higher = more runway before depletion

### Flow Rate f(t)

The durability-adjusted flow rate combines all three factors (per paper eq:flow):

```
f(t) = i(t) × (A(t)/A₀) × (I(t)/I₀) × SSR(t)   [sats/s]
```

Where:
- `i(t)` = income inflow rate [sats/s]
- `A(t)/A₀` = revealed HODLing strength (coin age ratio)
- `I(t)/I₀` = protocol-era context (expansion rate ratio)
- `SSR(t)` = financial runway (surplus-to-spending ratio)
- Positive `f(t)` = accumulating durable claims
- Negative `f(t)` = depleting reserves

### Stock S(T)

Cumulative flow over time (per paper eq:stock):

```
S(T) = ∫₀ᵀ f(t) dt   [sats]
```

Represents total accumulated bitcoin-denominated claims.

### Persistence BXS(T)

Time-weighted stock (per paper eq:bxs):

```
BXS(T) = ∫₀ᵀ S(t) dt   [sats·s]
```

Measured in **bitcoin-seconds** [sats·s], similar to how amp-hours measure battery capacity.

## Use Cases

### Personal Finance
- Monitor your Bitcoin position durability
- Set alerts for unsustainable spending patterns
- Track long-term wealth accumulation

### Research
- Empirical testing of Bitcoin HODLing behavior
- Time-preference studies
- Protocol evolution impact analysis

### Integration
- Dashboard widgets showing BXS metrics
- Automated alerts to other services
- Data export for external analysis

## Troubleshooting

### Service Won't Start

1. Check the service logs in Start9 interface
2. Verify sufficient disk space (database grows over time)
3. Try restarting the service
4. If problems persist, backup data and reinstall

### API Not Responding

1. Verify service is running (check health status)
2. Test health endpoint: `curl http://bitcoin-seconds.embassy:8080/healthz`
3. Check network connectivity (LAN or Tor)
4. Review logs for errors

### No Data / Empty Results

In **mock mode**: This shouldn't happen. Check logs for errors.

In **real mode**: 
1. Verify Bitcoin Core is synced
2. Check RPC credentials are correct
3. Ensure mempool.space service is accessible
4. Review pipeline interval setting (may need to wait)

### High Resource Usage

1. Increase pipeline interval to reduce frequency
2. Check if database is very large (consider archiving old data)
3. Monitor system resources in Start9 interface

## Data Persistence

All data is stored in `/app/data/bxs.sqlite` within the service volume. This includes:
- Historical metrics (timestamps, balances, flow rates)
- Alert history
- Configuration snapshots

**Backup**: Use Start9's built-in backup feature to preserve your BXS database.

## Security & Privacy

- **Local Only**: All computation happens on your Start9 device
- **No External APIs**: In mock mode, no network calls are made
- **Private Data**: Wallet information never leaves your device
- **Tor Support**: Access API over Tor for additional privacy

## Support

- **Documentation**: [GitHub Repository](https://github.com/CodeByMAB/bxs-paper)
- **Issues**: [Report bugs](https://github.com/CodeByMAB/bxs-paper/issues)
- **Paper**: See `/src/` directory for the academic whitepaper

## License

This service is licensed under CC BY 4.0. You are free to share and adapt with attribution.

---

**Bitcoin Seconds v0.1.0**  
Measuring durable accumulation of time-shifted energy claims in Bitcoin
