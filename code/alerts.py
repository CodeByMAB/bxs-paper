#!/usr/bin/env python3
"""
Alert rules for BXS metrics.
"""
import sqlite3
import json
from typing import Dict, List, Optional
from datetime import datetime, timedelta

ALERT_THRESHOLD_PCT = -20.0  # -20% decline
ALERT_WINDOW_DAYS = 14


def check_f_decline(conn: sqlite3.Connection, current_t: int) -> Optional[Dict]:
    """
    Check if f(t) has declined by ≥20% over trailing 14 days.
    
    Args:
        conn: Database connection
        current_t: Current timestamp
    
    Returns:
        Alert dict if triggered, None otherwise
    """
    window_seconds = ALERT_WINDOW_DAYS * 24 * 3600
    start_t = current_t - window_seconds
    
    # Get f values over window
    rows = conn.execute(
        """SELECT t, f, W, A, SSR FROM wallet
           WHERE t >= ? AND t <= ?
           ORDER BY t""",
        (start_t, current_t),
    ).fetchall()
    
    if len(rows) < 2:
        return None
    
    # Get first and last f values
    f_start = rows[0]["f"]
    f_current = rows[-1]["f"]
    
    if f_start <= 0:
        return None
    
    pct_change = ((f_current - f_start) / f_start) * 100.0
    
    if pct_change <= ALERT_THRESHOLD_PCT:
        # Get latest context
        latest = rows[-1]
        
        # Get I from blocks
        block = conn.execute(
            """SELECT I FROM blocks ORDER BY h DESC LIMIT 1"""
        ).fetchone()
        
        context = {
            "W": latest["W"],
            "A": latest["A"],
            "I": block["I"] if block else 0.0,
            "SSR": latest["SSR"],
            "f": latest["f"],
            "f_start": f_start,
            "f_current": f_current,
            "pct_change": pct_change,
        }
        
        return {
            "t": current_t,
            "alert_type": "f_decline",
            "severity": abs(pct_change),
            "context": context,
        }
    
    return None


def check_ssr_negative(conn: sqlite3.Connection, current_t: int) -> Optional[Dict]:
    """
    Check if SSR is negative (drawdown signal).
    
    Args:
        conn: Database connection
        current_t: Current timestamp
    
    Returns:
        Alert dict if SSR < 0, None otherwise
    """
    row = conn.execute(
        """SELECT t, W, A, SSR, f FROM wallet
           WHERE t <= ? ORDER BY t DESC LIMIT 1""",
        (current_t,),
    ).fetchone()
    
    if not row or row["SSR"] >= 0:
        return None
    
    block = conn.execute(
        """SELECT I FROM blocks ORDER BY h DESC LIMIT 1"""
    ).fetchone()
    
    context = {
        "W": row["W"],
        "A": row["A"],
        "I": block["I"] if block else 0.0,
        "SSR": row["SSR"],
        "f": row["f"],
    }
    
    return {
        "t": current_t,
        "alert_type": "ssr_negative",
        "severity": abs(row["SSR"]),
        "context": context,
    }


def process_alerts(conn: sqlite3.Connection, current_t: Optional[int] = None):
    """
    Process all alert rules and write to alerts table.
    
    Args:
        conn: Database connection
        current_t: Current timestamp (defaults to now)
    """
    if current_t is None:
        current_t = int(datetime.now().timestamp())
    
    alerts = []
    
    # Check f_decline
    f_alert = check_f_decline(conn, current_t)
    if f_alert:
        alerts.append(f_alert)
    
    # Check ssr_negative
    ssr_alert = check_ssr_negative(conn, current_t)
    if ssr_alert:
        alerts.append(ssr_alert)
    
    # Write alerts to DB
    for alert in alerts:
        conn.execute(
            """INSERT INTO alerts (t, created_at, alert_type, severity, context)
               VALUES (?, ?, ?, ?, ?)""",
            (
                alert["t"],
                current_t,
                alert["alert_type"],
                alert["severity"],
                json.dumps(alert["context"]),
            ),
        )
    
    conn.commit()
    return alerts

