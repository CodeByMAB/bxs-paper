#!/usr/bin/env python3
"""
FastAPI service for BXS metrics and alerts.
"""
import os
import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional
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


@app.get("/metrics/latest")
def latest():
    """
    Get latest BXS metrics.
    
    Returns most recent values for W(t), A(t), I(t), i(t), μ(t), SSR(t), 
    f(t), S_cum(t), and BXS_cum(t) from the database.
    
    Returns HTTP 503 with {"ready": false} during warm-up.
    """
    conn = get_db()
    try:
        # Check if wallet table exists and has data
        wallet = conn.execute(
            """SELECT * FROM wallet ORDER BY t DESC LIMIT 1"""
        ).fetchone()

        if not wallet:
            return JSONResponse(
                status_code=503,
                content={"ready": False, "message": "No data available yet. Pipeline is initializing."}
            )

        # Get latest block for I and h
        block = conn.execute(
            """SELECT h, I FROM blocks ORDER BY h DESC LIMIT 1"""
        ).fetchone()

        # Get latest metrics
        metrics = conn.execute(
            """SELECT * FROM metrics ORDER BY t DESC LIMIT 1"""
        ).fetchone()

        # Convert timestamp to ISO8601
        timestamp_iso = datetime.utcfromtimestamp(wallet["t"]).strftime("%Y-%m-%dT%H:%M:%SZ")

        # Cap SSR for UI display (retain negative signal but cap at [-10, +10])
        ssr_raw = wallet["SSR"]
        ssr_display = max(-10.0, min(10.0, ssr_raw)) if ssr_raw is not None else 0.0
        
        return MetricsLatest(
            t=timestamp_iso,
            h=block["h"] if block else 0,
            W=wallet["W"],
            A=wallet["A"],
            I=block["I"] if block else 0.0,
            i=wallet["i"],
            mu=wallet["mu"],
            SSR=ssr_display,  # Capped for UI, but raw value retained in DB
            f=wallet["f"],
            S_cum=metrics["S_cum"] if metrics else 0.0,
            BXS_cum=metrics["BXS_cum"] if metrics else 0.0,
            ready=True,
        )
    except sqlite3.OperationalError as e:
        return JSONResponse(
            status_code=503,
            content={"ready": False, "message": f"Database not ready: {str(e)}"}
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
            timestamp_iso = datetime.utcfromtimestamp(row["t"]).strftime("%Y-%m-%dT%H:%M:%SZ")
            data.append({
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
            })
        
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
            timestamp_iso = datetime.utcfromtimestamp(row["t"]).strftime("%Y-%m-%dT%H:%M:%SZ")
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


@app.get("/")
def root():
    """Serve the React dashboard."""
    dashboard_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(dashboard_path):
        return FileResponse(dashboard_path)
    
    # Fallback to API info if dashboard not found
    import time
    current_unix = int(time.time())
    hour_ago = current_unix - 3600
    
    return {
        "name": "BXS API",
        "version": "0.6.6",
        "status": "running",
        "endpoints": {
            "health": "GET /healthz",
            "latest": "GET /metrics/latest",
            "range": f"GET /metrics/range?start={hour_ago}&end={current_unix}",
            "alerts": "GET /alerts/recent?limit=10",
        },
        "note": "Timestamps must be Unix epoch seconds (integer)",
        "docs_enabled": DOCS_ENABLED,
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
    if full_path.startswith(("metrics", "alerts", "healthz", "docs", "openapi", "redoc", "static", "favicon.ico")):
        raise HTTPException(status_code=404, detail="Not found")
    
    dashboard_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(dashboard_path):
        return FileResponse(dashboard_path)
    raise HTTPException(status_code=404, detail="Dashboard not found")
