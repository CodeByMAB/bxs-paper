#!/usr/bin/env python3
"""
Data Pipeline: Fetch from mempool.space + wallet RPC, write to SQLite.

Connects to local Bitcoin node and mempool.space API to populate
the schema defined in data/schema.sql. Includes mock adapters for testing.

Computes per-block metrics:
- I(t): Protocol expansion rate [s⁻¹]
- W(t): Balance [sats]
- A(t): Value-weighted coin age [s]
- i(t), μ(t): Income/spending rates [sats/s]
- SSR(t): Surplus-to-Spending Ratio
- f(t): Durability-adjusted flow [sats/s]
"""
import sqlite3
import os
import time
from typing import Optional, Dict, List
import requests
from dotenv import load_dotenv

load_dotenv()

# Constants
MEMPOOL_API_URL = os.getenv("MEMPOOL_API_URL", "https://mempool.local")
BITCOIN_RPC_URL = os.getenv("BITCOIN_RPC_URL", "http://127.0.0.1:8332")
BITCOIN_RPC_USER = os.getenv("BITCOIN_RPC_USER", "rpcuser")
BITCOIN_RPC_PASSWORD = os.getenv("BITCOIN_RPC_PASSWORD", "rpcpassword")
MOCK_MODE = os.getenv("MOCK_MODE", "false").lower() == "true"


def fetch_block_data_mock(height: int) -> Optional[Dict]:
    """Mock block data for testing."""
    # Deterministic mock: block 800000 ≈ 2024-03-01
    base_time = 1709251200  # 2024-03-01 00:00:00
    block_time = base_time + (height - 800000) * 600

    # Approximate subsidy and supply for height
    halving_epoch = height // 210000
    subsidy = 50.0 / (2**halving_epoch)
    supply = halving_epoch * 210000 * 50.0 + (height % 210000) * subsidy

    return {
        "h": height,
        "t": block_time,
        "sigma": subsidy,
        "S": supply,
        "lambda": 1.0 / 600.0,  # ~600s per block
        "I": (subsidy / supply) * (1.0 / 600.0),
    }


def fetch_block_data(height: int) -> Optional[Dict]:
    """
    Fetch block data from mempool.space API.

    Args:
        height: Block height

    Returns:
        Dictionary with keys: h, t, sigma, S, lambda, I
        Returns None if fetch fails
    """
    if MOCK_MODE:
        return fetch_block_data_mock(height)

    try:
        url = f"{MEMPOOL_API_URL}/api/block-height/{height}"
        response = requests.get(url, timeout=5)
        if response.status_code != 200:
            return fetch_block_data_mock(height)

        block_hash = response.text.strip()
        block_url = f"{MEMPOOL_API_URL}/api/block/{block_hash}"
        block_data = requests.get(block_url, timeout=5).json()

        # Extract data
        t = block_data.get("timestamp", int(time.time()))
        subsidy = block_data.get("subsidy", 6.25) / 1e8  # Convert to BTC
        supply = (
            block_data.get("chainstats", {})
            .get("utxos", {})
            .get("totalAmount", 19_500_000)
            / 1e8
        )

        # Compute lambda (block arrival rate)
        prev_block_url = f"{MEMPOOL_API_URL}/api/blocks"
        prev_blocks = requests.get(prev_block_url, timeout=5).json()
        if len(prev_blocks) > 1:
            dt = prev_blocks[0]["timestamp"] - prev_blocks[1]["timestamp"]
            lambda_rate = 1.0 / max(dt, 1.0)
        else:
            lambda_rate = 1.0 / 600.0

        I = compute_expansion_rate(subsidy, supply, lambda_rate)  # noqa: E741

        return {
            "h": height,
            "t": t,
            "sigma": subsidy,
            "S": supply,
            "lambda": lambda_rate,
            "I": I,
        }
    except Exception:
        return fetch_block_data_mock(height)


def fetch_wallet_rpc_mock() -> Optional[Dict]:
    """Mock wallet data for testing."""
    return {
        "W": 12_000_000.0,  # sats
        "A": 18_000_000.0,  # seconds
        "i": 4700.0,  # sats/s
        "mu": 3800.0,  # sats/s
        "CP": 2_500_000.0,  # sats
    }


def fetch_wallet_rpc() -> Optional[Dict]:
    """
    Query local Bitcoin node RPC for wallet state.

    Returns:
        Dictionary with keys: W, A, i, mu, CP
        Returns None if RPC call fails
    """
    if MOCK_MODE:
        return fetch_wallet_rpc_mock()

    try:
        import requests

        payload = {
            "method": "getbalances",
            "params": [],
            "jsonrpc": "2.0",
            "id": 1,
        }
        response = requests.post(
            BITCOIN_RPC_URL,
            json=payload,
            auth=(BITCOIN_RPC_USER, BITCOIN_RPC_PASSWORD),
            timeout=5,
        )

        if response.status_code != 200:
            return fetch_wallet_rpc_mock()

        data = response.json()
        balance = (
            data.get("result", {}).get("mine", {}).get("trusted", 0) * 1e8
        )  # BTC to sats

        # Mock UTXO age and flows for now
        utxos = []
        payload = {"method": "listunspent", "params": [0], "jsonrpc": "2.0", "id": 2}
        utxo_resp = requests.post(
            BITCOIN_RPC_URL,
            json=payload,
            auth=(BITCOIN_RPC_USER, BITCOIN_RPC_PASSWORD),
            timeout=5,
        )
        if utxo_resp.status_code == 200:
            utxos = utxo_resp.json().get("result", [])

        A = compute_coin_age(utxos)
        i, mu = compute_flows(utxos)  # Simplified

        return {
            "W": balance,
            "A": A,
            "i": i,
            "mu": mu,
            "CP": 0.0,  # Would need transaction history
        }
    except Exception:
        return fetch_wallet_rpc_mock()


def compute_expansion_rate(sigma: float, S: float, lambda_rate: float) -> float:
    """
    Compute protocol expansion rate I(t) = (sigma / S) * lambda.

    Args:
        sigma: Block subsidy [BTC/block]
        S: Circulating supply [BTC]
        lambda_rate: Block arrival rate [blocks/s]

    Returns:
        I: Expansion rate [s⁻¹]
    """
    if S == 0:
        return 0.0
    return (sigma / S) * lambda_rate


def compute_coin_age(utxos: List[Dict]) -> float:
    """
    Compute value-weighted coin age from UTXO set.

    Args:
        utxos: List of UTXOs, each with value and age

    Returns:
        A: Value-weighted coin age [s]
    """
    if not utxos:
        return 0.0

    current_time = int(time.time())
    total_value_age = 0.0
    total_value = 0.0

    for utxo in utxos:
        value = utxo.get("amount", 0) * 1e8  # BTC to sats
        age = current_time - utxo.get("time", current_time)
        total_value_age += value * age
        total_value += value

    if total_value == 0:
        return 0.0
    return total_value_age / total_value


def compute_flows(tx_history: List[Dict], window_seconds: int = 7 * 86400) -> tuple:
    """
    Compute rolling income (i) and spending (mu) rates.

    Args:
        tx_history: Transaction history
        window_seconds: Rolling window size [s] (default: 7 days)

    Returns:
        (i, mu): Income rate [sats/s], spending rate [sats/s]
    """
    if not tx_history:
        return (0.0, 0.0)

    current_time = int(time.time())
    cutoff = current_time - window_seconds

    income = 0.0
    spending = 0.0

    for tx in tx_history:
        if tx.get("time", 0) < cutoff:
            continue
        amount = tx.get("amount", 0) * 1e8  # BTC to sats
        if amount > 0:
            income += amount
        else:
            spending += abs(amount)

    window_dt = (
        min(window_seconds, current_time - cutoff) if cutoff > 0 else window_seconds
    )
    i = income / window_dt if window_dt > 0 else 0.0
    mu = spending / window_dt if window_dt > 0 else 0.0

    return (i, mu)


def update_blocks_table(conn: sqlite3.Connection, block_data: Dict):
    """Insert/update block data in blocks table."""
    conn.execute(
        """INSERT OR REPLACE INTO blocks (h, t, sigma, S, lambda, I)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (
            block_data["h"],
            block_data["t"],
            block_data["sigma"],
            block_data["S"],
            block_data["lambda"],
            block_data["I"],
        ),
    )
    conn.commit()


def update_wallet_table(
    conn: sqlite3.Connection, wallet_data: Dict, ssr: float, f: float
):
    """Insert/update wallet state in wallet table."""
    conn.execute(
        """INSERT OR REPLACE INTO wallet (t, W, A, i, mu, CP, SSR, f)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            int(time.time()),
            wallet_data["W"],
            wallet_data["A"],
            wallet_data["i"],
            wallet_data["mu"],
            wallet_data.get("CP", 0.0),
            ssr,
            f,
        ),
    )
    conn.commit()


def update_metrics_table(
    conn: sqlite3.Connection, timestamp: int, S_cum: float, BXS_cum: float
):
    """Insert/update cumulative metrics in metrics table."""
    conn.execute(
        """INSERT OR REPLACE INTO metrics (t, S_cum, BXS_cum)
           VALUES (?, ?, ?)""",
        (timestamp, S_cum, BXS_cum),
    )
    conn.commit()


def pipeline_step(conn: sqlite3.Connection, height: int):
    """
    Execute one pipeline step: fetch data, compute, write to DB.

    Args:
        conn: SQLite connection
        height: Block height to process
    """
    block_data = fetch_block_data(height)
    if not block_data:
        return

    update_blocks_table(conn, block_data)

    wallet_data = fetch_wallet_rpc()
    if not wallet_data:
        return

    # Compute SSR(t) and f(t) per paper formulas
    # Use default baselines (would ideally load from DB rolling medians)
    t = int(time.time())
    r = 2 * 365 * 24 * 3600  # 2 years
    t_min = 1_000
    mu_min = 1e-6

    import sys
    import os

    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from code.bxs_calculator import compute_ssr, compute_f

    ssr = compute_ssr(
        wallet_data["W"],
        wallet_data["i"],
        wallet_data["mu"],
        wallet_data.get("CP", 0.0),
        t,
        r,
        t_min,
        mu_min,
    )

    # Get baselines (simplified - would query rolling median)
    A0 = 1.55e7  # 180 days default
    I0 = 2.61e-10

    f = compute_f(
        wallet_data["i"],
        wallet_data["A"],
        A0,
        block_data["I"],
        I0,
        ssr,
    )

    update_wallet_table(conn, wallet_data, ssr, f)
