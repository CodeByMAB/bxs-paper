# Pre-Registration: Bitcoin-Seconds (BXS) Empirical Tests — v0.6.6

## Objectives
Test whether durability-adjusted flow f(t) predicts holding behavior and early liquidation better than balance-only or coin-age-only baselines.

## Hypotheses
- H1 (Durability): Higher f(t) at time τ predicts a higher probability of HOLD over [τ, τ+Δ], controlling for W(t).
- H2 (Early Warning): Large negative Δf(t) over a short window precedes liquidation events within L days.
- H3 (Component Value): Each driver (A, I, SSR) adds incremental predictive power in nested models.

## Outcome & Labels
- HOLD(τ; Δ, x): 1 if wallet retains ≥ (1−x)% of W(τ) after Δ days, else 0.
  - Primary: Δ = 90 days, x = 5%.
  - Robustness: Δ ∈ {60,120}, x ∈ {3%, 10%}.

## Features (computed at τ)
- W(τ): balance (sats)
- A(τ): value-weighted coin age (s)
- I(τ): mechanical protocol expansion rate (s⁻¹)
- SSR(τ): [s(τ)+r·i(τ)−CP(τ)] / [max{τ−τ₀, t_min} · max{μ(τ), μ_min}]
- f(τ): i(τ) · (A/A₀) · (I/I₀) · SSR(τ)

Baselines: A₀, I₀ fixed 180-day medians; t_min = 30 d; μ_min = 1 sat/s.

## Model Specs (fixed)
- M1: HOLD ~ W
- M2: HOLD ~ W + A
- M3: HOLD ~ W + A + I
- M4: HOLD ~ W + A + I + SSR
- M5: HOLD ~ f

## Estimation & Metrics
- Classification: Logistic regression; Report AUC, Brier, accuracy.
- Survival (H1): Cox model on time-to-sell; log-rank across f(t) quartiles.
- Early warning (H2): Rule: flag if f drops ≥20% over 14 days; report TPR/FPR, lead time.
- Nested comparisons (H3): Likelihood ratio tests; AICc, ΔAICc; out-of-sample AUC.

## Splits & CV
- Rolling origin CV with 70/30 expanding window; final hold-out = last 20% of timeline.
- No target leakage: features only from τ.

## Significance Thresholds
- p < 0.05 (LR tests); ΔAICc > 10 = strong evidence; AUC improvement ≥ 0.05 = meaningful.

## Freeze Notice
This plan is locked prior to viewing test outcomes. Any deviations will be addended and time-stamped.

# Pre-Registration — Bitcoin-Seconds (BXS) v0.6.6 Durability Tests

**Version:** v0.6.6  
**Date (UTC):** 2025-11-04T00:00:00Z  
**Paper PDF:** ./paper/Bitcoin_Seconds_v0_6_6.pdf  
**Repo Tag/Commit:** v0.6.6  
**Scope:** Empirical validation of f(t), S(T), BXS(T) for durability prediction

---

## Outcomes (Pre-Registered)
For entity *j* at time *t*:
- Define **HOLD** over horizon Δ with threshold *x*:
  
  \[
  HOLD_{j,t} = 
  \begin{cases}
  1 & \text{if net outflows over } [t, t+Δ] \le x \cdot W_j(t) \\
  0 & \text{otherwise}
  \end{cases}
  \]

- Default: **Δ = 90 days**, **x = 5%** (we will run sensitivity checks).

## Features & Construction
- From wallet RPC / UTXO history: **W(t), A(t), i(t), μ(t)**  
- From node telemetry: **I(t) = σ/S · λ** (block subsidy / supply × block rate)  
- Optional: **CP(t)** (cumulative CPI-weighted cost)
- **SSR(t)** = \[W + r·i − CP\] / (max{t, t_min} · max{μ, μ_min})
- **f(t)** = *i(t)* · (A/A₀) · (I/I₀) · SSR(t)  
- Floors: **t_min > 0**, **μ_min > 0**. Keep **SSR(t) < 0** (drawdown signal).
- Baselines: **A₀** = rolling 180d median of A(t); **I₀** = per-epoch rolling median of I(t).

## Models (Non-Nested)
- **CM (Components Model):** HOLD ~ W + A + I + SSR  
- **SM (Scalar Model):** HOLD ~ f(t)  
- **ENS (Ensemble):** ½·(p_CM + p_SM)

> We intentionally avoid a model containing both f(t) and its components to prevent multicollinearity.

## Evaluation Plan
- **CV:** Rolling-origin cross-validation (time-series aware)
- **Primary metrics:** Out-of-sample AUC, Brier score
- **Comparisons:** CM vs SM via Diebold–Mariano tests and AICc on common validation windows
- **Calibration:** Reliability plots; survival curves by f(t) quartiles
- **Early warning (H2):** Flag when Δf(t) ≤ −20% over 14d; evaluate TPR/FPR and mean lead time to liquidation (≤30d)

## Hypotheses
- **H1 (Durability):** SM outperforms W-only baseline by ≥ 0.05 AUC
- **H2 (Stress):** Δf ≤ −20%/14d predicts liquidations within 30d (TPR > 60%, FPR < 30%, mean lead > 14d)
- **H3 (Component Value):** ENS outperforms CM and SM on AUC/Brier with statistically significant gains

## Robustness & Sensitivity
- Holding windows: Δ ∈ {60, 120, 180}, thresholds x ∈ {2%, 10%}
- Baselines: A₀, I₀ windows ∈ {90, 180, 360} days; per-epoch I₀
- Regimes: post-halving, bull/bear/sideways
- SSR guardrails: report capped vs uncapped
- Data hygiene: address clustering / self-churn handling for A(t), i(t), μ(t)

## Implementation Notes (Node-Local)
- Compute I(t) each block via Start9-hosted mempool.space (σ, S, λ)
- Derive W, A, i, μ from wallet RPC/UTXO history; persist to SQLite
- Expose f(t), S(T), BXS(T); alert when Δf(t) ≤ −20% over 14d
- Mark new wallets as “warming up” until A₀/I₀ baselines stabilize

---

**Sign-off:**  
Prepared by: CodeByMAB
Timestamp (UTC): 2025-11-04T09:22:00 UTC  

