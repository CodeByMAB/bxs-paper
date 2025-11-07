# Quick Start: Connect to Real Bitcoin Data

## 🚀 5-Minute Setup

### Step 1: SSH into Start9
```bash
ssh start9@your-start9.local
```

### Step 2: Navigate to Service Directory
```bash
cd /mnt/embassy-data/services/bitcoin-seconds
```

### Step 3: Create/Edit .env File
```bash
nano .env
```

### Step 4: Add Configuration
Paste this (replace with your actual values):

```bash
# Disable mock mode
MOCK_MODE=false

# Bitcoin Core RPC (get these from Bitcoin Core service in Start9 UI)
BITCOIN_RPC_URL=http://bitcoin-core.embassy:8332
BITCOIN_RPC_USER=your_rpc_username
BITCOIN_RPC_PASSWORD=your_rpc_password

# Mempool.space (usually this URL works for Start9)
MEMPOOL_API_URL=https://mempool.local

# Keep defaults or adjust as needed
PIPELINE_INTERVAL_SECONDS=600
ALERT_DROP_PCT=0.2
ALERT_WINDOW_DAYS=14
```

### Step 5: Save and Exit
- Press `Ctrl+X`
- Press `Y` to confirm
- Press `Enter` to save

### Step 6: Restart Service
Go to Start9 UI → Services → Bitcoin Seconds → Restart

## ✅ Verify It's Working

1. **Check logs** (Start9 UI → Bitcoin Seconds → Logs):
   - Look for: "Fetching block data from mempool.space..."
   - Look for: "Fetching wallet data from Bitcoin RPC..."
   - Should NOT see: "Using mock data"

2. **Check API**:
   ```bash
   curl https://bitcoin-seconds.local/metrics/latest
   ```
   - Should show real values (not mock data)
   - Balance should match your Bitcoin Core wallet

## 🔍 Finding Your Bitcoin Core RPC Credentials

1. Open Start9 UI
2. Go to **Services** → **Bitcoin Core**
3. Look for **Connection Info** or **RPC Settings**
4. Copy:
   - RPC URL (usually `http://bitcoin-core.embassy:8332`)
   - Username
   - Password

## ❌ Troubleshooting

**"Connection refused" to Bitcoin RPC:**
- Verify Bitcoin Core service is running
- Check RPC URL uses service name: `bitcoin-core.embassy` (not `127.0.0.1`)
- Verify credentials match Bitcoin Core config

**Still seeing mock data:**
- Verify `.env` file has `MOCK_MODE=false` (not `"false"` or `False`)
- Restart service after editing `.env`
- Check logs for "MOCK_MODE" to see what value is used

**Mempool API errors:**
- Verify mempool.space service is running
- Try: `curl https://mempool.local/api/blocks` to test

## 📖 Full Documentation

For detailed instructions, troubleshooting, and advanced options, see:
- `CONNECTING_TO_REAL_DATA.md` - Complete guide
- `instructions.md` - Service documentation

---

**That's it!** Your service should now be using real Bitcoin data. 🎉

