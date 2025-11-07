# Bitcoin Seconds (BXS) - Start9 Package

This directory contains all the files needed to build and deploy Bitcoin Seconds as a Start9 service.

## 📦 Package Contents

```
start9/
├── manifest.yaml           # Service manifest (metadata, config, dependencies)
├── instructions.md         # User-facing documentation
├── icon.png               # Service icon (512x512)
├── LICENSE                # CC BY 4.0 license
├── build.sh              # Build script to create the package
├── docker-compose.yml    # Service composition
├── properties.sh         # Runtime properties display
├── set-config.sh         # Configuration setter
├── check-web.sh          # Health check script
├── config_spec.yaml      # Configuration specification (legacy)
└── README.md             # This file
```

## 🚀 Quick Start

### Build the Package

```bash
# From the repository root
./start9/build.sh
```

This will:
1. Build the Docker image
2. Save it as a compressed tarball
3. Verify all required files are present
4. Show next steps

### Package for Start9

```bash
# Install start-sdk (one time)
npm install -g @start9labs/start-sdk

# Create the .s9pk package
start-sdk pack

# This creates: bitcoin-seconds.s9pk
```

### Install on Start9

1. Open your Start9 web interface
2. Navigate to **System** → **Sideload Service**
3. Upload the `bitcoin-seconds.s9pk` file
4. Click **Install**
5. Configure the service settings
6. Click **Start**

## ⚙️ Configuration

### Mock Mode (Default: ON)

When enabled, uses synthetic data for testing without requiring a Bitcoin node. Perfect for:
- Initial testing
- Development
- Learning BXS concepts

To use real Bitcoin data:
1. Disable mock mode
2. Ensure Bitcoin Core is installed and synced
3. Ensure mempool.space service is running

### Alert Settings

- **Alert Drop %**: Trigger when flow drops by this amount (default: 20%)
- **Alert Window**: Days to monitor for changes (default: 14)

### Advanced Settings

- **t_min**: Floor for elapsed time (default: 1000 seconds)
- **mu_min**: Floor for spend rate (default: 0.000001 sats/s)
- **Pipeline Interval**: Update frequency (default: 600 seconds)

## 📡 API Endpoints

Once running, access via:
- **LAN**: `https://bitcoin-seconds.local`
- **Tor**: Address shown in Start9 interface

### Available Endpoints

```bash
# Health check
GET /healthz

# Latest metrics
GET /metrics/latest

# Time range query
GET /metrics/range?start=<timestamp>&end=<timestamp>

# Recent alerts
GET /alerts/recent?limit=10
```

## 🔧 Development & Testing

### Test Locally (without Start9)

```bash
# Start with docker-compose
docker-compose -f start9/docker-compose.yml up

# Test the API
curl http://localhost:8080/healthz
curl http://localhost:8080/metrics/latest
```

### View Logs

```bash
# Via docker-compose
docker-compose -f start9/docker-compose.yml logs -f

# On Start9
# Use the web interface: Services → Bitcoin Seconds → Logs
```

### Rebuild After Changes

```bash
# Rebuild Docker image
./start9/build.sh

# Repackage
embassy-sdk pack start9

# Upload new version to Start9
```

## 📊 What BXS Measures

Bitcoin Seconds computes three key metrics:

1. **Durability-Adjusted Flow** `f(t)` [sats/s]
   - Combines HODLing strength, protocol context, and financial runway
   - Positive = accumulating, Negative = depleting

2. **Cumulative Stock** `S(T)` [sats]
   - Total accumulated bitcoin claims over time
   - Integral of flow rate

3. **Persistence** `BXS(T)` [sats·s]
   - Time-weighted stock (like amp-hours for batteries)
   - Measures true wealth accumulation

### Formula

```
f(t) = i(t) × (A(t)/A₀) × (I(t)/I₀) × SSR(t)   [sats/s]
```

Where:
- `i(t)` = income inflow rate [sats/s]
- `A(t)/A₀` = revealed HODLing strength (coin age ratio)
- `I(t)/I₀` = protocol era context (expansion rate ratio)
- `SSR(t)` = Surplus-to-Spending Ratio (financial runway)

## 🗄️ Data Storage

All data is stored in the persistent volume:
- Location: `/app/data/bxs.sqlite`
- Backed up by Start9's backup system
- Contains historical metrics and alerts

## 🔒 Security & Privacy

- **Local Only**: All computation on your Start9 device
- **No External Calls**: Mock mode makes no network requests
- **Private**: Wallet data never leaves your device
- **Tor Ready**: Access via Tor for privacy

## 📚 Documentation

- **Main Repository**: https://github.com/CodeByMAB/bxs-paper
- **Whitepaper**: See `/src/` directory
- **Issues**: https://github.com/CodeByMAB/bxs-paper/issues
- **Start9 Docs**: https://docs.start9.com

## 🐛 Troubleshooting

### Build Fails

- Ensure Docker is installed and running
- Check Docker has internet access to pull base images
- Verify sufficient disk space

### Service Won't Start on Start9

- Check service logs in Start9 interface
- Verify configuration settings
- Try enabling mock mode first

### API Not Responding

- Check service is running (green status)
- Verify port 8080 is accessible
- Test health endpoint: `curl http://bitcoin-seconds.embassy:8080/healthz`

### No Data in Metrics

- In mock mode: Check logs for errors
- In real mode: Verify Bitcoin Core is synced and accessible
- Wait for first pipeline run (default: 10 minutes)

## 📝 Version History

### v0.1.0 (Initial Release)
- Core BXS calculations
- REST API with 4 endpoints
- Mock mode for testing
- SQLite persistence
- Configurable alerts
- Full Start9 integration

## 🤝 Contributing

This is part of the Bitcoin Seconds research project. Contributions welcome!

1. Fork the main repository
2. Create a feature branch
3. Test thoroughly (including Start9 deployment)
4. Submit a pull request

## 📄 License

Licensed under CC BY 4.0 (Creative Commons Attribution 4.0 International)

You are free to:
- **Share** — copy and redistribute
- **Adapt** — remix, transform, and build upon the material

Under the terms:
- **Attribution** — You must give appropriate credit

See LICENSE file for full text.

---

**Bitcoin Seconds** v0.1.0  
Measuring durable accumulation of time-shifted energy claims in Bitcoin
