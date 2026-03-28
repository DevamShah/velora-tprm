"use client";

import React from "react";
import { Badge } from "@/components/ui/badge";
import type { EvidenceExtraction } from "@/types/evidence";

interface ExtractionViewerProps {
  extractions: EvidenceExtraction[];
}

function confidenceColor(score: number): string {
  if (score >= 0.9) return "text-emerald-600 bg-emerald-50";
  if (score >= 0.7) return "text-amber-600 bg-amber-50";
  return "text-red-600 bg-red-50";
}

function confidenceLabel(score: number): string {
  if (score >= 0.9) return "High";
  if (score >= 0.7) return "Medium";
  return "Low";
}

export function ExtractionViewer({ extractions }: ExtractionViewerProps) {
  if (extractions.length === 0) {
    return (
      <div className="text-center py-8 text-text-muted text-sm">
        No extractions found for this document.
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {extractions.map((ext) => (
        <div
          key={ext.id}
          className="p-3 rounded-lg border border-surface-card-border bg-white hover:bg-surface-main/50 transition-colors"
        >
          <div className="flex items-start justify-between gap-3">
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-1">
                <span className="text-xs font-semibold text-text-muted uppercase tracking-wider">
                  {ext.field_name.replace(/_/g, " ")}
                </span>
                {ext.page_number && (
                  <span className="text-[10px] text-text-muted">
                    Page {ext.page_number}
                  </span>
                )}
              </div>
              <p className="text-sm text-text-primary font-medium">
                {ext.field_value}
              </p>
              {ext.source_text && (
                <p className="text-xs text-text-muted mt-1 line-clamp-2 italic">
                  &quot;{ext.source_text}&quot;
                </p>
              )}
            </div>
            <div
              className={`px-2 py-1 rounded-md text-xs font-medium shrink-0 ${confidenceColor(
                ext.confidence
              )}`}
            >
              {Math.round(ext.confidence * 100)}% {confidenceLabel(ext.confidence)}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
