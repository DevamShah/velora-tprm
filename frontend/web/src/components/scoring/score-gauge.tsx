"use client";

import { cn } from "@/lib/utils";
import { getScoreColor, getScoreLabel } from "@/types/scoring";

interface ScoreGaugeProps {
  score: number | null;
  size?: "sm" | "md" | "lg";
  showLabel?: boolean;
  className?: string;
}

const SIZE_CONFIG = {
  sm: { width: 80, stroke: 6, fontSize: 16, labelSize: 10, radius: 32 },
  md: { width: 120, stroke: 8, fontSize: 24, labelSize: 12, radius: 48 },
  lg: { width: 160, stroke: 10, fontSize: 32, labelSize: 14, radius: 64 },
};

export function ScoreGauge({
  score,
  size = "md",
  showLabel = true,
  className,
}: ScoreGaugeProps) {
  const config = SIZE_CONFIG[size];
  const { width, stroke, fontSize, labelSize, radius } = config;
  const center = width / 2;

  // Semi-circular arc from 180 to 0 degrees (bottom half is open)
  const startAngle = 180;
  const endAngle = 0;
  const circumference = Math.PI * radius;

  if (score === null || score === undefined) {
    return (
      <div className={cn("flex flex-col items-center", className)}>
        <svg width={width} height={width / 2 + stroke + 8} viewBox={`0 0 ${width} ${width / 2 + stroke + 8}`}>
          <path
            d={describeArc(center, center, radius, startAngle, endAngle)}
            fill="none"
            stroke="currentColor"
            strokeWidth={stroke}
            strokeLinecap="round"
            className="text-surface-card-border"
          />
          <text
            x={center}
            y={center - 4}
            textAnchor="middle"
            dominantBaseline="middle"
            className="fill-text-muted"
            fontSize={fontSize}
            fontWeight={600}
          >
            --
          </text>
        </svg>
        {showLabel && (
          <span className="text-text-muted" style={{ fontSize: labelSize }}>
            No score
          </span>
        )}
      </div>
    );
  }

  const normalizedScore = Math.max(0, Math.min(100, score));
  const progress = normalizedScore / 100;
  const dashOffset = circumference * (1 - progress);
  const color = getScoreColor(normalizedScore);
  const label = getScoreLabel(normalizedScore);

  return (
    <div className={cn("flex flex-col items-center", className)}>
      <svg width={width} height={width / 2 + stroke + 8} viewBox={`0 0 ${width} ${width / 2 + stroke + 8}`}>
        {/* Background arc */}
        <path
          d={describeArc(center, center, radius, startAngle, endAngle)}
          fill="none"
          stroke="currentColor"
          strokeWidth={stroke}
          strokeLinecap="round"
          className="text-surface-card-border"
        />
        {/* Progress arc */}
        <path
          d={describeArc(center, center, radius, startAngle, endAngle)}
          fill="none"
          stroke={color}
          strokeWidth={stroke}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={dashOffset}
          className="transition-all duration-700 ease-out"
        />
        {/* Score text */}
        <text
          x={center}
          y={center - 4}
          textAnchor="middle"
          dominantBaseline="middle"
          fill={color}
          fontSize={fontSize}
          fontWeight={700}
        >
          {normalizedScore}
        </text>
      </svg>
      {showLabel && (
        <span
          className="font-medium -mt-1"
          style={{ fontSize: labelSize, color }}
        >
          {label}
        </span>
      )}
    </div>
  );
}

function polarToCartesian(cx: number, cy: number, r: number, angle: number) {
  const rad = ((angle - 90) * Math.PI) / 180;
  return {
    x: cx + r * Math.cos(rad),
    y: cy + r * Math.sin(rad),
  };
}

function describeArc(
  cx: number,
  cy: number,
  r: number,
  startAngle: number,
  endAngle: number
) {
  const start = polarToCartesian(cx, cy, r, endAngle);
  const end = polarToCartesian(cx, cy, r, startAngle);
  const largeArcFlag = startAngle - endAngle <= 180 ? "0" : "1";
  return `M ${start.x} ${start.y} A ${r} ${r} 0 ${largeArcFlag} 0 ${end.x} ${end.y}`;
}
