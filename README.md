# Bitcoin-Seconds (BXS)
![CI](https://github.com/CodeByMAB/bxs-paper/actions/workflows/ci.yml/badge.svg)
![LaTeX](https://github.com/CodeByMAB/bxs-paper/actions/workflows/latex.yml/badge.svg)

**Version:** v0.6.6 (theory) • **Status:** Framework finalized, empirical testing in progress

Bitcoin-Seconds (BXS) measures the **durable accumulation of time-shifted energy claims** in a Bitcoin-denominated economy.

- **Flow (rate):** \( f(t) \) — durability-adjusted Bitcoin flow [sats/s]  
- **Stock (cumulative):** \( S(T)=\int_0^T f(t)\,dt \) — accumulated claims [sats]  
- **Persistence (time-weighted):** \( \mathrm{BXS}(T)=\int_0^T S(t)\,dt \) — Bitcoin-Seconds [sats·s]

**Durability drivers** (multiplicative):
1) **HODLing strength:** \( A(t)/A_0 \) (value-weighted coin-age vs. baseline)  
2) **Protocol era context:** \( I(t)/I_0 \) (mechanical expansion rate)  
3) **Financial runway:** \( \mathrm{SSR}(t)=\dfrac{s(t)+r\,i(t)-CP(t)}{\max\{t,t_{\min}\}\,\max\{\mu(t),\mu_{\min}\}} \)

> Baseline “core persistence” comparator: \( \mathrm{BXScore}(T)=\int_0^T W(t)\,dt \) (size-only).

---

## Repository Layout

```
/src/                            # LaTeX source (paper v0.6.6)
/build/                          # Compiled PDFs
/tools/                          # (optional) scripts, notebooks
main.py                          # CLI (legacy BS index — see below)
example_data_legacy.csv          # CSV for legacy CLI
example_data_bxs.csv             # CSV schema for durability flow (future CLI)
README.md                        # This file
preregister.md                   # Analysis plan (pre-registered)
```

---

## Quick Start (legacy CLI)

> The current `main.py` implements the earlier **BS index** (discounted utility ÷ discounted spend). It’s useful for reproducing v0.3-series results. The durability-flow CLI for v0.6.6 is planned; schema below so you can extend safely.

### Install
```bash
python3 -m venv venv && . venv/bin/activate
pip install -U pip pandas numpy
chmod +x main.py
```

### Run (example: annual discount rate = 5%)
```bash
./main.py --input example_data_legacy.csv --rho-per-year 0.05 --alpha 1 --beta 1 --gamma 1
```

### Legacy CSV Columns (for `main.py`)
- `timestamp` — ISO8601 (e.g., `2025-01-01T00:00:00Z`) or Unix seconds
- `A` — expected (value-weighted) coin age **[seconds]**
- `Y` — income rate **[sats/s]**
- `R` — retirement income rate **[sats/s]**
- `c` — spend rate **[sats/s]**
- `iota` — real inflation rate **[s⁻¹]**

**Output (JSON to stdout + `bs_report.json`):**
- `U_discounted` — discounted utility (BXS units)
- `S_discounted` — discounted spend (BTC units)
- `BS_index` — dimensionless ratio

---

## Durability Flow (v0.6.6) — Theory & Data Schema

**Flow (current spec):**
\[
f(t) \;=\; i(t)\;\Big(\tfrac{A(t)}{A_0}\Big)\;\Big(\tfrac{I(t)}{I_0}\Big)\;\mathrm{SSR}(t),
\qquad
\mathrm{SSR}(t)=\frac{s(t) + r\,i(t) - CP(t)}{\max\{t,t_{\min}\}\cdot \max\{\mu(t),\mu_{\min}\}}
\]

**Integrals:**
\[
S(T)=\int_0^T f(t)\,dt, \qquad
\mathrm{BXS}(T)=\int_0^T S(t)\,dt
\]

### CSV Schema (for a future CLI that computes \(f,S,\mathrm{BXS}\))
`example_data_bxs.csv` (per timestamp or per block):
- `timestamp` — ISO8601 or Unix seconds  
- `W` — balance, **[sats]**  
- `A` — value-weighted coin age, **[s]**  
- `I` — mechanical expansion rate, **[s⁻¹]** (see “Provenance”)  
- `i` — income rate, **[sats/s]** (rolling avg recommended)  
- `mu` — spend rate, **[sats/s]** (rolling avg recommended)  
- `CP` — cumulative CPI-weighted spend, **[sats]**  
- `r` — retirement horizon, **[s]**  
- `A0` — coin-age baseline, **[s]** (e.g., 180-day median)  
- `I0` — expansion baseline, **[s⁻¹]** (e.g., 180-day median)  
- `tmin` — floor for elapsed time, **[s]** (e.g., 30 days)  
- `mumin` — floor for spend rate, **[sats/s]** (e.g., 1 sat/s)

**Recommended smoothing:** 7–30 day rolling medians for `i` and `mu`.

---

## Data Provenance (node-local, reproducible)

- **Compute \(I(t)\)** mechanically via your node:
  \[
  I(t) \;=\; \frac{\sigma(h(t))}{S(t)}\cdot \lambda(t)
  \]
  where \(\sigma\) = block subsidy [BTC/block], \(S\)=circulating supply [BTC], \(\lambda\)=block arrival rate [blocks/s].

- **Start9 + mempool.space (local):**
  - Query subsidy `σ(h)`, supply `S`, and block timestamps → `λ`.
  - Wallet RPC for UTXOs → `W` and value-weighted `A`.
  - Derive rolling `i` (inflows) and `μ` (outflows) from txs.
  - Maintain a small SQLite for time series and integration.

---

## Pre-Registration (credibility)

This repo includes `preregister.md` locking:
- **Models:** M1…M5 (nested), including the full \(f(t)\) spec  
- **Metrics:** AUC, Brier, LR tests, AICc, survival curves  
- **Splits:** rolling-origin CV; fixed hold-out  
- **Outcomes:** HOLD(Δ=90d, x=5%), with robustness checks

Host on OSF/AsPredicted and/or commit hash + signed tag here.

---

## Reproducibility & Integrity

- Tag releases (e.g., `v0.6.6`) and attach built PDFs.  
- Record checksums:
  ```bash
  shasum -a 256 build/Bitcoin_Seconds_v0_6_6.pdf > SHA256SUMS.txt
  ```
- (Optional) Bitcoin-anchor with OpenTimestamps:
  ```bash
  ots stamp build/Bitcoin_Seconds_v0_6_6.pdf
  ```
- (Optional) Enable Zenodo for a DOI on each GitHub release.

---

## Evaluate (empirical plan)
- Labels: `HOLD` with Δ=90 days and x=5% net outflow threshold.
- Models (non-nested): CM = `HOLD ~ W + A + I + SSR`, SM = `HOLD ~ f(t)`, ENS = avg(CM,SM).
- Metrics: out-of-sample AUC, Brier; Diebold–Mariano and AICc for CM vs SM; calibration curves.
- Robustness: vary (Δ,x), baselines (A0,I0), regimes (post-halvings, bull/bear), SSR caps vs uncapped.

---

## Roadmap

- [ ] CLI: durability flow \(f,S,\mathrm{BXS}\) from `example_data_bxs.csv`  
- [ ] Start9 app: per-block compute + dashboard (W, f, SSR, BXS, alerts)  
- [ ] Empirical tests: H1→H3 (survival, ROC, LR/AICc) on wallet/cohort data  
- [ ] Preprint + replication package

---

## License
Add your preferred license (e.g., MIT/Apache-2.0).

## Citation
If you publish a preprint/DOI, add BibTeX here.
