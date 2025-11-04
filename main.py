#!/usr/bin/env python3
# Bitcoin-Seconds CLI: compute BS_rho(T) from CSV time series
import argparse
import json
import os
from datetime import datetime
import pandas as pd
import numpy as np
SEC_PER_YEAR = 365.0*24*3600.0
def parse_time(x):
    try:
        return float(x)
    except Exception:
        return datetime.fromisoformat(str(x).replace('Z','+00:00')).timestamp()
def discounted_integral(t, f, rho_s):
    t = np.asarray(t, dtype=float)
    f = np.asarray(f, dtype=float)
    if len(t) < 2:
        return 0.0
    dt = np.diff(t)
    w = np.exp(-rho_s * t)
    wmid = 0.5*(w[1:] + w[:-1])
    fmid = 0.5*(f[1:] + f[:-1])
    return float(np.sum(wmid * fmid * dt))
def load_series(path):
    df = pd.read_csv(path)
    required = ['timestamp','A','Y','R','c','iota']
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise SystemExit(f'Missing required columns: {missing}')
    df = df.copy()
    df['t_s'] = df['timestamp'].apply(parse_time)
    df = df.sort_values('t_s').reset_index(drop=True)
    t0 = df['t_s'].iloc[0]
    df['t'] = df['t_s'] - t0
    return df
def compute_bs(df, alpha, beta, gamma, rho_s):
    u = alpha*df['A'].to_numpy()*df['Y'].to_numpy() + beta*df['R'].to_numpy() - gamma*df['iota'].to_numpy()*df['c'].to_numpy()
    c = df['c'].to_numpy()
    t = df['t'].to_numpy()
    U = discounted_integral(t, u, rho_s)
    S = discounted_integral(t, c, rho_s)
    bs = float(U / S) if S != 0 else float('nan')
    return bs, U, S
def main():
    ap = argparse.ArgumentParser(description='Compute Bitcoin-Seconds index from CSV time series.')
    ap.add_argument('--input', required=True, help='CSV with columns: timestamp,A,Y,R,c,iota')
    ap.add_argument('--alpha', type=float, default=1.0)
    ap.add_argument('--beta', type=float, default=1.0)
    ap.add_argument('--gamma', type=float, default=1.0)
    ap.add_argument('--rho-per-year', type=float, default=0.05)
    ap.add_argument('--rho-per-second', type=float, default=None)
    ap.add_argument('--out', default='bs_report.json')
    args = ap.parse_args()
    rho_s = args.rho_per_second if args.rho_per_second is not None else args.rho_per_year/SEC_PER_YEAR
    df = load_series(args.input)
    bs, U, S = compute_bs(df, args.alpha, args.beta, args.gamma, rho_s)
    result = {
        'input': os.path.abspath(args.input),
        'n_rows': int(df.shape[0]),
        'alpha': args.alpha, 'beta': args.beta, 'gamma': args.gamma,
        'rho_per_year': None if args.rho_per_second is not None else args.rho_per_year,
        'rho_per_second': rho_s,
        'U_discounted': U,
        'S_discounted': S,
        'BS_index': bs
    }
    with open(args.out, 'w') as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result, indent=2))
if __name__ == '__main__':
    main()