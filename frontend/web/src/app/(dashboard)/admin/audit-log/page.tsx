"use client";

import React, { useState, useCallback } from "react";
import { ScrollText, Search, X, Download } from "lucide-react";
import { toast } from "sonner";
import { PageHeader } from "@/components/page-header";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
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
import { TableLoadingSkeleton } from "@/components/loading-skeleton";
import { TablePagination } from "@/components/table-pagination";
import { EmptyState } from "@/components/empty-state";
import { useAuditLogs } from "@/hooks/use-admin";
import {
  AUDIT_ACTIONS,
  AUDIT_ACTION_LABELS,
} from "@/types/admin";
import type { AuditLogFilters, AuditAction } from "@/types/admin";

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "numeric",
    minute: "2-digit",
    second: "2-digit",
  });
}

const ACTION_STYLES: Record<string, string> = {
  create: "bg-green-50 text-green-700",
  update: "bg-blue-50 text-blue-700",
  delete: "bg-red-50 text-red-700",
  login: "bg-purple-50 text-purple-700",
  logout: "bg-gray-100 text-gray-600",
  export: "bg-amber-50 text-amber-700",
  invite: "bg-indigo-50 text-indigo-700",
  role_change: "bg-orange-50 text-orange-700",
  settings_change: "bg-teal-50 text-teal-700",
};

export default function AuditLogPage() {
  const [filters, setFilters] = useState<AuditLogFilters>({
    page: 1,
    page_size: 25,
  });

  const { logs, total, isLoading, error } = useAuditLogs(filters);

  const updateFilter = useCallback(
    <K extends keyof AuditLogFilters>(key: K, value: AuditLogFilters[K]) => {
      setFilters((prev) => ({
        ...prev,
        [key]: value,
        page: key === "page" ? (value as number) : 1,
      }));
    },
    []
  );

  const totalPages = Math.ceil(total / (filters.page_size || 25));
  const currentPage = (filters.page || 1) - 1;
  const hasFilters =
    filters.search || filters.action || filters.date_from || filters.date_to;

  if (error) {
    toast.error(error);
  }

  const handleExport = () => {
    toast.info("Export functionality will download a CSV of the current view");
  };

  return (
    <>
      <PageHeader
        title="Audit Log"
        description="Review all platform activity and changes"
        actions={
          <Button variant="outline" onClick={handleExport}>
            <Download className="h-4 w-4 mr-1" />
            Export CSV
          </Button>
        }
      />

      <div className="space-y-4">
        {/* Filters */}
        <AuditFiltersBar
          filters={filters}
          onFilterChange={updateFilter}
          onClear={() => setFilters({ page: 1, page_size: 25 })}
          hasFilters={!!hasFilters}
        />

        {isLoading ? (
          <TableLoadingSkeleton rows={10} />
        ) : logs.length === 0 ? (
          <EmptyState
            icon={ScrollText}
            title="No audit entries"
            description={
              hasFilters
                ? "Try adjusting your filters."
                : "Audit events will be recorded as users interact with the platform."
            }
          />
        ) : (
          <div className="space-y-4">
            <div className="rounded-xl border border-surface-card-border bg-white overflow-hidden">
              <Table>
                <TableHeader>
                  <TableRow className="hover:bg-transparent">
                    <TableHead className="w-[170px]">Timestamp</TableHead>
                    <TableHead className="w-[150px]">User</TableHead>
                    <TableHead className="w-[120px]">Action</TableHead>
                    <TableHead className="w-[120px]">Resource</TableHead>
                    <TableHead>Details</TableHead>
                    <TableHead className="w-[110px]">IP Address</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {logs.map((entry) => (
                    <TableRow key={entry.id}>
                      <TableCell className="text-text-muted text-xs font-mono">
                        {formatDate(entry.created_at)}
                      </TableCell>
                      <TableCell>
                        <div>
                          <span className="text-sm font-medium text-text-primary">
                            {entry.user_name}
                          </span>
                          <span className="block text-xs text-text-muted">
                            {entry.user_email}
                          </span>
                        </div>
                      </TableCell>
                      <TableCell>
                        <span
                          className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${
                            ACTION_STYLES[entry.action] ||
                            "bg-gray-100 text-gray-600"
                          }`}
                        >
                          {AUDIT_ACTION_LABELS[entry.action] || entry.action}
                        </span>
                      </TableCell>
                      <TableCell className="text-text-secondary text-sm">
                        <Badge variant="outline" className="text-[10px]">
                          {entry.resource_type}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-text-secondary text-sm truncate max-w-[200px]">
                        {typeof entry.details === "string"
                          ? entry.details
                          : entry.details
                            ? JSON.stringify(entry.details)
                            : "--"}
                      </TableCell>
                      <TableCell className="text-text-muted text-xs font-mono">
                        {entry.ip_address || "--"}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>

            <TablePagination
              page={currentPage}
              totalPages={totalPages}
              pageSize={filters.page_size || 25}
              totalItems={total}
              onPageChange={(p) => updateFilter("page", p + 1)}
              onPageSizeChange={(size) =>
                setFilters((prev) => ({ ...prev, page_size: size, page: 1 }))
              }
            />
          </div>
        )}
      </div>
    </>
  );
}

/* --- Audit Filters Bar --- */

function AuditFiltersBar({
  filters,
  onFilterChange,
  onClear,
  hasFilters,
}: {
  filters: AuditLogFilters;
  onFilterChange: <K extends keyof AuditLogFilters>(
    key: K,
    value: AuditLogFilters[K]
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
          placeholder="Search audit log..."
          value={localSearch}
          onChange={(e) => setLocalSearch(e.target.value)}
          className="pl-9"
        />
      </div>
      <Select
        value={filters.action || "all"}
        onValueChange={(v) =>
          onFilterChange(
            "action",
            v === "all" ? "" : (v as AuditAction)
          )
        }
      >
        <SelectTrigger className="w-[160px]">
          <SelectValue placeholder="All Actions" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">All Actions</SelectItem>
          {AUDIT_ACTIONS.map((a) => (
            <SelectItem key={a} value={a}>
              {AUDIT_ACTION_LABELS[a]}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
      <Input
        type="date"
        placeholder="From"
        value={filters.date_from || ""}
        onChange={(e) => onFilterChange("date_from", e.target.value)}
        className="w-[150px]"
      />
      <Input
        type="date"
        placeholder="To"
        value={filters.date_to || ""}
        onChange={(e) => onFilterChange("date_to", e.target.value)}
        className="w-[150px]"
      />
      {hasFilters && (
        <Button variant="ghost" size="sm" onClick={onClear}>
          <X className="h-3 w-3 mr-1" />
          Clear
        </Button>
      )}
    </div>
  );
}
