#!/usr/bin/env python3
"""
Background pipeline runner for Docker container.
Runs data pipeline periodically and computes metrics.
"""
import os
import sys
import time
import sqlite3
import signal

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from code.data_pipeline import pipeline_step  # noqa: E402
from code.cli import compute_and_persist  # noqa: E402

RUNNING = True


def signal_handler(sig, frame):
    """Handle shutdown signals."""
    global RUNNING
    RUNNING = False
    print("Received shutdown signal, stopping pipeline...")


def main():
    """Main pipeline runner loop."""
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    db_path = os.getenv("DB_PATH", "/app/data/bxs.sqlite")
    interval = int(os.getenv("PIPELINE_INTERVAL_SECONDS", "600"))

    print(f"Starting pipeline runner: DB={db_path}, interval={interval}s")

    while RUNNING:
        try:
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row  # Enable row access by column name

            # Get latest block height or start from 800000
            try:
                result = conn.execute("SELECT MAX(h) FROM blocks").fetchone()
                height = (result[0] + 1) if result[0] else 800000
            except Exception:
                height = 800000

            # Run pipeline step
            pipeline_step(conn, height)

            # Compute metrics after pipeline update
            compute_and_persist(conn)

            conn.close()
            print(f"Pipeline step completed at height {height}")

        except Exception as e:
            print(f"Pipeline step failed: {e}")

        # Sleep for interval, but check RUNNING flag periodically
        for _ in range(interval):
            if not RUNNING:
                break
            time.sleep(1)

    print("Pipeline runner stopped")


if __name__ == "__main__":
    main()
