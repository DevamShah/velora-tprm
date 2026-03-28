"use client";

import React from "react";
import {
  AlertTriangle,
  ClipboardCheck,
  FileText,
  RefreshCw,
  TrendingUp,
  MessageSquare,
  StickyNote,
  Clock,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { useVendorTimeline } from "@/hooks/use-monitoring";
import type { TimelineEventType } from "@/types/monitoring";
import { TIMELINE_EVENT_TYPE_LABELS } from "@/types/monitoring";

const EVENT_ICONS: Record<TimelineEventType, React.ElementType> = {
  alert: AlertTriangle,
  assessment: ClipboardCheck,
  evidence: FileText,
  status_change: RefreshCw,
  score_change: TrendingUp,
  communication: MessageSquare,
  note: StickyNote,
};

const EVENT_COLORS: Record<TimelineEventType, string> = {
  alert: "bg-red-100 text-red-600",
  assessment: "bg-blue-100 text-blue-600",
  evidence: "bg-emerald-100 text-emerald-600",
  status_change: "bg-purple-100 text-purple-600",
  score_change: "bg-amber-100 text-amber-600",
  communication: "bg-cyan-100 text-cyan-600",
  note: "bg-gray-100 text-gray-600",
};

function formatDateTime(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}

interface VendorTimelineProps {
  vendorId: string;
}

export function VendorTimeline({ vendorId }: VendorTimelineProps) {
  const { events, isLoading, error } = useVendorTimeline(vendorId);

  if (isLoading) {
    return (
      <div className="space-y-4 p-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="flex gap-3">
            <Skeleton className="h-8 w-8 rounded-full shrink-0" />
            <div className="space-y-2 flex-1">
              <Skeleton className="h-4 w-48" />
              <Skeleton className="h-3 w-72" />
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-8 text-text-muted text-sm">
        Failed to load timeline: {error}
      </div>
    );
  }

  if (events.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-text-muted">
        <Clock className="h-8 w-8 mb-2" />
        <p className="text-sm font-medium">No timeline events yet</p>
        <p className="text-xs mt-0.5">
          Events will appear here as vendor interactions occur.
        </p>
      </div>
    );
  }

  return (
    <div className="relative">
      {/* Vertical line */}
      <div className="absolute left-4 top-4 bottom-4 w-px bg-surface-card-border" />

      <div className="space-y-0">
        {events.map((event, idx) => {
          const Icon = EVENT_ICONS[event.event_type] || StickyNote;
          const colorClass = EVENT_COLORS[event.event_type] || EVENT_COLORS.note;

          return (
            <div key={event.id} className="relative flex gap-4 pb-6 last:pb-0">
              {/* Icon */}
              <div
                className={`relative z-10 flex items-center justify-center w-8 h-8 rounded-full shrink-0 ${colorClass}`}
              >
                <Icon className="h-3.5 w-3.5" />
              </div>

              {/* Content */}
              <div className="flex-1 min-w-0 pt-0.5">
                <div className="flex items-center gap-2 mb-0.5">
                  <span className="text-sm font-medium text-text-primary">
                    {event.title}
                  </span>
                  <Badge variant="outline" className="text-[10px]">
                    {TIMELINE_EVENT_TYPE_LABELS[event.event_type]}
                  </Badge>
                </div>
                {event.description && (
                  <p className="text-sm text-text-secondary line-clamp-2">
                    {event.description}
                  </p>
                )}
                <p className="text-xs text-text-muted mt-1">
                  {formatDateTime(event.created_at)}
                  {event.created_by && ` by ${event.created_by}`}
                </p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
