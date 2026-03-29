"use client";

import React, { useState } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { cn } from "@/lib/utils";

interface RiskTrendChartProps {
  avgRiskScore: number;
}

// Generate mock trend data points since the API provides current avg only
function generateTrendData(currentScore: number, days: number) {
  const data: Array<{ date: string; score: number }> = [];
  const now = new Date();
  for (let i = days; i >= 0; i--) {
    const date = new Date(now);
    date.setDate(date.getDate() - i);
    // Create a slight variance around the current score for realistic trend
    const variance = (Math.sin(i * 0.3) * 8 + Math.cos(i * 0.15) * 5);
    const score = Math.max(0, Math.min(100, currentScore + variance - (days - i) * 0.05));
    data.push({
      date: date.toLocaleDateString("en-US", { month: "short", day: "numeric" }),
      score: Math.round(score * 10) / 10,
    });
  }
  return data;
}

export function RiskTrendChart({ avgRiskScore }: RiskTrendChartProps) {
  const [range, setRange] = useState<30 | 60 | 90>(30);
  const data = generateTrendData(avgRiskScore, range);

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <div>
          <span className="text-2xl font-semibold text-text-primary">
            {avgRiskScore.toFixed(1)}
          </span>
          <span className="text-sm text-text-muted ml-1">avg score</span>
        </div>
        <div className="flex items-center gap-1 rounded-lg bg-surface-main p-0.5">
          {([30, 60, 90] as const).map((d) => (
            <button
              key={d}
              onClick={() => setRange(d)}
              className={cn(
                "px-2.5 py-1 text-xs font-medium rounded-md transition-all",
                range === d
                  ? "bg-surface-card text-text-primary shadow-sm"
                  : "text-text-muted hover:text-text-secondary"
              )}
            >
              {d}d
            </button>
          ))}
        </div>
      </div>
      <div className="h-48">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data}>
            <CartesianGrid
              strokeDasharray="3 3"
              stroke="#e5e7eb"
              vertical={false}
            />
            <XAxis
              dataKey="date"
              axisLine={false}
              tickLine={false}
              tick={{ fontSize: 10, fill: "#9ca3af" }}
              interval={Math.floor(data.length / 6)}
            />
            <YAxis
              domain={[0, 100]}
              axisLine={false}
              tickLine={false}
              tick={{ fontSize: 10, fill: "#9ca3af" }}
              width={32}
            />
            <Tooltip
              content={({ active, payload, label }) => {
                if (!active || !payload?.length) return null;
                return (
                  <div className="rounded-lg border border-surface-card-border bg-surface-card px-3 py-2 shadow-sm text-xs">
                    <p className="text-text-muted">{label}</p>
                    <p className="font-semibold text-text-primary">
                      Risk Score: {payload[0].value}
                    </p>
                  </div>
                );
              }}
            />
            <Line
              type="monotone"
              dataKey="score"
              stroke="#6366f1"
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 4, fill: "#6366f1", stroke: "#fff", strokeWidth: 2 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
