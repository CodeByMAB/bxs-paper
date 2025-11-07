import React from "react";
import Sparkline from "./Sparkline";

type MetricCardProps = {
  title: string;
  value: string | number;
  unitLabel?: string;        // e.g., "[sats/s]"
  subtitle?: string;         // optional explanatory text
  tooltip?: string;          // hover tooltip text
  series?: number[];         // sparkline data (optional)
  warn?: boolean;            // tint outline/background if true
};

export default function MetricCard({
  title, value, unitLabel, subtitle, tooltip, series, warn
}: MetricCardProps) {
  return (
    <div
      className={[
        "rounded-2xl shadow-md p-5 bg-white/90 backdrop-blur",
        "border",
        warn ? "border-amber-400 bg-amber-50/40" : "border-black/10"
      ].join(" ")}
    >
      <div className="flex items-center gap-2">
        <h3 className="text-sm font-medium text-black/70">{title}</h3>
        {tooltip && (
          <span
            className="text-xs text-black/50 cursor-help"
            title={tooltip}
            aria-label={tooltip}
          >
            ℹ️
          </span>
        )}
      </div>
      <div className="mt-1 text-3xl font-semibold tracking-tight tabular-nums">
        {value}
      </div>
      {unitLabel && (
        <div className="text-xs text-black/70 leading-tight mt-0.5 opacity-85">
          {unitLabel}
        </div>
      )}
      {subtitle && (
        <div className="text-xs text-black/50 mt-1">{subtitle}</div>
      )}
      {warn && (
        <div className="mt-2 inline-block px-2 py-0.5 text-xs font-medium bg-amber-200 text-amber-900 rounded-full">
          Runway {'<'} 0
        </div>
      )}
      {series && series.length > 0 && (
        <div className="mt-3">
          <Sparkline values={series} height={28} />
        </div>
      )}
    </div>
  );
}

