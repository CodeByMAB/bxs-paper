#!/usr/bin/env python3
"""
Data Pipeline: Fetch from mempool.space + wallet RPC, write to SQLite.

Connects to local Bitcoin node and mempool.space API to populate
the schema defined in data/schema.sql.
"""

import sqlite3
from typing import Optional


def fetch_block_data(height: int) -> Optional[dict]:
    """
    Fetch block data from mempool.space API.
    
    Args:
        height: Block height
    
    Returns:
        Dictionary with keys: h, t, sigma, S, lambda, I
        Returns None if fetch fails
    """
    pass


def fetch_wallet_rpc() -> Optional[dict]:
    """
    Query local Bitcoin node RPC for wallet state.
    
    Returns:
        Dictionary with keys: W, A, i, mu, CP
        Returns None if RPC call fails
    """
    pass


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
    pass


def compute_coin_age(utxos: list) -> float:
    """
    Compute value-weighted coin age from UTXO set.
    
    Args:
        utxos: List of UTXOs, each with value and age
    
    Returns:
        A: Value-weighted coin age [s]
    """
    pass


def compute_flows(tx_history: list, window_seconds: int = 7 * 86400) -> tuple:
    """
    Compute rolling income (i) and spending (mu) rates.
    
    Args:
        tx_history: Transaction history
        window_seconds: Rolling window size [s] (default: 7 days)
    
    Returns:
        (i, mu): Income rate [sats/s], spending rate [sats/s]
    """
    pass


def update_blocks_table(conn: sqlite3.Connection, block_data: dict):
    """
    Insert/update block data in blocks table.
    
    Args:
        conn: SQLite connection
        block_data: Dictionary with keys: h, t, sigma, S, lambda, I
    """
    pass


def update_wallet_table(conn: sqlite3.Connection, wallet_data: dict, ssr: float, f: float):
    """
    Insert/update wallet state in wallet table.
    
    Args:
        conn: SQLite connection
        wallet_data: Dictionary with keys: W, A, i, mu, CP
        ssr: Computed SSR value
        f: Computed f(t) value
    """
    pass


def update_metrics_table(conn: sqlite3.Connection, timestamp: int, S_cum: float, BXS_cum: float):
    """
    Insert/update cumulative metrics in metrics table.
    
    Args:
        conn: SQLite connection
        timestamp: Unix seconds
        S_cum: Cumulative S [sats]
        BXS_cum: Cumulative BXS [sats·s]
    """
    pass


def pipeline_step(conn: sqlite3.Connection, height: int):
    """
    Execute one pipeline step: fetch data, compute, write to DB.
    
    Args:
        conn: SQLite connection
        height: Block height to process
    """
    pass

