import csv
import sys
from datetime import datetime, timezone


def parse_ts(s):
    try:
        return (
            datetime.fromisoformat(s.replace("Z", "+00:00"))
            .replace(tzinfo=timezone.utc)
            .timestamp()
        )
    except Exception:
        return float(s)


def row_f(row):
    A = float(row["A"])
    A0 = float(row["A0"]) or 1.0
    capital_i = float(row["I"])  # renamed from "I" to avoid E741
    capital_i0 = float(row["I0"]) or 1.0
    i = float(row["i"])
    tmin = float(row["tmin"])
    mumin = float(row["mumin"])
    mu = max(float(row["mu"]), mumin)
    CP = float(row["CP"])
    r = float(row["r"])
    s_bal = float(row["W"])
    # elapsed time since first row handled in integrate step; SSR uses floor tmin to avoid div-by-zero
    SSR_num = s_bal + r * i - CP
    SSR_den = max(tmin, tmin) * mu  # placeholder until you pass actual elapsed t
    SSR = SSR_num / SSR_den
    return i * (A / A0) * (capital_i / capital_i0) * max(SSR, 0.0)


def main(path):
    with open(path) as f:
        rows = list(csv.DictReader(f))
    # integrate per-sample using trapezoid with Δt from timestamps
    ts = [parse_ts(r["timestamp"]) for r in rows]
    fs = [row_f(r) for r in rows]
    S = 0.0
    BXS = 0.0
    for k in range(1, len(rows)):
        dt = ts[k] - ts[k - 1]
        f_mid = 0.5 * (fs[k] + fs[k - 1])
        S += f_mid * dt
        BXS += S * dt
    print({"S_sats": S, "BXS_sats_seconds": BXS})


if __name__ == "__main__":
    main(sys.argv[1])
