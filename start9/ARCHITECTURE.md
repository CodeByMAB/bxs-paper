# Bitcoin Seconds (BXS) - Start9 Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Start9 Environment                           │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │              Bitcoin Seconds Container (bxs:0.1.0)           │   │
│  │                                                               │   │
│  │  ┌────────────────────────────────────────────────────┐     │   │
│  │  │            FastAPI Web Server                       │     │   │
│  │  │            Port: 8080                               │     │   │
│  │  │  ┌──────────────────────────────────────────┐     │     │   │
│  │  │  │  Endpoints:                               │     │     │   │
│  │  │  │  • GET /healthz                          │     │     │   │
│  │  │  │  • GET /metrics/latest                   │     │     │   │
│  │  │  │  • GET /metrics/range                    │     │     │   │
│  │  │  │  • GET /alerts/recent                    │     │     │   │
│  │  │  │  • GET /docs (Swagger UI)                │     │     │   │
│  │  │  └──────────────────────────────────────────┘     │     │   │
│  │  └────────────────────────────────────────────────────┘     │   │
│  │                          ▲                                   │   │
│  │                          │                                   │   │
│  │                          │ queries                           │   │
│  │                          │                                   │   │
│  │  ┌────────────────────────────────────────────────────┐     │   │
│  │  │         Data Pipeline Runner (Background)          │     │   │
│  │  │         Interval: 600s (configurable)             │     │   │
│  │  │  ┌──────────────────────────────────────────┐     │     │   │
│  │  │  │  1. Fetch blockchain data (or mock)      │     │     │   │
│  │  │  │  2. Compute BXS metrics (f, S, BXS)     │     │     │   │
│  │  │  │  3. Check alert conditions               │     │     │   │
│  │  │  │  4. Store to database                    │     │     │   │
│  │  │  └──────────────────────────────────────────┘     │     │   │
│  │  └────────────────────────────────────────────────────┘     │   │
│  │                          │                                   │   │
│  │                          │ writes                            │   │
│  │                          ▼                                   │   │
│  │  ┌────────────────────────────────────────────────────┐     │   │
│  │  │            SQLite Database                         │     │   │
│  │  │            /app/data/bxs.sqlite                   │     │   │
│  │  │  ┌──────────────────────────────────────────┐     │     │   │
│  │  │  │  Tables:                                  │     │     │   │
│  │  │  │  • metrics (historical data)             │     │     │   │
│  │  │  │  • alerts (alert history)                │     │     │   │
│  │  │  │  • config (runtime settings)             │     │     │   │
│  │  │  └──────────────────────────────────────────┘     │     │   │
│  │  └────────────────────────────────────────────────────┘     │   │
│  │                                                               │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                   Persistent Volume                          │   │
│  │                   /app/data (mounted)                       │   │
│  │  • Database file (bxs.sqlite)                               │   │
│  │  • Backed up by Start9                                      │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                   Network Interfaces                         │   │
│  │                                                               │   │
│  │  LAN:  https://bitcoin-seconds.local:443 → 8080            │   │
│  │  Tor:  http://[onion].onion:80 → 8080                      │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                       │
└───────────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. FastAPI Web Server

**Purpose**: REST API for querying BXS metrics

**Technology**: 
- FastAPI (Python web framework)
- Uvicorn (ASGI server)
- Pydantic (data validation)

**Endpoints**:
- `GET /healthz` - Health check (returns 200 if healthy)
- `GET /metrics/latest` - Latest computed metrics
- `GET /metrics/range` - Historical data in time range
- `GET /alerts/recent` - Recent alert history
- `GET /docs` - Interactive API documentation

**Port**: 8080 (internal), proxied via Start9

### 2. Data Pipeline Runner

**Purpose**: Periodic data collection and metric computation

**Process**:
1. **Data Collection**
   - Mock mode: Generate synthetic data
   - Real mode: Query Bitcoin Core RPC + mempool.space API
   
2. **Metric Computation**
   - Calculate coin age `A(t)` [s]
   - Determine income/spend rates `i(t)`, `μ(t)` [sats/s]
   - Compute SSR (Surplus-to-Spending Ratio)
   - Calculate flow `f(t)` [sats/s], stock `S(t)` [sats], persistence `BXS(t)` [sats·s]

3. **Alert Evaluation**
   - Compare current flow to historical baseline
   - Trigger alerts on significant drops
   - Store alert events

4. **Data Storage**
   - Insert metrics into SQLite
   - Maintain historical time series

**Interval**: Configurable (default: 600 seconds / 10 minutes)

**Run Mode**: Background process, runs continuously

### 3. SQLite Database

**Purpose**: Persistent storage for all historical data

**Location**: `/app/data/bxs.sqlite` (in persistent volume)

**Schema**:

```sql
-- Historical metrics
CREATE TABLE metrics (
    timestamp INTEGER PRIMARY KEY,
    balance_sats INTEGER,
    coin_age_seconds INTEGER,
    flow_rate REAL,
    cumulative_stock INTEGER,
    bxs_persistence INTEGER,
    ssr REAL
);

-- Alert history
CREATE TABLE alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp INTEGER,
    alert_type TEXT,
    message TEXT,
    severity TEXT,
    metadata TEXT
);

-- Runtime configuration
CREATE TABLE config (
    key TEXT PRIMARY KEY,
    value TEXT,
    updated_at INTEGER
);
```

**Backup**: Included in Start9's automatic backup system

## Data Flow

### Typical Operation Cycle

```
1. Pipeline Wake Up (every 10 minutes)
        ↓
2. Fetch Data
   ├─ Mock Mode: Generate synthetic UTXO data
   └─ Real Mode: Query Bitcoin Core + mempool.space
        ↓
3. Compute Metrics
   ├─ Calculate A(t) (coin age) [s]
   ├─ Calculate I(t) (expansion rate) [s⁻¹]
   ├─ Calculate SSR(t) (surplus-to-spending ratio)
   ├─ Compute f(t) = i(t) × (A(t)/A₀) × (I(t)/I₀) × SSR(t) [sats/s]
   ├─ Update S(t) = ∫f(t)dt [sats]
   └─ Update BXS(t) = ∫S(t)dt [sats·s]
        ↓
4. Check Alerts
   ├─ Compare f(t) to baseline
   ├─ Detect drops > threshold
   └─ Generate alert if triggered
        ↓
5. Store to Database
   ├─ INSERT INTO metrics
   └─ INSERT INTO alerts (if any)
        ↓
6. Sleep until next interval
```

### API Request Flow

```
Client Request
    ↓
Start9 Proxy (LAN/Tor)
    ↓
FastAPI Server (port 8080)
    ↓
SQLite Query
    ↓
Format Response (JSON)
    ↓
Return to Client
```

## Configuration System

### Configuration Sources

1. **Start9 UI**
   - User edits in web interface
   - Calls `set-config.sh`
   - Updates `/app/.env`

2. **Environment Variables**
   - Loaded from `/app/.env`
   - Available to all processes
   - Persist across restarts

3. **Runtime Properties**
   - Read via `properties.sh`
   - Displayed in Start9 UI
   - Includes computed values

### Configuration Flow

```
Start9 UI (User Input)
    ↓
set-config.sh (validation)
    ↓
/app/.env (file write)
    ↓
Container Restart (if needed)
    ↓
Environment Variables (loaded)
    ↓
Application Config (applied)
```

## Health Check System

### Health Check Process

```
Start9 Scheduler (every 30s)
    ↓
check-web.sh (runs in container)
    ↓
HTTP GET localhost:8080/healthz
    ↓
API Health Check Handler
    ├─ Check database connection
    ├─ Check pipeline status
    └─ Verify last update time
    ↓
Return JSON Status
    ↓
Start9 UI (display green/red)
```

### Health Criteria

- ✅ **Healthy**: API responds with 200, database accessible
- ⚠️ **Degraded**: API responds but stale data (>30 min old)
- ❌ **Unhealthy**: API not responding or database error

## Network Architecture

### LAN Access

```
Client (https://bitcoin-seconds.local:443)
    ↓
Start9 Reverse Proxy (nginx)
    ├─ SSL termination
    ├─ Authentication (if enabled)
    └─ Forward to container:8080
    ↓
BXS API Server
```

### Tor Access

```
Client (http://[onion].onion:80)
    ↓
Tor Hidden Service
    ↓
Start9 Tor Proxy
    └─ Forward to container:8080
    ↓
BXS API Server
```

## Security Layers

### 1. Container Isolation
- Runs in separate Docker container
- Limited system access
- Controlled resource allocation

### 2. Network Segmentation
- No direct external network access (mock mode)
- Only local container network in real mode
- All external access via Start9 proxy

### 3. Data Encryption
- Volume encrypted by Start9
- TLS for LAN access (Start9 handles)
- Tor encryption for .onion access

### 4. Access Control
- Start9 authentication required
- Optional API key (future)
- Rate limiting via Start9

## Performance Characteristics

### Resource Usage

**CPU**:
- Idle: <1% (waiting for next pipeline run)
- Active: 5-10% (during 10-second computation burst)
- Peak: 20% (initial database setup)

**Memory**:
- Base: 150 MB (Python + FastAPI)
- Working: 200 MB (during computation)
- Peak: 256 MB (with large queries)

**Disk**:
- Initial: 150 MB (Docker image + empty database)
- Growth: ~10 MB/year (depends on update frequency)
- Max: 500 MB (with several years of data)

**Network** (Real Mode):
- Per Update: <100 KB (RPC calls + API queries)
- Daily: <5 MB (at 10-minute intervals)
- Monthly: <150 MB

### Scalability

**Current Limits**:
- Single wallet support
- 10-minute minimum update interval
- ~10 years of data before optimization needed
- API rate limited by Start9

**Future Improvements**:
- Multi-wallet support
- Faster update intervals (1-5 minutes)
- Database partitioning for larger datasets
- Caching layer for frequent queries

## Deployment Topology

### Single-User (Current)

```
┌──────────────┐
│   Start9     │
│              │
│ ┌──────────┐ │
│ │   BXS    │ │
│ └──────────┘ │
│              │
└──────────────┘
```

### Multi-Node (Future)

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Start9 A   │     │   Start9 B   │     │   Start9 C   │
│              │     │              │     │              │
│ ┌──────────┐ │     │ ┌──────────┐ │     │ ┌──────────┐ │
│ │   BXS    │ │     │ │   BXS    │ │     │ │   BXS    │ │
│ └──────────┘ │     │ └──────────┘ │     │ └──────────┘ │
│              │     │              │     │              │
└──────────────┘     └──────────────┘     └──────────────┘
      ↓                     ↓                     ↓
      └─────────────────────┴─────────────────────┘
                            ↓
                   ┌────────────────┐
                   │ Aggregator API │
                   │   (optional)   │
                   └────────────────┘
```

## Maintenance & Operations

### Routine Operations

**Daily**:
- Automatic health checks (every 30s)
- Pipeline updates (every 10 min)
- Data persistence to disk

**Weekly**:
- Review alert history
- Check database size
- Verify no errors in logs

**Monthly**:
- Update service (if new version available)
- Review configuration settings
- Backup verification

### Troubleshooting Points

**If API Not Responding**:
1. Check container status: `docker ps`
2. Review logs: Start9 UI → Services → BXS → Logs
3. Verify port mapping: 8080 should be listening
4. Test health check: `curl localhost:8080/healthz`

**If No New Data**:
1. Check pipeline is running: Look for periodic log entries
2. Verify interval setting: Should see updates every 10 min
3. In real mode: Check Bitcoin Core connectivity
4. Check database write permissions

**If High Resource Usage**:
1. Increase pipeline interval (600s → 1800s)
2. Check for database locks
3. Review query patterns
4. Consider archiving old data

---

**Version**: 0.1.0  
**Last Updated**: November 6, 2025  
**Architecture Status**: Implemented and Tested ✅

