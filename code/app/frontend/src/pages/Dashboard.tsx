import React, { useEffect, useState } from "react";
import MetricCard from "../components/MetricCard";

interface LatestMetrics {
  t: string;
  h: number;
  W: number;
  A: number;
  I: number;
  i: number;
  mu: number;
  SSR: number;
  f: number;
  S_cum: number;
  BXS_cum: number;
  ready?: boolean;
}

interface RangeMetrics {
  t: string;
  W?: number;
  i?: number;
  mu?: number;
  f?: number;
  A?: number;
  I?: number;
}

export default function Dashboard() {
  const [latest, setLatest] = useState<LatestMetrics | null>(null);
  const [series, setSeries] = useState<RangeMetrics[]>([]);
  const [loading, setLoading] = useState(true);
  const [warming, setWarming] = useState(false);

  async function fetchData() {
    setLoading(true);
    try {
      const res = await fetch("/metrics/latest");
      if (!res.ok) {
        if (res.status === 503) {
          setWarming(true);
        }
        throw new Error(`HTTP ${res.status}`);
      }
      const latestJson = await res.json();
      setLatest(latestJson);
      setWarming(false);

      // Fetch range data for sparklines (last 30 days)
      const now = Math.floor(Date.now() / 1000);
      const start = now - 30 * 24 * 3600;
      try {
        const rangeRes = await fetch(`/metrics/range?start=${start}&end=${now}&step=day`);
        if (rangeRes.ok) {
          const rangeData = await rangeRes.json();
          setSeries(rangeData);
        }
      } catch (e) {
        // Fallback: create minimal series from latest
        if (latestJson) {
          setSeries([latestJson]);
        }
      }
    } catch (error) {
      console.error("Failed to fetch metrics:", error);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 60000); // Refresh every 60s
    return () => clearInterval(interval);
  }, []);

  if (loading && !latest) {
    return (
      <div className="p-6 md:p-8 flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-black/70">Loading metrics...</p>
        </div>
      </div>
    );
  }

  const ssr = latest?.SSR ?? 0;
  const warn = ssr < 0;

  // Extract arrays for sparklines (downsample to ~80 points max)
  const downsample = (arr: number[], maxPoints: number) => {
    if (arr.length <= maxPoints) return arr;
    const step = Math.ceil(arr.length / maxPoints);
    const result = [];
    for (let i = 0; i < arr.length; i += step) {
      result.push(arr[i]);
    }
    return result;
  };

  const sW = downsample(
    series.map((d) => d.W ?? latest?.W ?? 0),
    80
  );
  const sI = downsample(
    series.map((d) => d.i ?? latest?.i ?? 0),
    80
  );
  const sMu = downsample(
    series.map((d) => d.mu ?? latest?.mu ?? 0),
    80
  );
  const sF = downsample(
    series.map((d) => d.f ?? latest?.f ?? 0),
    80
  );

  return (
    <div className="p-6 md:p-8 min-h-screen bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500">
      <div className="max-w-7xl mx-auto">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-6 gap-4">
          <div>
            <h1 className="text-2xl font-bold text-white">Bitcoin Seconds (BXS)</h1>
            {warming && (
              <div className="text-xs text-white/80 mt-1">
                Warming up baselines… some metrics may be volatile for ~30d.
              </div>
            )}
          </div>
          <div className="flex justify-end md:justify-end">
            <button
              onClick={fetchData}
              disabled={loading}
              className="px-4 py-2 rounded-lg bg-white/20 backdrop-blur text-white hover:bg-white/30 transition-colors disabled:opacity-50 w-full md:w-auto"
            >
              {loading ? "Refreshing..." : "Refresh Data"}
            </button>
          </div>
        </div>

        {/* Cards grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <MetricCard
            title="BALANCE W(t)"
            value={latest?.W?.toLocaleString() ?? "—"}
            unitLabel="[sats]"
            subtitle="Current holdings"
            series={sW.length > 1 ? sW : undefined}
          />

          <MetricCard
            title="COIN AGE A(t)"
            value={(latest?.A ?? 0).toLocaleString()}
            unitLabel="[seconds]"
            subtitle="Value-weighted holding duration"
            tooltip="A₀: Rolling 180-day median of value-weighted coin age (configurable)."
          />

          <MetricCard
            title="EXPANSION RATE I(t)"
            value={(latest?.I ?? 0).toExponential(2)}
            unitLabel="[s⁻¹]"
            subtitle="Protocol monetary expansion"
            tooltip="I₀: Epoch-median of I(t)=σ/S·λ (configurable per halving)."
          />

          <MetricCard
            title="INCOME RATE i(t)"
            value={(latest?.i ?? 0).toLocaleString()}
            unitLabel="[sats/s]"
            subtitle="Inflow rate"
            series={sI.length > 1 ? sI : undefined}
          />

          <MetricCard
            title="SPENDING RATE μ(t)"
            value={(latest?.mu ?? 0).toLocaleString()}
            unitLabel="[sats/s]"
            subtitle="Outflow rate"
            series={sMu.length > 1 ? sMu : undefined}
          />

          <MetricCard
            title="SSR(t)"
            value={(latest?.SSR ?? 0).toFixed(2)}
            unitLabel="[dimensionless]"
            subtitle="Surplus-to-Spending Ratio (financial runway)"
            warn={warn}
          />

          <MetricCard
            title="FLOW f(t)"
            value={(latest?.f ?? 0).toLocaleString(undefined, { maximumFractionDigits: 2 })}
            unitLabel="[sats/s]"
            subtitle="Durability-adjusted flow"
            warn={warn}
            series={sF.length > 1 ? sF : undefined}
          />

          <MetricCard
            title="STOCK S(T)"
            value={(latest?.S_cum ?? 0).toLocaleString()}
            unitLabel="[sats]"
            subtitle="Cumulative durable claims"
          />

          <MetricCard
            title="BXS(T)"
            value={(latest?.BXS_cum ?? 0).toLocaleString()}
            unitLabel="[sats·s]"
            subtitle="Time-weighted persistence"
          />
        </div>

        {/* Key Formulas box with extra padding */}
        <div className="rounded-2xl border border-white/20 bg-white/90 backdrop-blur p-6 md:p-10 shadow-lg">
          <h2 className="text-lg font-semibold mb-2">Key Formulas (BXS v0.6.7)</h2>
          <code className="block text-sm md:text-base whitespace-normal break-words mb-2">
            f(t) = i(t) × (A(t)/A₀) × (I(t)/I₀) × SSR(t)
          </code>
          <div className="text-sm text-black/60 mt-1 mb-4">
            Durability-adjusted flow combines income with HODLing strength, protocol context, and runway.
          </div>
          <code className="block text-sm md:text-base mt-3 break-words">
            S(T) = ∫₀ᵀ f(t) dt
          </code>
          <code className="block text-sm md:text-base mt-1 break-words">
            BXS(T) = ∫₀ᵀ S(t) dt
          </code>
        </div>
      </div>
    </div>
  );
}

