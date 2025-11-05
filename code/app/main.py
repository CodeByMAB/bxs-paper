#!/usr/bin/env python3
"""
FastAPI service for BXS metrics and alerts.
"""
import os
import sqlite3
import json
from typing import Optional, List, Dict
from datetime import datetime
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="BXS API", version="0.6.6")

DB_PATH = os.getenv("DB_PATH", "data/bxs.sqlite")
ADMIN_ENABLED = os.getenv("ADMIN_ENABLED", "false").lower() == "true"


class MetricsLatest(BaseModel):
    t: int
    W: float
    A: float
    I: float
    i: float
    mu: float
    SSR: float
    f: float
    S: float
    BXS: float


class MetricsRange(BaseModel):
    data: List[Dict]


class Alert(BaseModel):
    t: int
    alert_type: str
    severity: float
    context: Dict


def get_db():
    """Get database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@app.get("/metrics/latest", response_model=MetricsLatest)
def latest():
    """Get latest metrics."""
    conn = get_db()
    try:
        # Get latest wallet entry
        wallet = conn.execute(
            """SELECT * FROM wallet ORDER BY t DESC LIMIT 1"""
        ).fetchone()
        
        if not wallet:
            raise HTTPException(status_code=404, detail="No wallet data found")
        
        # Get latest block for I
        block = conn.execute(
            """SELECT I FROM blocks ORDER BY h DESC LIMIT 1"""
        ).fetchone()
        
        # Get latest metrics
        metrics = conn.execute(
            """SELECT * FROM metrics ORDER BY t DESC LIMIT 1"""
        ).fetchone()
        
        return MetricsLatest(
            t=wallet["t"],
            W=wallet["W"],
            A=wallet["A"],
            I=block["I"] if block else 0.0,
            i=wallet["i"],
            mu=wallet["mu"],
            SSR=wallet["SSR"],
            f=wallet["f"],
            S=metrics["S_cum"] if metrics else 0.0,
            BXS=metrics["BXS_cum"] if metrics else 0.0,
        )
    finally:
        conn.close()


@app.get("/metrics/range")
def range_metrics(
    start: int = Query(..., description="Start timestamp (unix seconds)"),
    end: int = Query(..., description="End timestamp (unix seconds)"),
):
    """Get metrics in time range."""
    conn = get_db()
    try:
        rows = conn.execute(
            """SELECT w.t, w.W, w.A, w.i, w.mu, w.SSR, w.f, m.S_cum as S, m.BXS_cum as BXS
               FROM wallet w
               LEFT JOIN metrics m ON w.t = m.t
               WHERE w.t >= ? AND w.t <= ?
               ORDER BY w.t""",
            (start, end),
        ).fetchall()
        
        data = [dict(row) for row in rows]
        return {"data": data, "count": len(data)}
    finally:
        conn.close()


@app.get("/alerts/recent", response_model=List[Alert])
def recent_alerts(limit: int = Query(10, ge=1, le=100)):
    """Get recent alerts."""
    conn = get_db()
    try:
        rows = conn.execute(
            """SELECT * FROM alerts ORDER BY created_at DESC LIMIT ?""",
            (limit,),
        ).fetchall()
        
        alerts = []
        for row in rows:
            alerts.append(
                Alert(
                    t=row["t"],
                    alert_type=row["alert_type"],
                    severity=row["severity"],
                    context=json.loads(row["context"]),
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
        wallets = conn.execute(
            """SELECT * FROM wallet ORDER BY t"""
        ).fetchall()
        
        if not wallets:
            return {"status": "no_data"}
        
        # Import compute functions
        import sys
        import os
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
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


def update_metrics_table(conn: sqlite3.Connection, timestamp: int, S_cum: float, BXS_cum: float):
    """Helper to update metrics."""
    conn.execute(
        """INSERT OR REPLACE INTO metrics (t, S_cum, BXS_cum)
           VALUES (?, ?, ?)""",
        (timestamp, S_cum, BXS_cum),
    )
    conn.commit()


@app.get("/")
def root():
    """API root."""
    return {
        "name": "BXS API",
        "version": "0.6.6",
        "endpoints": [
            "GET /metrics/latest",
            "GET /metrics/range?start=...&end=...",
            "GET /alerts/recent?limit=10",
            "POST /admin/recompute",
        ],
    }


@app.get("/healthz")
def healthz():
    """Health check endpoint for CI."""
    return {"status": "ok"}

