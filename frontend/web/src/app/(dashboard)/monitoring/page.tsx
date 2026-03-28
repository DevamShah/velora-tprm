"use client";

import React, { useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import {
  Activity,
  Bell,
  Search,
  X,
  Settings2,
  Eye,
  MoreHorizontal,
} from "lucide-react";
import { toast } from "sonner";
import { PageHeader } from "@/components/page-header";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { TableLoadingSkeleton } from "@/components/loading-skeleton";
import { TablePagination } from "@/components/table-pagination";
import { EmptyState } from "@/components/empty-state";
import { AlertPriorityBadge } from "@/components/monitoring/alert-priority-badge";
import { AlertStatusBadge } from "@/components/monitoring/alert-status-badge";
import { AlertRulesPanel } from "@/components/monitoring/alert-rules-panel";
import { useAlerts } from "@/hooks/use-monitoring";
import {
  ALERT_PRIORITIES,
  ALERT_STATUSES,
  ALERT_PRIORITY_LABELS,
  ALERT_STATUS_LABELS,
  ALERT_SOURCE_LABELS,
} from "@/types/monitoring";
import type {
  AlertFilters,
  AlertPriority,
  AlertStatus,
  AlertSource,
} from "@/types/monitoring";

function formatDate(dateStr: string | null): string {
  if (!dateStr) return "--";
  return new Date(dateStr).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}

function timeAgo(dateStr: string): string {
  const now = new Date();
  const date = new Date(dateStr);
  const diff = now.getTime() - date.getTime();
  const minutes = Math.floor(diff / 60000);
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  return `${days}d ago`;
}

export default function MonitoringPage() {
  const router = useRouter();
  const [filters, setFilters] = useState<AlertFilters>({
    page: 1,
    page_size: 10,
    sort_by: "created_at",
    sort_order: "desc",
  });

  const { alerts, total, isLoading, error, refetch } = useAlerts(filters);

  const updateFilter = useCallback(
    <K extends keyof AlertFilters>(key: K, value: AlertFilters[K]) => {
      setFilters((prev) => ({
        ...prev,
        [key]: value,
        page: key === "page" ? (value as number) : 1,
      }));
    },
    []
  );

  const totalPages = Math.ceil(total / (filters.page_size || 10));
  const currentPage = (filters.page || 1) - 1;
  const hasFilters =
    filters.search || filters.priority || filters.status || filters.source;

  if (error) {
    toast.error(error);
  }

  return (
    <>
      <PageHeader
        title="Monitoring"
        description="Continuous monitoring of vendor risk signals"
      />

      <Tabs defaultValue="alerts">
        <TabsList>
          <TabsTrigger value="alerts">
            <Bell className="h-3.5 w-3.5 mr-1" />
            Alerts
          </TabsTrigger>
          <TabsTrigger value="rules">
            <Settings2 className="h-3.5 w-3.5 mr-1" />
            Alert Rules
          </TabsTrigger>
        </TabsList>

        <TabsContent value="alerts" className="mt-4">
          <div className="space-y-4">
            {/* Filters */}
            <AlertFiltersBar
              filters={filters}
              onFilterChange={updateFilter}
              onClear={() =>
                setFilters({
                  page: 1,
                  page_size: 10,
                  sort_by: "created_at",
                  sort_order: "desc",
                })
              }
              hasFilters={!!hasFilters}
            />

            {isLoading ? (
              <TableLoadingSkeleton rows={5} />
            ) : alerts.length === 0 ? (
              <EmptyState
                icon={Activity}
                title="No alerts found"
                description={
                  hasFilters
                    ? "Try adjusting your filters."
                    : "No monitoring alerts yet. Configure alert rules to get started."
                }
              />
            ) : (
              <div className="space-y-4">
                <div className="rounded-xl border border-surface-card-border bg-white overflow-hidden">
                  <Table>
                    <TableHeader>
                      <TableRow className="hover:bg-transparent">
                        <TableHead className="w-[110px]">Priority</TableHead>
                        <TableHead>Alert</TableHead>
                        <TableHead className="w-[130px]">Vendor</TableHead>
                        <TableHead className="w-[110px]">Source</TableHead>
                        <TableHead className="w-[110px]">Status</TableHead>
                        <TableHead className="w-[100px]">Created</TableHead>
                        <TableHead className="w-[50px]" />
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {alerts.map((alert) => (
                        <TableRow
                          key={alert.id}
                          className="cursor-pointer"
                          onClick={() =>
                            router.push(`/monitoring/${alert.id}`)
                          }
                        >
                          <TableCell>
                            <AlertPriorityBadge priority={alert.priority} />
                          </TableCell>
                          <TableCell>
                            <div>
                              <span className="font-medium text-text-primary">
                                {alert.title}
                              </span>
                              {alert.description && (
                                <span className="block text-xs text-text-muted line-clamp-1">
                                  {alert.description}
                                </span>
                              )}
                            </div>
                          </TableCell>
                          <TableCell className="text-text-secondary text-sm">
                            {alert.vendor_name}
                          </TableCell>
                          <TableCell className="text-text-secondary text-sm">
                            {ALERT_SOURCE_LABELS[alert.source]}
                          </TableCell>
                          <TableCell>
                            <AlertStatusBadge status={alert.status} />
                          </TableCell>
                          <TableCell className="text-text-muted text-sm">
                            {timeAgo(alert.created_at)}
                          </TableCell>
                          <TableCell>
                            <DropdownMenu>
                              <DropdownMenuTrigger asChild>
                                <Button
                                  variant="ghost"
                                  size="icon"
                                  className="h-8 w-8"
                                  onClick={(e) => e.stopPropagation()}
                                >
                                  <MoreHorizontal className="h-4 w-4" />
                                </Button>
                              </DropdownMenuTrigger>
                              <DropdownMenuContent align="end">
                                <DropdownMenuItem
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    router.push(`/monitoring/${alert.id}`);
                                  }}
                                >
                                  <Eye className="h-4 w-4 mr-2" />
                                  View Details
                                </DropdownMenuItem>
                              </DropdownMenuContent>
                            </DropdownMenu>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>

                <TablePagination
                  page={currentPage}
                  totalPages={totalPages}
                  pageSize={filters.page_size || 10}
                  totalItems={total}
                  onPageChange={(p) => updateFilter("page", p + 1)}
                  onPageSizeChange={(size) =>
                    setFilters((prev) => ({
                      ...prev,
                      page_size: size,
                      page: 1,
                    }))
                  }
                />
              </div>
            )}
          </div>
        </TabsContent>

        <TabsContent value="rules" className="mt-4">
          <AlertRulesPanel />
        </TabsContent>
      </Tabs>
    </>
  );
}

/* --- Alert Filters Bar --- */

function AlertFiltersBar({
  filters,
  onFilterChange,
  onClear,
  hasFilters,
}: {
  filters: AlertFilters;
  onFilterChange: <K extends keyof AlertFilters>(
    key: K,
    value: AlertFilters[K]
  ) => void;
  onClear: () => void;
  hasFilters: boolean;
}) {
  const [localSearch, setLocalSearch] = React.useState(filters.search || "");

  React.useEffect(() => {
    const timer = setTimeout(() => onFilterChange("search", localSearch), 300);
    return () => clearTimeout(timer);
  }, [localSearch, onFilterChange]);

  React.useEffect(() => {
    setLocalSearch(filters.search || "");
  }, [filters.search]);

  return (
    <div className="flex flex-wrap items-center gap-3">
      <div className="relative flex-1 min-w-[200px] max-w-sm">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-text-muted" />
        <Input
          placeholder="Search alerts..."
          value={localSearch}
          onChange={(e) => setLocalSearch(e.target.value)}
          className="pl-9"
        />
      </div>
      <Select
        value={filters.priority || "all"}
        onValueChange={(v) =>
          onFilterChange(
            "priority",
            v === "all" ? "" : (v as AlertPriority)
          )
        }
      >
        <SelectTrigger className="w-[150px]">
          <SelectValue placeholder="All Priorities" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">All Priorities</SelectItem>
          {ALERT_PRIORITIES.map((p) => (
            <SelectItem key={p} value={p}>
              {ALERT_PRIORITY_LABELS[p]}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
      <Select
        value={filters.status || "all"}
        onValueChange={(v) =>
          onFilterChange(
            "status",
            v === "all" ? "" : (v as AlertStatus)
          )
        }
      >
        <SelectTrigger className="w-[150px]">
          <SelectValue placeholder="All Statuses" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">All Statuses</SelectItem>
          {ALERT_STATUSES.map((s) => (
            <SelectItem key={s} value={s}>
              {ALERT_STATUS_LABELS[s]}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
      {hasFilters && (
        <Button variant="ghost" size="sm" onClick={onClear}>
          <X className="h-3 w-3 mr-1" />
          Clear
        </Button>
      )}
    </div>
  );
}
