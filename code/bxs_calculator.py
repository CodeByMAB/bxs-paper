#!/usr/bin/env python3
"""
Bitcoin-Seconds (BXS) Calculator

Functions to compute SSR, f(t), and integrate S(T) and BXS(T).
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

    Args:
        W: Current holdings [sats]
        r: Retirement horizon [s]
        i: Income inflow rate [sats/s]
        CP: Cumulative CPI-weighted cost [sats], optional
        t: Elapsed time [s]
        t_min: Floor for elapsed time [s]
        mu: Spending outflow rate [sats/s]
        mu_min: Floor for spending rate [sats/s]

    Returns:
        SSR: Surplus-to-spending ratio [dimensionless, can be <0]
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
    Compute productive flow of durable claims f(t).

    Args:
        i: Income inflow rate [sats/s]
        A: Value-weighted coin age [s]
        A0: Coin-age baseline [s]
        I: Protocol expansion rate [s⁻¹]
        I0: Expansion-rate baseline [s⁻¹]
        SSR: Surplus-to-spending ratio [dimensionless]

    Returns:
        f: Productive flow [sats/s]
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

    Uses trapezoidal rule for numerical integration.

    Args:
        f_timeseries: Array of f(t) values [sats/s]
        timestamps: Array of timestamps [unix seconds]

    Returns:
        S: Cumulative claims [sats] (same length as input)
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

    Uses trapezoidal rule for numerical integration.

    Args:
        S_timeseries: Array of S(t) values [sats]
        timestamps: Array of timestamps [unix seconds]

    Returns:
        BXS: Bitcoin-Seconds [sats·s] (same length as input)
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

    BXScore(T) = ∫₀ᵀ W(t) dt

    Args:
        W_timeseries: Array of wealth/balance values [sats]
        timestamps: Array of timestamps [unix seconds]

    Returns:
        BXScore: Baseline time-weighted wealth [sats·s] (same length as input)
    """
    return integrate_bxs(W_timeseries, timestamps)
