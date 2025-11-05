#!/usr/bin/env python3
"""
Generate results/quickstart.json with latest metrics snapshot.
"""
import json
import sqlite3
import os
import sys
import argparse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def generate_quickstart(db_path: str, output_path: str):
    """Generate quickstart JSON from database."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    
    try:
        # Get latest wallet
        wallet = conn.execute(
            """SELECT * FROM wallet ORDER BY t DESC LIMIT 1"""
        ).fetchone()
        
        if not wallet:
            print("No wallet data found")
            return
        
        # Get latest block
        block = conn.execute(
            """SELECT * FROM blocks ORDER BY h DESC LIMIT 1"""
        ).fetchone()
        
        # Get latest metrics
        metrics = conn.execute(
            """SELECT * FROM metrics ORDER BY t DESC LIMIT 1"""
        ).fetchone()
        
        snapshot = {
            "timestamp": wallet["t"],
            "wallet": {
                "W": wallet["W"],
                "A": wallet["A"],
                "i": wallet["i"],
                "mu": wallet["mu"],
                "CP": wallet.get("CP", 0.0),
                "SSR": wallet["SSR"],
                "f": wallet["f"],
            },
            "block": {
                "h": block["h"] if block else None,
                "I": block["I"] if block else None,
                "sigma": block["sigma"] if block else None,
                "S": block["S"] if block else None,
            },
            "metrics": {
                "S_cum": metrics["S_cum"] if metrics else None,
                "BXS_cum": metrics["BXS_cum"] if metrics else None,
            },
        }
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(snapshot, f, indent=2)
        
        print(f"Generated {output_path}")
        print(json.dumps(snapshot, indent=2))
        
    finally:
        conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate quickstart.json")
    parser.add_argument("--db", default="data/bxs.sqlite", help="Database path")
    parser.add_argument("--output", default="results/quickstart.json", help="Output path")
    args = parser.parse_args()
    
    generate_quickstart(args.db, args.output)

