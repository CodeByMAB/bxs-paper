# Bitcoin Seconds (BXS) - Start9 Deployment Guide

## 🎯 Overview

This guide covers the complete process of deploying Bitcoin Seconds as a Start9 service, from building the package to accessing the API on your Start9 device.

## 📋 Prerequisites

### Required
- Docker installed and running
- Node.js and npm installed
- Start9 SDK: `npm install -g @start9labs/start-sdk`
- Start9 device (for final deployment)

### Optional
- Bitcoin Core node (for real data mode)
- Mempool.space service (for blockchain queries)

## 🏗️ Build Process

### Step 1: Build the Docker Image

```bash
cd /path/to/bxs-paper
./start9/build.sh
```

This script will:
- ✅ Check prerequisites (Docker, npm)
- ✅ Build the Docker image (`bxs:0.1.0`)
- ✅ Save image to tarball (118 MB)
- ✅ Set script permissions
- ✅ Create configuration template
- ✅ Verify all package files

**Expected Output:**
```
✓ Docker image built: bxs:0.1.0
✓ Docker image saved: docker_images.tgz (118M)
✓ All package files verified
```

### Step 2: Create the .s9pk Package

```bash
cd /path/to/bxs-paper
start-sdk pack
```

This creates: `bitcoin-seconds.s9pk`

**Note:** The first pack may take a few minutes as it validates all files and creates the package.

## 📱 Installation on Start9

### Via Web Interface

1. **Navigate to Sideload**
   - Open your Start9 web interface
   - Go to **System** → **Sideload Service**

2. **Upload Package**
   - Click **Choose File**
   - Select `bitcoin-seconds.s9pk`
   - Click **Install**

3. **Wait for Installation**
   - Start9 will validate and install the package
   - This may take 2-5 minutes

4. **Configure Service**
   - Navigate to **Services** → **Bitcoin Seconds**
   - Click **Config**
   - Adjust settings (defaults are good for testing)
   - Click **Save**

5. **Start Service**
   - Click **Start**
   - Wait for health check to pass (green status)

### Via SSH (Advanced)

```bash
# Copy package to Start9
scp bitcoin-seconds.s9pk start9@your-start9.local:/tmp/

# SSH into Start9
ssh start9@your-start9.local

# Install package
embassy-cli package install /tmp/bitcoin-seconds.s9pk

# Start service
embassy-cli service start bitcoin-seconds
```

## ⚙️ Configuration

### Default Settings (Recommended for Testing)

```yaml
MOCK_MODE: true                    # Use synthetic data
ALERT_DROP_PCT: 0.2                # Alert on 20% drop
ALERT_WINDOW_DAYS: 14              # Monitor 14-day window
T_MIN_SECS: 1000                   # SSR(t) floor for t: ~16 minutes
MU_MIN_SATS_PER_S: 0.000001       # SSR(t) floor for μ(t): spend rate
PIPELINE_INTERVAL_SECONDS: 600     # Update every 10 minutes
```

### Production Settings (With Bitcoin Node)

```yaml
MOCK_MODE: false                   # Use real Bitcoin data
ALERT_DROP_PCT: 0.15               # More sensitive alerts
ALERT_WINDOW_DAYS: 30              # Longer monitoring period
T_MIN_SECS: 2592000                # 30 days minimum
MU_MIN_SATS_PER_S: 0.00001        # Higher spend floor
PIPELINE_INTERVAL_SECONDS: 300     # Update every 5 minutes
```

**Note:** Production mode requires Bitcoin Core and mempool.space services to be running and accessible.

## 🔌 Accessing the Service

### LAN Access

```bash
# Health check
curl https://bitcoin-seconds.local/healthz

# Latest metrics
curl https://bitcoin-seconds.local/metrics/latest

# Historical data
curl "https://bitcoin-seconds.local/metrics/range?start=2024-01-01T00:00:00Z&end=2024-01-02T00:00:00Z"

# Recent alerts
curl https://bitcoin-seconds.local/alerts/recent?limit=5
```

### Tor Access

1. Find your Tor address in Start9 interface:
   - Services → Bitcoin Seconds → Interfaces → Tor Address

2. Use with Tor browser or `torify`:
   ```bash
   torify curl http://[your-onion-address].onion/healthz
   ```

### API Documentation

Once running, access interactive API docs at:
- **LAN**: `https://bitcoin-seconds.local/docs`
- **Tor**: `http://[your-onion-address].onion/docs`

## 📊 Using the API

### Example: Monitor Your Bitcoin Position

```bash
#!/bin/bash
# get-bxs-status.sh

API_URL="https://bitcoin-seconds.local"

# Get latest metrics
METRICS=$(curl -s "$API_URL/metrics/latest")

# Extract key values (requires jq)
BALANCE=$(echo "$METRICS" | jq -r '.balance_sats')
FLOW=$(echo "$METRICS" | jq -r '.flow_rate')
BXS=$(echo "$METRICS" | jq -r '.bxs_persistence')

echo "Bitcoin Seconds Status"
echo "====================="
echo "Balance: $(($BALANCE / 100000000)) BTC"
echo "Flow Rate: $FLOW sats/s"
echo "BXS Persistence: $BXS sats·s"

# Check for alerts
ALERTS=$(curl -s "$API_URL/alerts/recent?limit=1")
if [ "$(echo "$ALERTS" | jq 'length')" -gt 0 ]; then
    echo "⚠️  Alert: $(echo "$ALERTS" | jq -r '.[0].message')"
fi
```

### Example: Dashboard Integration

```python
import requests
import time

API_URL = "https://bitcoin-seconds.local"

def get_bxs_metrics():
    """Fetch latest BXS metrics."""
    response = requests.get(f"{API_URL}/metrics/latest")
    return response.json()

def monitor_durability():
    """Continuous monitoring of durability flow."""
    while True:
        metrics = get_bxs_metrics()
        
        print(f"Timestamp: {metrics['timestamp']}")
        print(f"Flow Rate: {metrics['flow_rate']:.6f} sats/s")
        print(f"Stock: {metrics['cumulative_stock']:,.0f} sats")
        print(f"BXS: {metrics['bxs_persistence']:,.0f} sats·s")
        print("-" * 50)
        
        time.sleep(600)  # Check every 10 minutes

if __name__ == "__main__":
    monitor_durability()
```

## 🔍 Monitoring & Troubleshooting

### View Logs

**In Start9 Interface:**
- Services → Bitcoin Seconds → Logs

**Via SSH:**
```bash
embassy-cli service logs bitcoin-seconds
```

### Health Check

```bash
# Should return: {"status": "ok"}
curl https://bitcoin-seconds.local/healthz
```

If unhealthy:
1. Check service logs for errors
2. Verify configuration (especially mock mode in testing)
3. Restart service: Services → Bitcoin Seconds → Restart
4. Check system resources (CPU, memory, disk)

### Common Issues

#### Service Won't Start
- **Cause**: Configuration error or insufficient resources
- **Solution**: 
  - Check logs for specific error
  - Verify all required config fields are set
  - Enable mock mode for testing

#### API Not Responding
- **Cause**: Service not fully started or network issue
- **Solution**:
  - Wait 30-60 seconds after start
  - Check health status in Start9 UI
  - Verify network connectivity

#### No Metrics Data
- **In Mock Mode**: Should never happen - check logs
- **In Real Mode**: 
  - Verify Bitcoin Core is synced
  - Check RPC credentials
  - Wait for first pipeline run (10 minutes default)

#### High Resource Usage
- **Cause**: Too frequent pipeline updates
- **Solution**: Increase `PIPELINE_INTERVAL_SECONDS` to 900 or 1800

## 🔄 Updating the Service

### Process

1. **Build new version**
   ```bash
   git pull
   ./start9/build.sh
   embassy-sdk pack start9
   ```

2. **Upload to Start9**
   - System → Sideload Service
   - Upload new `bitcoin-seconds.s9pk`

3. **Start9 handles migration**
   - Stops old version
   - Migrates data
   - Starts new version

4. **Verify update**
   ```bash
   curl https://bitcoin-seconds.local/healthz
   ```

### Data Preservation

Start9 automatically preserves:
- SQLite database (all historical metrics)
- Configuration settings
- Alert history

## 💾 Backup & Restore

### Automatic Backup

Start9 includes BXS data in system backups:
- Services → Bitcoin Seconds → Create Backup

### Manual Export

```bash
# Via SSH
scp start9@your-start9.local:/embassy/volumes/bitcoin-seconds/data/bxs.sqlite ./backup/

# Via API (if admin enabled)
curl https://bitcoin-seconds.local/admin/export > bxs-backup.json
```

### Restore

1. Stop service
2. Replace database file
3. Restart service

## 🧪 Local Development & Testing

### Test Before Deploying

```bash
# Start service locally
docker-compose -f start9/docker-compose.yml up -d

# Run tests
curl http://localhost:8080/healthz
curl http://localhost:8080/metrics/latest

# Check logs
docker-compose -f start9/docker-compose.yml logs -f

# Stop when done
docker-compose -f start9/docker-compose.yml down
```

### Modify and Rebuild

```bash
# Make code changes
vim code/app/main.py

# Rebuild
./start9/build.sh

# Test locally
docker-compose -f start9/docker-compose.yml up --build -d
```

## 📚 Additional Resources

### Documentation
- **User Guide**: `start9/instructions.md`
- **Developer Docs**: `start9/README.md`
- **Package Summary**: `start9/PACKAGE_SUMMARY.md`
- **Main README**: `README.md`
- **Whitepaper**: `src/` directory

### Support
- **Issues**: https://github.com/CodeByMAB/bxs-paper/issues
- **Start9 Docs**: https://docs.start9.com
- **Start9 Forum**: https://community.start9.com

## 📄 License

Bitcoin Seconds is licensed under CC BY 4.0. See LICENSE file.

---

**Version**: 0.1.0  
**Last Updated**: November 6, 2025  
**Status**: Ready for Deployment ✅

