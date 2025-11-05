# Start9 Configuration Guide

This guide explains how to configure BXS to work with a local Start9 instance running mempool.space and Bitcoin Core.

## Prerequisites

- Start9 device with:
  - Bitcoin Core node (RPC enabled)
  - Mempool.space service (local instance)

## Configuration

### 1. Environment Variables

Create a `.env` file in the project root (copy from `.env.example`):

```bash
# Bitcoin Core RPC
BITCOIN_RPC_URL=http://127.0.0.1:8332
BITCOIN_RPC_USER=your_rpc_user
BITCOIN_RPC_PASSWORD=your_rpc_password

# Mempool.space (local Start9 instance)
MEMPOOL_API_URL=https://mempool.local

# Database
DB_PATH=data/bxs.sqlite

# Admin API (enable for recompute endpoint)
ADMIN_ENABLED=false
```

### 2. Bitcoin Core RPC Setup

Enable RPC in your Bitcoin Core configuration:

```conf
server=1
rpcuser=your_rpc_user
rpcpassword=your_rpc_password
rpcallowip=127.0.0.1
rpcport=8332
```

Restart Bitcoin Core after configuration changes.

### 3. Mempool.space Access

Ensure your local mempool.space instance is accessible at `https://mempool.local` (or update `MEMPOOL_API_URL` in `.env`).

For Start9, the mempool service typically runs on a local domain. Check your Start9 dashboard for the exact URL.

### 4. Mock Mode (Development)

If you don't have local access to mempool.space or Bitcoin Core RPC, you can use mock mode:

```bash
export MOCK_MODE=true
```

This will use deterministic mock data instead of making API calls.

## Usage

### Initialize Database

```bash
python3 code/cli.py --init --db data/bxs.sqlite
```

### Backfill from CSV

```bash
python3 code/cli.py --csv data/sample_data/example_data_bxs.csv --db data/bxs.sqlite
```

### Run Data Pipeline

```bash
# Set MOCK_MODE=true if APIs unavailable
export MOCK_MODE=true
python3 code/data_pipeline.py --db data/bxs.sqlite
```

### Compute Metrics

```bash
python3 code/cli.py --compute --db data/bxs.sqlite
```

### Start API Server

```bash
uvicorn code.app.main:app --reload --host 0.0.0.0 --port 8000
```

### Test Endpoints

```bash
# Get latest metrics
curl http://127.0.0.1:8000/metrics/latest

# Get metrics in range
curl "http://127.0.0.1:8000/metrics/range?start=1709251200&end=1709251300"

# Get recent alerts
curl http://127.0.0.1:8000/alerts/recent
```

## Troubleshooting

### RPC Connection Errors

- Verify Bitcoin Core is running: `bitcoin-cli -rpcuser=... -rpcpassword=... getblockchaininfo`
- Check firewall settings
- Ensure RPC credentials match `.env` file

### Mempool.space Errors

- Verify mempool service is running in Start9
- Check if `https://mempool.local` resolves (may need `/etc/hosts` entry)
- Use `MOCK_MODE=true` for development without local mempool

### Database Issues

- Ensure `data/` directory exists and is writable
- Check SQLite file permissions
- Reinitialize with `--init` flag if schema is missing

## Security Notes

- Never commit `.env` file (it's in `.gitignore`)
- Use strong RPC passwords
- Keep `ADMIN_ENABLED=false` in production unless needed
- Restrict API access with firewall rules if exposing to network

