import React from "react";

export default function Sparkline({
  values,
  width = 160,
  height = 28,
  stroke = "currentColor"
}: { values: number[]; width?: number; height?: number; stroke?: string }) {
  if (!values || values.length < 2) return null;

  const min = Math.min(...values);
  const max = Math.max(...values);
  const range = max - min || 1;
  const stepX = width / (values.length - 1);

  const points = values.map((v, i) => {
    const x = i * stepX;
    const y = height - ((v - min) / range) * height;
    return `${x},${y}`;
  }).join(" ");

  return (
    <svg viewBox={`0 0 ${width} ${height}`} width="100%" height={height} className="block">
      <polyline
        fill="none"
        stroke={stroke}
        strokeWidth="2"
        points={points}
        className="text-blue-600/70"
      />
    </svg>
  );
}

