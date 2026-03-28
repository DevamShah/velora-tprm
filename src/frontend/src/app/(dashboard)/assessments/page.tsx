"use client";

import React, { useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { Plus, MoreHorizontal, Eye, ClipboardCheck } from "lucide-react";
import { toast } from "sonner";
import { PageHeader } from "@/components/page-header";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { TableLoadingSkeleton } from "@/components/loading-skeleton";
import { TablePagination } from "@/components/table-pagination";
import { EmptyState } from "@/components/empty-state";
import { AssessmentStatusBadge } from "@/components/assessments/assessment-status-badge";
import { AssessmentFiltersBar } from "@/components/assessments/assessment-filters";
import { useAssessments } from "@/hooks/use-assessments";
import type { AssessmentStatus, AssessmentFilters } from "@/types/assessment";

function formatDate(dateStr: string | null): string {
  if (!dateStr) return "--";
  return new Date(dateStr).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

function formatScore(score: number | null): string {
  if (score === null || score === undefined) return "--";
  return `${Math.round(score)}%`;
}

export default function AssessmentsPage() {
  const router = useRouter();
  const [filters, setFilters] = useState<AssessmentFilters>({
    page: 1,
    page_size: 10,
    sort_by: "created_at",
    sort_order: "desc",
  });

  const { assessments, total, isLoading, error } = useAssessments(filters);

  const updateFilter = useCallback(
    <K extends keyof AssessmentFilters>(key: K, value: AssessmentFilters[K]) => {
      setFilters((prev) => ({
        ...prev,
        [key]: value,
        page: key === "page" ? (value as number) : 1,
      }));
    },
    []
  );

  const handleSort = useCallback((col: string) => {
    setFilters((prev) => ({
      ...prev,
      sort_by: col,
      sort_order:
        prev.sort_by === col && prev.sort_order === "asc" ? "desc" : "asc",
      page: 1,
    }));
  }, []);

  const totalPages = Math.ceil(total / (filters.page_size || 10));
  const currentPage = (filters.page || 1) - 1;

  if (error) {
    toast.error(error);
  }

  return (
    <>
      <PageHeader
        title="Assessments"
        description="Manage vendor risk assessments"
        actions={
          <Button onClick={() => router.push("/assessments/new")}>
            <Plus className="h-4 w-4 mr-1" />
            Create Assessment
          </Button>
        }
      />

      <div className="space-y-4">
        <AssessmentFiltersBar
          search={filters.search || ""}
          status={(filters.status as AssessmentStatus) || ""}
          onSearchChange={(v) => updateFilter("search", v)}
          onStatusChange={(v) => updateFilter("status", v)}
        />

        {isLoading ? (
          <TableLoadingSkeleton rows={5} />
        ) : assessments.length === 0 ? (
          <EmptyState
            icon={ClipboardCheck}
            title="No assessments found"
            description={
              filters.search || filters.status
                ? "Try adjusting your filters."
                : "Create your first assessment to begin evaluating vendor risk."
            }
            actionLabel={
              !filters.search && !filters.status
                ? "Create Assessment"
                : undefined
            }
            onAction={
              !filters.search && !filters.status
                ? () => router.push("/assessments/new")
                : undefined
            }
          />
        ) : (
          <div className="space-y-4">
            <div className="rounded-xl border border-surface-card-border bg-white overflow-hidden">
              <Table>
                <TableHeader>
                  <TableRow className="hover:bg-transparent">
                    <SortableHead
                      label="Title"
                      col="title"
                      current={filters.sort_by}
                      order={filters.sort_order}
                      onSort={handleSort}
                    />
                    <TableHead className="w-[160px]">Vendor</TableHead>
                    <TableHead className="w-[140px]">Template</TableHead>
                    <TableHead className="w-[130px]">Status</TableHead>
                    <TableHead className="w-[80px]">
                      <button
                        onClick={() => handleSort("score")}
                        className="flex items-center gap-1 hover:text-text-primary transition-colors"
                      >
                        Score
                        <SortIndicator
                          col="score"
                          current={filters.sort_by}
                          order={filters.sort_order}
                        />
                      </button>
                    </TableHead>
                    <SortableHead
                      label="Due Date"
                      col="due_date"
                      current={filters.sort_by}
                      order={filters.sort_order}
                      onSort={handleSort}
                    />
                    <TableHead className="w-[50px]" />
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {assessments.map((assessment) => (
                    <TableRow
                      key={assessment.id}
                      className="cursor-pointer"
                      onClick={() =>
                        router.push(`/assessments/${assessment.id}`)
                      }
                    >
                      <TableCell>
                        <span className="font-medium text-text-primary">
                          {assessment.title}
                        </span>
                      </TableCell>
                      <TableCell className="text-text-secondary text-sm">
                        {assessment.vendor_name || "--"}
                      </TableCell>
                      <TableCell className="text-text-secondary text-sm">
                        {assessment.template_name || "--"}
                      </TableCell>
                      <TableCell>
                        <AssessmentStatusBadge status={assessment.status} />
                      </TableCell>
                      <TableCell>
                        <span
                          className={`text-sm font-medium ${
                            assessment.score !== null
                              ? assessment.score >= 80
                                ? "text-emerald-600"
                                : assessment.score >= 60
                                ? "text-amber-600"
                                : "text-red-600"
                              : "text-text-muted"
                          }`}
                        >
                          {formatScore(assessment.score)}
                        </span>
                      </TableCell>
                      <TableCell className="text-text-secondary text-sm">
                        {formatDate(assessment.due_date)}
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
                                router.push(
                                  `/assessments/${assessment.id}`
                                );
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
    </>
  );
}

/* --- Sort helpers --- */

function SortIndicator({
  col,
  current,
  order,
}: {
  col: string;
  current?: string;
  order?: "asc" | "desc";
}) {
  if (col !== current)
    return (
      <span className="text-text-muted/40 text-xs ml-0.5">
        &uarr;&darr;
      </span>
    );
  return (
    <span className="text-xs ml-0.5">
      {order === "asc" ? "\u2191" : "\u2193"}
    </span>
  );
}

function SortableHead({
  label,
  col,
  current,
  order,
  onSort,
}: {
  label: string;
  col: string;
  current?: string;
  order?: "asc" | "desc";
  onSort: (col: string) => void;
}) {
  return (
    <TableHead>
      <button
        onClick={() => onSort(col)}
        className="flex items-center gap-1 hover:text-text-primary transition-colors"
      >
        {label}
        <SortIndicator col={col} current={current} order={order} />
      </button>
    </TableHead>
  );
}
