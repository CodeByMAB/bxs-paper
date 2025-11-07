#!/usr/bin/env python3
"""
CLI for backfilling from CSV and running compute+persist.
"""
import argparse
import csv
import os
import sqlite3
import sys
from datetime import datetime
from typing import Dict

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from code.alerts import process_alerts  # noqa: E402
from code.bxs_calculator import (  # noqa: E402
    compute_ssr,
    compute_f,
    integrate_s,
    integrate_bxs,
)


def init_db(db_path: str, schema_path: str):
    """Initialize database from schema."""
    # Verify schema file exists
    if not os.path.exists(schema_path):
        raise FileNotFoundError(
            f"Schema file not found: {schema_path}\n"
            f"Current working directory: {os.getcwd()}\n"
            f"Checked paths:\n"
            f"  - {schema_path}\n"
            f"  - {os.path.abspath(schema_path)}\n"
            f"  - /app/data/schema.sql (if in Docker)"
        )
    
    conn = sqlite3.connect(db_path)
    with open(schema_path, "r") as f:
        conn.executescript(f.read())
    conn.commit()
    return conn


def parse_csv_row(row: Dict) -> Dict:
    """Parse CSV row to internal format."""
    # Parse timestamp
    ts_str = row.get("timestamp", "")
    try:
        if "T" in ts_str or "Z" in ts_str:
            dt = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
            t = int(dt.timestamp())
        else:
            t = int(float(ts_str))
    except Exception:
        t = int(datetime.now().timestamp())

    return {
        "t": t,
        "W": float(row.get("W", 0)),
        "A": float(row.get("A", 0)),
        "I": float(row.get("I", 0)),
        "i": float(row.get("i", 0)),
        "mu": float(row.get("mu", 0)),
        "CP": float(row.get("CP", 0)),
        "r": float(row.get("r", 2.0 * 365 * 24 * 3600)),
        "A0": float(row.get("A0", 1.55e7)),
        "I0": float(row.get("I0", 2.61e-10)),
        "tmin": float(row.get("tmin", 2.592e6)),
        "mumin": float(row.get("mumin", 1.0)),
    }


def backfill_from_csv(
    conn: sqlite3.Connection, csv_path: str, start_height: int = 800000
):
    """Backfill database from CSV file."""
    print(f"Loading CSV from {csv_path}...")

    rows = []
    with open(csv_path, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(parse_csv_row(row))

    print(f"Loaded {len(rows)} rows")

    # Insert blocks (simplified - use deterministic heights)
    for i, row in enumerate(rows):
        height = start_height + i
        block_time = row["t"]

        # Compute I from sigma, S, lambda
        # For mock, use deterministic values
        halving_epoch = height // 210000
        sigma = 50.0 / (2**halving_epoch)
        supply = halving_epoch * 210000 * 50.0 + (height % 210000) * sigma
        lambda_rate = 1.0 / 600.0
        I = (sigma / supply) * lambda_rate  # noqa: E741

        conn.execute(
            """INSERT OR REPLACE INTO blocks (h, t, sigma, S, lambda, I)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (height, block_time, sigma, supply, lambda_rate, I),
        )

        # Compute SSR and f
        t_elapsed = row["t"] - rows[0]["t"] if rows else 1.0
        ssr = compute_ssr(
            row["W"],
            row["i"],
            row["mu"],
            row["CP"],
            t_elapsed,
            row["r"],
            row["tmin"],
            row["mumin"],
        )

        f = compute_f(
            row["i"],
            row["A"],
            row["A0"],
            row["I"],
            row["I0"],
            ssr,
        )

        # Insert wallet
        conn.execute(
            """INSERT OR REPLACE INTO wallet (t, W, A, i, mu, CP, SSR, f)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                row["t"],
                row["W"],
                row["A"],
                row["i"],
                row["mu"],
                row["CP"],
                ssr,
                f,
            ),
        )

    conn.commit()
    print(f"Inserted {len(rows)} blocks and wallet entries")
    return rows


def compute_and_persist(conn: sqlite3.Connection):
    """Compute S and BXS from wallet data and persist to metrics."""
    print("Computing metrics...")

    # Get all wallet entries
    wallets = conn.execute("""SELECT * FROM wallet ORDER BY t""").fetchall()

    if not wallets:
        print("No wallet data found")
        return

    timestamps = [w["t"] for w in wallets]
    f_series = [w["f"] for w in wallets]

    # Compute S
    S_series = integrate_s(f_series, timestamps)

    # Compute BXS from S
    BXS_series = integrate_bxs(S_series, timestamps)

    # Persist to metrics
    for i, wallet in enumerate(wallets):
        conn.execute(
            """INSERT OR REPLACE INTO metrics (t, S_cum, BXS_cum)
               VALUES (?, ?, ?)""",
            (wallet["t"], S_series[i], BXS_series[i]),
        )

    conn.commit()
    print(f"Computed and persisted {len(wallets)} metric entries")

    # Process alerts
    if wallets:
        latest_t = timestamps[-1]
        alerts = process_alerts(conn, latest_t)
        if alerts:
            print(f"Generated {len(alerts)} alerts")
        else:
            print("No alerts triggered")


def main():
    parser = argparse.ArgumentParser(description="BXS CLI: backfill and compute")
    parser.add_argument(
        "--db",
        default="data/bxs.sqlite",
        help="Database path",
    )
    parser.add_argument(
        "--csv",
        help="CSV file to backfill from",
    )
    parser.add_argument(
        "--schema",
        help="Schema file path",
    )
    parser.add_argument(
        "--init",
        action="store_true",
        help="Initialize database from schema",
    )
    parser.add_argument(
        "--compute",
        action="store_true",
        help="Compute metrics from wallet data",
    )

    args = parser.parse_args()
    
    # Set default schema path if not provided
    if not args.schema:
        # Check multiple possible locations (in order of preference)
        possible_paths = [
            "/app/data/schema.sql",  # Docker runtime (copied from /app/schema.sql by entrypoint)
            "/app/schema.sql",       # Docker image (before volume mount)
            "data/schema.sql",       # Relative path from project root
            os.path.join(os.path.dirname(__file__), "..", "..", "data", "schema.sql"),  # Relative from code/cli.py
        ]
        
        for path in possible_paths:
            abs_path = os.path.abspath(path)
            if os.path.exists(path) or os.path.exists(abs_path):
                args.schema = path if os.path.exists(path) else abs_path
                break
        else:
            # If none found, default to relative path (will fail with better error)
            args.schema = "data/schema.sql"

    # Ensure data directory exists
    os.makedirs(os.path.dirname(args.db) or ".", exist_ok=True)

    # Initialize DB if needed
    if args.init or not os.path.exists(args.db):
        print(f"Initializing database at {args.db}...")
        conn = init_db(args.db, args.schema)
    else:
        conn = sqlite3.connect(args.db)
    
    conn.row_factory = sqlite3.Row  # Enable row access by column name

    try:
        # Backfill from CSV
        if args.csv:
            backfill_from_csv(conn, args.csv)

        # Compute metrics
        if args.compute or args.csv:
            compute_and_persist(conn)

        print("Done!")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
