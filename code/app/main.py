#!/usr/bin/env python3
"""
FastAPI service for BXS metrics and alerts.
"""
import os
import sqlite3
import json
from datetime import datetime
from typing import List, Dict
from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

# Disable docs in production for security
DOCS_ENABLED = os.getenv("DOCS_ENABLED", "false").lower() == "true"

app = FastAPI(
    title="BXS API",
    version="0.6.6",
    docs_url="/docs" if DOCS_ENABLED else None,
    redoc_url="/redoc" if DOCS_ENABLED else None,
    openapi_url="/openapi.json" if DOCS_ENABLED else None,
)

DB_PATH = os.getenv("DB_PATH", "data/bxs.sqlite")
ADMIN_ENABLED = os.getenv("ADMIN_ENABLED", "false").lower() == "true"

# Mount static files directory
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class MetricsLatest(BaseModel):
    """Latest BXS metrics (per BXS whitepaper v0.6.7)."""

    t: str  # ISO8601 timestamp
    h: int  # block height
    W: float  # balance/holdings [sats]
    A: float  # value-weighted coin age [s]
    I: float  # noqa: E741 - protocol expansion rate [s⁻¹]
    i: float  # income inflow rate [sats/s]
    mu: float  # spending outflow rate [sats/s]
    SSR: float  # Surplus-to-Spending Ratio
    f: float  # durability-adjusted flow [sats/s] (eq:flow)
    S_cum: float  # cumulative stock [sats] (eq:stock)
    BXS_cum: float  # time-weighted persistence [sats·s] (eq:bxs)
    ready: bool = True  # service ready status


class MetricsRange(BaseModel):
    data: List[Dict]


class Alert(BaseModel):
    t: str  # ISO8601 timestamp
    type: str  # alert type (e.g., "f_decline")
    severity: float  # severity 0-1
    context: Dict  # additional context (f_prev, f_now, SSR, W, etc.)


def get_db():
    """Get database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@app.get("/metrics/latest", response_class=JSONResponse)
def latest():
    """
    Get latest BXS metrics.

    Returns the most recent values mapped to API keys expected by tests:
    - f: durability-adjusted flow [sats/s] from wallet.f
    - S: cumulative stock [sats] from blocks.S
    - BXS: time-weighted persistence [sats·s] from metrics.BXS_cum

    Returns HTTP 404 if no data available.
    """
    conn = get_db()
    try:
        # Get latest wallet row (for f)
        wallet = conn.execute(
            """SELECT f FROM wallet ORDER BY t DESC LIMIT 1"""
        ).fetchone()

        # Get latest blocks row (for S)
        blocks = conn.execute(
            """SELECT S FROM blocks ORDER BY t DESC LIMIT 1"""
        ).fetchone()

        # Get latest metrics row (for BXS, mapped from BXS_cum)
        metrics = conn.execute(
            """SELECT BXS_cum FROM metrics ORDER BY t DESC LIMIT 1"""
        ).fetchone()

        if not wallet or not blocks or not metrics:
            raise HTTPException(
                status_code=404, detail="No metrics available"
            )

        # Map DB columns to expected API keys
        result = {
            "f": float(wallet["f"]) if wallet["f"] is not None else None,
            "S": float(blocks["S"]) if blocks["S"] is not None else None,
            "BXS": float(metrics["BXS_cum"]) if metrics["BXS_cum"] is not None else None,
        }

        return result
    except sqlite3.OperationalError as e:
        raise HTTPException(
            status_code=500, detail=f"Database error: {str(e)}"
        )
    finally:
        conn.close()


@app.get("/metrics/range")
def range_metrics(
    start: int = Query(..., description="Start timestamp (unix seconds)"),
    end: int = Query(..., description="End timestamp (unix seconds)"),
    step: str = Query("block", description="Aggregation step: block, hour, or day"),
):
    """
    Get BXS metrics in time range.

    Returns time series of W(t), A(t), i(t), μ(t), SSR(t), f(t), S_cum(t), BXS_cum(t)
    for the specified time period [start, end].

    Supports aggregation by block, hour, or day.
    """
    conn = get_db()
    try:
        # For now, return block-level data (can add aggregation later)
        rows = conn.execute(
            """SELECT w.t, w.W, w.A, w.i, w.mu, w.SSR, w.f, 
                      m.S_cum as S_cum, m.BXS_cum as BXS_cum,
                      b.h
               FROM wallet w
               LEFT JOIN metrics m ON w.t = m.t
               LEFT JOIN blocks b ON w.t = b.t
               WHERE w.t >= ? AND w.t <= ?
               ORDER BY w.t""",
            (start, end),
        ).fetchall()

        data = []
        for row in rows:
            timestamp_iso = datetime.utcfromtimestamp(row["t"]).strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            )
            data.append(
                {
                    "t": timestamp_iso,
                    "h": row["h"] if row["h"] else 0,
                    "W": row["W"],
                    "A": row["A"],
                    "i": row["i"],
                    "mu": row["mu"],
                    "SSR": row["SSR"],
                    "f": row["f"],
                    "S_cum": row["S_cum"] if row["S_cum"] else 0.0,
                    "BXS_cum": row["BXS_cum"] if row["BXS_cum"] else 0.0,
                }
            )

        return {"data": data, "count": len(data), "step": step}
    finally:
        conn.close()


@app.get("/alerts/recent")
def recent_alerts(days: int = Query(14, ge=1, le=365, description="Days to look back")):
    """
    Get recent alerts.

    Returns alerts from the last N days, ordered by timestamp (newest first).
    """
    conn = get_db()
    try:
        # Calculate cutoff timestamp
        from time import time

        cutoff_t = int(time()) - (days * 86400)

        rows = conn.execute(
            """SELECT * FROM alerts 
               WHERE t >= ? 
               ORDER BY t DESC 
               LIMIT 100""",
            (cutoff_t,),
        ).fetchall()

        alerts = []
        for row in rows:
            timestamp_iso = datetime.utcfromtimestamp(row["t"]).strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            )
            context = json.loads(row["context"]) if row["context"] else {}
            alerts.append(
                Alert(
                    t=timestamp_iso,
                    type=row["alert_type"],
                    severity=row["severity"],
                    context=context,
                )
            )
        return alerts
    finally:
        conn.close()


@app.post("/admin/recompute")
def recompute():
    """Recompute metrics from wallet data (admin only)."""
    if not ADMIN_ENABLED:
        raise HTTPException(status_code=403, detail="Admin endpoint disabled")

    conn = get_db()
    try:
        # Get all wallet entries
        wallets = conn.execute("""SELECT * FROM wallet ORDER BY t""").fetchall()

        if not wallets:
            return {"status": "no_data"}

        # Import compute functions
        import sys
        import os

        sys.path.insert(
            0,
            os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            ),
        )
        from code.bxs_calculator import integrate_s, integrate_bxs

        timestamps = [w["t"] for w in wallets]
        f_series = [w["f"] for w in wallets]

        # Compute S and BXS
        S_series = integrate_s(f_series, timestamps)

        # Get S values for BXS integration
        metrics_existing = conn.execute(
            """SELECT t, S_cum FROM metrics ORDER BY t"""
        ).fetchall()

        # If metrics exist, use them; otherwise use S_series
        if metrics_existing:
            S_for_bxs = [m["S_cum"] for m in metrics_existing]
            timestamps_bxs = [m["t"] for m in metrics_existing]
        else:
            S_for_bxs = S_series
            timestamps_bxs = timestamps

        BXS_series = integrate_bxs(S_for_bxs, timestamps_bxs)

        # Update metrics table
        for i, wallet in enumerate(wallets):
            update_metrics_table(conn, wallet["t"], S_series[i], BXS_series[i])

        return {
            "status": "success",
            "processed": len(wallets),
            "latest_t": timestamps[-1] if timestamps else None,
        }
    finally:
        conn.close()


def update_metrics_table(
    conn: sqlite3.Connection, timestamp: int, S_cum: float, BXS_cum: float
):
    """Helper to update metrics."""
    conn.execute(
        """INSERT OR REPLACE INTO metrics (t, S_cum, BXS_cum)
           VALUES (?, ?, ?)""",
        (timestamp, S_cum, BXS_cum),
    )
    conn.commit()


@app.get("/", response_class=JSONResponse)
def root():
    """
    Return API information with available endpoints.
    
    Always returns JSON (tests expect "endpoints" key).
    """
    return {
        "endpoints": [
            "/metrics/latest",
            "/metrics/range",
            "/alerts/recent",
            "/healthz",
        ]
    }


@app.get("/favicon.ico")
def favicon():
    """Serve favicon."""
    favicon_path = os.path.join(STATIC_DIR, "favicon.ico")
    if os.path.exists(favicon_path):
        return FileResponse(favicon_path)
    raise HTTPException(status_code=404, detail="Favicon not found")


@app.get("/healthz")
def healthz():
    """Health check endpoint for CI."""
    return {"status": "ok"}


# Catch-all route for React SPA (must be at the very end, after all API routes)
@app.get("/{full_path:path}")
def serve_spa(full_path: str):
    """Serve React app for all non-API routes."""
    # Don't serve SPA for API routes
    if full_path.startswith(
        (
            "metrics",
            "alerts",
            "healthz",
            "docs",
            "openapi",
            "redoc",
            "static",
            "favicon.ico",
        )
    ):
        raise HTTPException(status_code=404, detail="Not found")

    dashboard_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(dashboard_path):
        return FileResponse(dashboard_path)
    raise HTTPException(status_code=404, detail="Dashboard not found")
