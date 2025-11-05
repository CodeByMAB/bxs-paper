#!/usr/bin/env python3
"""Tests for bxs_calculator module."""
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from code.bxs_calculator import compute_ssr, compute_f, integrate_s, integrate_bxs


def test_compute_ssr():
    """Test SSR computation with floors."""
    # Normal case
    ssr = compute_ssr(W=12_000_000, i=4700, mu=3800, CP=2_500_000, t=2_592_000, r=6.3072e8)
    assert isinstance(ssr, float)
    assert ssr > 0  # Should be positive with these inputs
    
    # Test floor on t
    ssr_small_t = compute_ssr(W=12_000_000, i=4700, mu=3800, CP=2_500_000, t=100, r=6.3072e8, t_min=1_000)
    assert ssr_small_t > 0  # Should use t_min
    
    # Test floor on mu
    ssr_small_mu = compute_ssr(W=12_000_000, i=4700, mu=1e-10, CP=2_500_000, t=2_592_000, r=6.3072e8, mu_min=1e-6)
    assert ssr_small_mu > 0  # Should use mu_min
    
    # Negative SSR (drawdown) - CP exceeds W + r*i
    # W + r*i = 1_000_000 + 6.3072e8 * 100 ≈ 63_073_000_000
    ssr_neg = compute_ssr(W=1_000_000, i=100, mu=5000, CP=70_000_000_000, t=2_592_000, r=6.3072e8)
    assert ssr_neg < 0  # Should be negative


def test_compute_f():
    """Test f(t) computation."""
    f = compute_f(i=4700, A=18_000_000, A0=1.55e7, I=2.61e-10, I0=2.61e-10, SSR=1.5)
    assert isinstance(f, float)
    assert f > 0
    
    # Test with zero baseline (should use floor)
    f_zero_a0 = compute_f(i=4700, A=18_000_000, A0=0, I=2.61e-10, I0=2.61e-10, SSR=1.5)
    assert f_zero_a0 > 0


def test_integrate_s():
    """Test S integration."""
    f_series = [100.0, 110.0, 120.0, 130.0]
    timestamps = [1000, 1600, 2200, 2800]  # 600s intervals
    
    S_series = integrate_s(f_series, timestamps)
    assert len(S_series) == len(f_series)
    assert S_series[0] == 0.0  # First should be 0
    assert S_series[-1] > 0  # Cumulative should be positive


def test_integrate_bxs():
    """Test BXS integration."""
    S_series = [1000.0, 2000.0, 3000.0, 4000.0]
    timestamps = [1000, 1600, 2200, 2800]  # 600s intervals
    
    BXS_series = integrate_bxs(S_series, timestamps)
    assert len(BXS_series) == len(S_series)
    assert BXS_series[0] == 0.0  # First should be 0
    assert BXS_series[-1] > 0  # Cumulative should be positive


def test_integrate_empty():
    """Test integration with empty/single element."""
    S_single = integrate_s([100.0], [1000])
    assert len(S_single) == 1
    assert S_single[0] == 0.0


def test_integration_chain():
    """Test integration chain: f -> S -> BXS."""
    f_series = [100.0, 110.0, 120.0]
    timestamps = [1000, 1600, 2200]
    
    S_series = integrate_s(f_series, timestamps)
    BXS_series = integrate_bxs(S_series, timestamps)
    
    assert len(S_series) == len(f_series)
    assert len(BXS_series) == len(S_series)
    assert all(s >= 0 for s in S_series)
    assert all(bxs >= 0 for bxs in BXS_series)

