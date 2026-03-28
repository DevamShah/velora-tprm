"use client";

import React, { useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import {
  AlertTriangle,
  Plus,
  Search,
  X,
  Eye,
  MoreHorizontal,
  Clock,
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
import { TableLoadingSkeleton } from "@/components/loading-skeleton";
import { TablePagination } from "@/components/table-pagination";
import { EmptyState } from "@/components/empty-state";
import { FindingSeverityBadge } from "@/components/findings/finding-severity-badge";
import { FindingStatusBadge } from "@/components/findings/finding-status-badge";
import { useFindings } from "@/hooks/use-findings";
import {
  FINDING_SEVERITIES,
  FINDING_STATUSES,
  FINDING_SEVERITY_LABELS,
  FINDING_STATUS_LABELS,
} from "@/types/finding";
import type { FindingFilters, FindingSeverity, FindingStatus } from "@/types/finding";

function formatDate(dateStr: string | null): string {
  if (!dateStr) return "--";
  return new Date(dateStr).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

function slaCountdown(slaDueDate: string | null): {
  label: string;
  urgent: boolean;
} {
  if (!slaDueDate) return { label: "--", urgent: false };
  const now = new Date();
  const due = new Date(slaDueDate);
  const diff = due.getTime() - now.getTime();
  const days = Math.ceil(diff / (1000 * 60 * 60 * 24));
  if (days < 0) return { label: `${Math.abs(days)}d overdue`, urgent: true };
  if (days === 0) return { label: "Due today", urgent: true };
  if (days <= 3) return { label: `${days}d left`, urgent: true };
  return { label: `${days}d left`, urgent: false };
}

export default function FindingsPage() {
  const router = useRouter();
  const [filters, setFilters] = useState<FindingFilters>({
    page: 1,
    page_size: 10,
    sort_by: "created_at",
    sort_order: "desc",
  });

  const { findings, total, isLoading, error, refetch } = useFindings(filters);

  const updateFilter = useCallback(
    <K extends keyof FindingFilters>(key: K, value: FindingFilters[K]) => {
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
  const hasFilters = filters.search || filters.severity || filters.status;

  if (error) {
    toast.error(error);
  }

  return (
    <>
      <PageHeader
        title="Findings"
        description="Track and remediate identified risks"
      />

      <div className="space-y-4">
        {/* Filters */}
        <FindingsFiltersBar
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
        ) : findings.length === 0 ? (
          <EmptyState
            icon={AlertTriangle}
            title="No findings found"
            description={
              hasFilters
                ? "Try adjusting your filters."
                : "Findings will appear here as assessments are completed."
            }
          />
        ) : (
          <div className="space-y-4">
            <div className="rounded-xl border border-surface-card-border bg-white overflow-hidden">
              <Table>
                <TableHeader>
                  <TableRow className="hover:bg-transparent">
                    <TableHead className="w-[100px]">Severity</TableHead>
                    <TableHead>Finding</TableHead>
                    <TableHead className="w-[140px]">Vendor</TableHead>
                    <TableHead className="w-[110px]">Status</TableHead>
                    <TableHead className="w-[110px]">SLA</TableHead>
                    <TableHead className="w-[110px]">Created</TableHead>
                    <TableHead className="w-[50px]" />
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {findings.map((finding) => {
                    const sla = slaCountdown(finding.sla_due_date);
                    return (
                      <TableRow
                        key={finding.id}
                        className="cursor-pointer"
                        onClick={() => router.push(`/findings/${finding.id}`)}
                      >
                        <TableCell>
                          <FindingSeverityBadge severity={finding.severity} />
                        </TableCell>
                        <TableCell>
                          <div>
                            <span className="font-medium text-text-primary">
                              {finding.title}
                            </span>
                            {finding.description && (
                              <span className="block text-xs text-text-muted line-clamp-1">
                                {finding.description}
                              </span>
                            )}
                          </div>
                        </TableCell>
                        <TableCell className="text-text-secondary text-sm">
                          {finding.vendor_name}
                        </TableCell>
                        <TableCell>
                          <FindingStatusBadge status={finding.status} />
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center gap-1">
                            {sla.urgent && (
                              <Clock className="w-3.5 h-3.5 text-risk-critical" />
                            )}
                            <span
                              className={`text-sm ${
                                sla.urgent
                                  ? "text-risk-critical font-medium"
                                  : "text-text-muted"
                              }`}
                            >
                              {sla.label}
                            </span>
                          </div>
                        </TableCell>
                        <TableCell className="text-text-secondary text-sm">
                          {formatDate(finding.created_at)}
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
                                  router.push(`/findings/${finding.id}`);
                                }}
                              >
                                <Eye className="h-4 w-4 mr-2" />
                                View Details
                              </DropdownMenuItem>
                            </DropdownMenuContent>
                          </DropdownMenu>
                        </TableCell>
                      </TableRow>
                    );
                  })}
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
                setFilters((prev) => ({ ...prev, page_size: size, page: 1 }))
              }
            />
          </div>
        )}
      </div>
    </>
  );
}

/* --- Filters Bar --- */

function FindingsFiltersBar({
  filters,
  onFilterChange,
  onClear,
  hasFilters,
}: {
  filters: FindingFilters;
  onFilterChange: <K extends keyof FindingFilters>(
    key: K,
    value: FindingFilters[K]
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
          placeholder="Search findings..."
          value={localSearch}
          onChange={(e) => setLocalSearch(e.target.value)}
          className="pl-9"
        />
      </div>
      <Select
        value={filters.severity || "all"}
        onValueChange={(v) =>
          onFilterChange(
            "severity",
            v === "all" ? "" : (v as FindingSeverity)
          )
        }
      >
        <SelectTrigger className="w-[150px]">
          <SelectValue placeholder="All Severities" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">All Severities</SelectItem>
          {FINDING_SEVERITIES.map((s) => (
            <SelectItem key={s} value={s}>
              {FINDING_SEVERITY_LABELS[s]}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
      <Select
        value={filters.status || "all"}
        onValueChange={(v) =>
          onFilterChange(
            "status",
            v === "all" ? "" : (v as FindingStatus)
          )
        }
      >
        <SelectTrigger className="w-[150px]">
          <SelectValue placeholder="All Statuses" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">All Statuses</SelectItem>
          {FINDING_STATUSES.map((s) => (
            <SelectItem key={s} value={s}>
              {FINDING_STATUS_LABELS[s]}
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
