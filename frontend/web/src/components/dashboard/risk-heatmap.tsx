"use client";

import React, { useState } from "react";
import { cn } from "@/lib/utils";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";

const IMPACT_LABELS = ["Negligible", "Minor", "Moderate", "Major", "Severe"];
const LIKELIHOOD_LABELS = ["Rare", "Unlikely", "Possible", "Likely", "Almost Certain"];

function getCellColor(impact: number, likelihood: number): string {
  const score = (impact + 1) * (likelihood + 1);
  if (score >= 20) return "bg-red-500 hover:bg-red-600";
  if (score >= 15) return "bg-red-400 hover:bg-red-500";
  if (score >= 10) return "bg-orange-400 hover:bg-orange-500";
  if (score >= 6) return "bg-yellow-400 hover:bg-yellow-500";
  if (score >= 3) return "bg-green-400 hover:bg-green-500";
  return "bg-green-300 hover:bg-green-400";
}

function getRiskLevel(impact: number, likelihood: number): string {
  const score = (impact + 1) * (likelihood + 1);
  if (score >= 20) return "Critical";
  if (score >= 15) return "High";
  if (score >= 10) return "Medium";
  if (score >= 6) return "Low";
  return "Minimal";
}

interface RiskHeatmapProps {
  vendorsByRisk?: Record<string, number>;
  className?: string;
}

export function RiskHeatmap({ vendorsByRisk, className }: RiskHeatmapProps) {
  const [activeCell, setActiveCell] = useState<{ i: number; l: number } | null>(
    null
  );

  // Simulate distribution across cells based on vendor risk data
  const getCellCount = (impact: number, likelihood: number): number => {
    if (!vendorsByRisk) return 0;
    const score = (impact + 1) * (likelihood + 1);
    if (score >= 20) return vendorsByRisk["critical"] || 0;
    if (score >= 15) return vendorsByRisk["high"] || 0;
    if (score >= 10) return vendorsByRisk["medium"] || 0;
    if (score >= 6) return vendorsByRisk["low"] || 0;
    return vendorsByRisk["unclassified"] || 0;
  };

  return (
    <div className={cn("space-y-2", className)}>
      <div className="flex items-end gap-1">
        <div className="flex flex-col items-end gap-1 pr-2 pb-7">
          {IMPACT_LABELS.slice()
            .reverse()
            .map((label) => (
              <div
                key={label}
                className="h-10 flex items-center text-[10px] text-text-muted font-medium leading-none"
              >
                {label}
              </div>
            ))}
          <span className="text-[10px] text-text-muted font-semibold uppercase tracking-wider mt-1 -rotate-90 origin-center translate-y-6">
            Impact
          </span>
        </div>
        <div className="flex-1">
          <TooltipProvider delayDuration={100}>
            <div className="grid grid-cols-5 gap-1">
              {Array.from({ length: 25 }).map((_, idx) => {
                const likelihood = idx % 5;
                const impact = 4 - Math.floor(idx / 5);
                const count = getCellCount(impact, likelihood);
                const riskLevel = getRiskLevel(impact, likelihood);

                return (
                  <Tooltip key={idx}>
                    <TooltipTrigger asChild>
                      <button
                        className={cn(
                          "h-10 rounded-md transition-all duration-150 flex items-center justify-center text-xs font-semibold text-white/90",
                          getCellColor(impact, likelihood),
                          activeCell?.i === impact && activeCell?.l === likelihood
                            ? "ring-2 ring-offset-1 ring-text-primary scale-105"
                            : ""
                        )}
                        onClick={() =>
                          setActiveCell(
                            activeCell?.i === impact && activeCell?.l === likelihood
                              ? null
                              : { i: impact, l: likelihood }
                          )
                        }
                      >
                        {count > 0 ? count : ""}
                      </button>
                    </TooltipTrigger>
                    <TooltipContent
                      side="top"
                      className="text-xs"
                    >
                      <p className="font-semibold">{riskLevel} Risk</p>
                      <p className="text-text-muted">
                        {IMPACT_LABELS[impact]} impact, {LIKELIHOOD_LABELS[likelihood]} likelihood
                      </p>
                      {count > 0 && <p>{count} vendor{count !== 1 ? "s" : ""}</p>}
                    </TooltipContent>
                  </Tooltip>
                );
              })}
            </div>
          </TooltipProvider>
          <div className="flex justify-between mt-2 px-1">
            {LIKELIHOOD_LABELS.map((label) => (
              <span
                key={label}
                className="text-[10px] text-text-muted font-medium"
              >
                {label}
              </span>
            ))}
          </div>
          <p className="text-center text-[10px] text-text-muted font-semibold uppercase tracking-wider mt-1">
            Likelihood
          </p>
        </div>
      </div>
    </div>
  );
}
