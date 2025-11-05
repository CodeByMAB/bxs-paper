-- data/schema.sql
CREATE TABLE blocks (
  h INTEGER PRIMARY KEY,
  t INTEGER NOT NULL,         -- unix seconds
  sigma REAL NOT NULL,        -- BTC per block
  S REAL NOT NULL,            -- BTC supply
  lambda REAL NOT NULL,       -- blocks per second
  I REAL NOT NULL             -- per second (sigma/S * lambda)
);

CREATE TABLE wallet (
  t INTEGER PRIMARY KEY,      -- unix seconds (block sample)
  W REAL NOT NULL,            -- sats
  A REAL NOT NULL,            -- seconds (value-weighted coin age)
  i REAL NOT NULL,            -- sats/s
  mu REAL NOT NULL,           -- sats/s
  CP REAL,                    -- sats (optional)
  SSR REAL NOT NULL,          -- dimensionless (can be <0)
  f REAL NOT NULL             -- sats/s
);

CREATE TABLE metrics (
  t INTEGER PRIMARY KEY,
  S_cum REAL NOT NULL,        -- sats
  BXS_cum REAL NOT NULL       -- sats*s
);

CREATE TABLE alerts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  t INTEGER NOT NULL,
  created_at INTEGER NOT NULL,  -- unix timestamp
  alert_type TEXT NOT NULL,     -- 'f_decline', 'ssr_negative', etc.
  severity REAL,                -- magnitude (e.g., %-change in f)
  context TEXT                  -- JSON: {W,A,I,SSR,f}
);

