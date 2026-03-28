"use client";

import React from "react";
import Link from "next/link";
import { Bell, ExternalLink } from "lucide-react";
import { cn } from "@/lib/utils";
import type { DashboardAlert } from "@/types/dashboard";

const PRIORITY_STYLES: Record<string, { dot: string; bg: string }> = {
  p0: { dot: "bg-red-500", bg: "bg-red-50" },
  p1: { dot: "bg-orange-500", bg: "bg-orange-50" },
  p2: { dot: "bg-yellow-500", bg: "bg-yellow-50" },
  p3: { dot: "bg-blue-500", bg: "bg-blue-50" },
  p4: { dot: "bg-gray-400", bg: "bg-gray-50" },
  critical: { dot: "bg-red-500", bg: "bg-red-50" },
  high: { dot: "bg-orange-500", bg: "bg-orange-50" },
  medium: { dot: "bg-yellow-500", bg: "bg-yellow-50" },
  low: { dot: "bg-blue-500", bg: "bg-blue-50" },
};

function timeAgo(dateStr: string): string {
  const now = new Date();
  const date = new Date(dateStr);
  const diff = now.getTime() - date.getTime();
  const minutes = Math.floor(diff / 60000);
  if (minutes < 1) return "Just now";
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  return `${days}d ago`;
}

interface RecentAlertsProps {
  alerts: DashboardAlert[];
}

export function RecentAlerts({ alerts }: RecentAlertsProps) {
  if (alerts.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-8 text-center">
        <div className="flex items-center justify-center w-10 h-10 rounded-lg bg-surface-main mb-3">
          <Bell className="w-5 h-5 text-text-muted" />
        </div>
        <p className="text-sm text-text-muted">No recent alerts</p>
      </div>
    );
  }

  return (
    <div className="divide-y divide-surface-card-border">
      {alerts.map((alert) => {
        const style = PRIORITY_STYLES[alert.priority] || PRIORITY_STYLES.p4;
        return (
          <Link
            key={alert.id}
            href={`/monitoring/${alert.id}`}
            className="flex items-start gap-3 px-1 py-3 group hover:bg-surface-main/50 rounded-lg transition-colors -mx-1"
          >
            <div
              className={cn(
                "flex items-center justify-center w-8 h-8 rounded-lg shrink-0 mt-0.5",
                style.bg
              )}
            >
              <span className={cn("w-2 h-2 rounded-full", style.dot)} />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-text-primary truncate group-hover:text-accent-primary transition-colors">
                {alert.title}
              </p>
              <p className="text-xs text-text-muted mt-0.5">
                {alert.vendor_name} &middot; {timeAgo(alert.created_at)}
              </p>
            </div>
            <ExternalLink className="w-3.5 h-3.5 text-text-muted opacity-0 group-hover:opacity-100 transition-opacity shrink-0 mt-1" />
          </Link>
        );
      })}
    </div>
  );
}
