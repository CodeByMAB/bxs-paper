#!/usr/bin/env python3
"""
Bitcoin-Seconds (BXS) Calculator

Functions to compute SSR(t), f(t), and integrate S(T) and BXS(T).
Implements formulas from BXS whitepaper v0.6.7.

Paper notation:
- W(t): balance/holdings [sats]
- A(t): value-weighted coin age [s]
- I(t): protocol expansion rate [s⁻¹]
- i(t): income inflow [sats/s]
- μ(t): spending outflow [sats/s]
- SSR(t): Surplus-to-Spending Ratio
- f(t): durability-adjusted flow [sats/s] (eq:flow)
- S(T): cumulative stock [sats] (eq:stock)
- BXS(T): time-weighted persistence [sats·s] (eq:bxs)
"""
import numpy as np
from typing import List, Union


def compute_ssr(
    W: float,
    i: float,
    mu: float,
    CP: float,
    t: float,
    r: float,
    t_min: float = 1_000.0,
    mu_min: float = 1e-6,
) -> float:
    """
    Compute Surplus-to-Spending Ratio (SSR).
    
    Paper formula (Section 3):
    SSR(t) = (s(t) + r·i(t) - CP(t)) / (max{t, t_min} · max{μ(t), μ_min})

    Args:
        W: Current holdings s(t) [sats]
        i: Income inflow rate i(t) [sats/s]
        mu: Spending outflow rate μ(t) [sats/s]
        CP: Cumulative inflation-adjusted cost CP(t) [sats], optional
        t: Elapsed time [s]
        r: Retirement (forward) horizon [s]
        t_min: Floor for elapsed time [s]
        mu_min: Floor for spending rate [sats/s]

    Returns:
        SSR(t): Surplus-to-spending ratio [dimensionless, can be <0]
    """
    t_safe = max(t, t_min)
    mu_safe = max(mu, mu_min)
    numerator = W + r * i - CP
    return numerator / (t_safe * mu_safe)  # keep negatives


def compute_f(
    i: float,
    A: float,
    A0: float,
    I: float,  # noqa: E741 - protocol expansion rate (standard notation)
    I0: float,
    SSR: float,
) -> float:
    """
    Compute durability-adjusted flow of durable claims f(t).
    
    Paper formula (eq:flow, Section 4):
    f(t) = i(t) × (A(t)/A₀) × (I(t)/I₀) × SSR(t)

    Args:
        i: Income inflow rate i(t) [sats/s]
        A: Value-weighted coin age A(t) [s]
        A0: Coin-age baseline A₀ [s]
        I: Protocol expansion rate I(t) [s⁻¹]
        I0: Expansion-rate baseline I₀ [s⁻¹]
        SSR: Surplus-to-spending ratio SSR(t) [dimensionless]

    Returns:
        f(t): Durability-adjusted flow [sats/s]
    """
    A0 = max(A0, 1e-9)
    I0 = max(I0, 1e-12)
    return i * (A / A0) * (I / I0) * SSR


def integrate_cumulative(
    series: Union[List[float], np.ndarray],
    dt: float,
) -> List[float]:
    """
    Integrate cumulative series using trapezoidal rule.

    Args:
        series: Array of values
        dt: Time step [s]

    Returns:
        Cumulative integral (same length as input)
    """
    series = np.asarray(series)
    out = []
    acc = 0.0
    prev = series[0]
    out.append(0.0)
    for x in series[1:]:
        acc += (x + prev) * 0.5 * dt
        out.append(acc)
        prev = x
    return out


def integrate_s(
    f_timeseries: Union[List[float], np.ndarray],
    timestamps: Union[List[int], np.ndarray],
) -> List[float]:
    """
    Integrate cumulative durable claims S(T) = ∫₀ᵀ f(t) dt.
    
    Paper formula (eq:stock, Section 5):
    S(T) = ∫₀ᵀ f(t) dt

    Uses trapezoidal rule for numerical integration.

    Args:
        f_timeseries: Array of f(t) values [sats/s]
        timestamps: Array of timestamps [unix seconds]

    Returns:
        S(T): Cumulative durable claims [sats] (same length as input)
    """
    timestamps = np.asarray(timestamps, dtype=float)
    dt_series = np.diff(timestamps)
    if len(dt_series) == 0:
        return [0.0]
    # Use first dt for initial step, then variable dt
    dt = dt_series[0] if len(dt_series) > 0 else 600.0
    return integrate_cumulative(f_timeseries, dt)


def integrate_bxs(
    S_timeseries: Union[List[float], np.ndarray],
    timestamps: Union[List[int], np.ndarray],
) -> List[float]:
    """
    Integrate Bitcoin-Seconds BXS(T) = ∫₀ᵀ S(t) dt.
    
    Paper formula (eq:bxs, Section 5):
    BXS(T) = ∫₀ᵀ S(t) dt = ∫₀ᵀ ∫₀ᵗ f(τ) dτ dt

    Uses trapezoidal rule for numerical integration.

    Args:
        S_timeseries: Array of S(t) values [sats]
        timestamps: Array of timestamps [unix seconds]

    Returns:
        BXS(T): Bitcoin-Seconds [sats·s] (same length as input)
    """
    timestamps = np.asarray(timestamps, dtype=float)
    dt_series = np.diff(timestamps)
    if len(dt_series) == 0:
        return [0.0]
    dt = dt_series[0] if len(dt_series) > 0 else 600.0
    return integrate_cumulative(S_timeseries, dt)


def compute_baseline_bxscore(
    W_timeseries: Union[List[float], np.ndarray],
    timestamps: Union[List[int], np.ndarray],
) -> List[float]:
    """
    Compute baseline BXScore (size-only persistence).

    Paper formula (eq:bxs_core, Section 5):
    BXS_core(T) = ∫₀ᵀ W(t) dt
    
    This is the baseline comparator that omits durability adjustments.

    Args:
        W_timeseries: Array of W(t) wealth/balance values [sats]
        timestamps: Array of timestamps [unix seconds]

    Returns:
        BXS_core(T): Baseline time-weighted wealth [sats·s] (same length as input)
    """
    return integrate_bxs(W_timeseries, timestamps)
