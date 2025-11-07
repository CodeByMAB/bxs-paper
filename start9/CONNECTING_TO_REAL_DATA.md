# Connecting Bitcoin Seconds to Real Bitcoin Data

This guide explains how to configure Bitcoin Seconds to use real data from your Bitcoin Core node and mempool.space service instead of mock data.

## Prerequisites

Before connecting to real data, ensure you have:

1. **Bitcoin Core** running on your Start9 device
   - Fully synced blockchain
   - RPC enabled
   - Wallet loaded (if tracking your own wallet)

2. **Mempool.space** service running on Start9
   - Accessible via local network
   - API endpoints working

## Configuration Methods

### Method 1: Start9 UI Configuration (Recommended - No SSH Required!)

**This is the easiest way!** Configure everything through the Start9 web interface using dependency pointers:

1. **Install Dependencies** (if not already installed):
   - Go to **Services** → **Marketplace** in Start9 UI
   - Search for and install **Bitcoin Core** (or **Bitcoin Knots**)
   - Search for and install **Mempool.space**
   - Wait for both services to be fully synced and running

2. **Configure Bitcoin Seconds**:
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

3. **Verify Dependencies are Connected**:
   - In the configuration screen, check that the dependency fields show values
   - If fields are empty, go to the **Dependencies** section and ensure Bitcoin Core/Knots and Mempool are selected

4. **Start/Restart the Service**:
   - The service will automatically restart after saving configuration
   - Go to **Services** → **Bitcoin Seconds** → **Logs**
   - Look for: "Fetching block data from mempool.space..."
   - Look for: "Fetching wallet data from Bitcoin RPC..."
   - Should NOT see: "Using mock data"

**That's it!** No SSH or manual file editing required.

### Method 2: SSH Configuration (Fallback)

1. **SSH into your Start9 device:**
   ```bash
   ssh start9@your-start9.local
   ```

2. **Navigate to the service directory:**
   ```bash
   cd /embassy-data/package-data/volumes/bitcoin-seconds
   ```

3. **Create or edit the `.env` file:**
   ```bash
   sudo nano .env
   ```

4. **Add the following configuration:**
   ```bash
   # Disable mock mode
   MOCK_MODE=false

   # Bitcoin Core RPC Configuration
   BITCOIN_RPC_URL=http://bitcoin-core.embassy:8332
   BITCOIN_RPC_USER=your_rpc_username
   BITCOIN_RPC_PASSWORD=your_rpc_password

   # Mempool.space API (local Start9 instance)
   MEMPOOL_API_URL=https://mempool.local

   # Pipeline settings
   PIPELINE_INTERVAL_SECONDS=600

   # Alert settings
   ALERT_DROP_PCT=0.2
   ALERT_WINDOW_DAYS=14
   T_MIN_SECS=1000
   MU_MIN_SATS_PER_S=0.000001
   ```

5. **Get Bitcoin Core RPC credentials:**
   
   If Bitcoin Core is running as a Start9 service:
   - Go to Start9 UI → Services → Bitcoin Core
   - Check the service details for RPC connection info
   - The RPC URL is typically: `http://bitcoin-core.embassy:8332`
   - Username and password are in the service configuration

6. **Restart the Bitcoin Seconds service:**
   ```bash
   # From Start9 UI: Services → Bitcoin Seconds → Restart
   # Or via CLI:
   embassy-cli service restart bitcoin-seconds
   ```

### Method 3: Manual Configuration via SSH (Advanced)

If the UI configuration doesn't work or you need to override values, you can manually edit the `.env` file:

## Finding Your Bitcoin Core RPC Settings

### If Bitcoin Core is a Start9 Service:

1. Open Start9 web interface
2. Navigate to **Services** → **Bitcoin Core**
3. Look for **Connection Info** or **RPC Settings**
4. Note the:
   - RPC URL (usually `http://bitcoin-core.embassy:8332`)
   - RPC Username
   - RPC Password

### If Bitcoin Core is Running Elsewhere:

1. Check your `bitcoin.conf` file:
   ```conf
   server=1
   rpcuser=your_username
   rpcpassword=your_password
   rpcallowip=127.0.0.1
   rpcport=8332
   ```

2. Test the connection:
   ```bash
   curl --user your_username:your_password \
        --data-binary '{"jsonrpc":"1.0","id":"test","method":"getblockchaininfo","params":[]}' \
        http://your-bitcoin-node:8332
   ```

## Finding Your Mempool.space URL

### If Mempool.space is a Start9 Service:

1. Open Start9 web interface
2. Navigate to **Services** → **Mempool.space**
3. Check the **Interfaces** section
4. Use the LAN URL (e.g., `https://mempool.local`)

### If Mempool.space is Running Elsewhere:

- Use the full URL: `https://your-mempool-instance.local`
- Or public instance: `https://mempool.space` (not recommended for privacy)

## Verifying the Connection

After configuring, verify everything works:

1. **Check service logs:**
   ```bash
   # In Start9 UI: Services → Bitcoin Seconds → Logs
   # Or via SSH:
   docker logs bitcoin-seconds.embassy
   ```

2. **Look for successful data fetches:**
   ```
   Fetching block data from mempool.space...
   Fetching wallet data from Bitcoin RPC...
   Pipeline step completed successfully
   ```

3. **Check the API:**
   ```bash
   curl https://bitcoin-seconds.local/metrics/latest
   ```

   You should see real data instead of mock values.

## Troubleshooting

### "Connection refused" to Bitcoin RPC

**Problem:** Can't connect to Bitcoin Core RPC

**Solutions:**
- Verify Bitcoin Core service is running
- Check RPC URL is correct (use service name: `bitcoin-core.embassy`)
- Verify RPC credentials match Bitcoin Core config
- Check if RPC is enabled in Bitcoin Core (`server=1` in bitcoin.conf)
- Ensure Bitcoin Core allows connections from the Bitcoin Seconds container

### "Cannot access mempool.space API"

**Problem:** Mempool.space API calls failing

**Solutions:**
- Verify mempool.space service is running
- Check the URL is correct (try `https://mempool.local`)
- Test manually: `curl https://mempool.local/api/blocks`
- If using public instance, ensure network connectivity

### "No wallet data" or "Balance is 0"

**Problem:** Wallet RPC calls succeed but return empty data

**Solutions:**
- Ensure Bitcoin Core has a wallet loaded
- Check wallet is not encrypted (or unlock it)
- Verify wallet has transactions/UTXOs
- If tracking a specific wallet, ensure it's loaded in Bitcoin Core

### Pipeline Still Using Mock Data

**Problem:** Even after setting `MOCK_MODE=false`, still seeing mock data

**Solutions:**
- Verify `.env` file is in the correct location
- Check environment variable is actually `false` (not `"false"` or `False`)
- Restart the service after changing `.env`
- Check logs for "MOCK_MODE" to see what value is being used
- Ensure `.env` file is readable by the container

## Advanced Configuration

### Custom RPC Endpoint

If Bitcoin Core is on a different machine:

```bash
BITCOIN_RPC_URL=http://192.168.1.100:8332
```

### Custom Mempool Instance

If using a different mempool instance:

```bash
MEMPOOL_API_URL=https://your-custom-mempool.local
```

### Faster Updates

To update more frequently (uses more resources):

```bash
PIPELINE_INTERVAL_SECONDS=300  # Every 5 minutes instead of 10
```

### More Sensitive Alerts

To get alerts for smaller changes:

```bash
ALERT_DROP_PCT=0.15  # Alert on 15% drop instead of 20%
ALERT_WINDOW_DAYS=30  # Monitor 30 days instead of 14
```

## Security Considerations

⚠️ **Important Security Notes:**

1. **RPC Credentials**: Never commit `.env` file with real credentials
2. **Network Access**: Keep RPC access restricted to local network
3. **Wallet Security**: If tracking your own wallet, ensure Bitcoin Core wallet is properly secured
4. **HTTPS**: Use HTTPS for mempool.space when possible
5. **Tor**: Consider accessing the API over Tor for additional privacy

## Next Steps

Once connected to real data:

1. **Monitor the dashboard** to see real-time metrics
2. **Set up alerts** for important threshold changes
3. **Review historical data** via the API
4. **Integrate with other tools** using the REST API

## Support

If you encounter issues:

1. Check the service logs for detailed error messages
2. Verify all prerequisites are met
3. Test each component individually (Bitcoin RPC, mempool API)
4. Open an issue on GitHub with:
   - Error messages from logs
   - Your configuration (with credentials redacted)
   - Steps to reproduce

---

**Happy tracking! 🚀**

