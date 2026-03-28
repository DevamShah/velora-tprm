"use client";

import React, { useState, useCallback } from "react";
import { Upload, FileCheck, MoreHorizontal, Eye, Trash2, Search, X } from "lucide-react";
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
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { TableLoadingSkeleton } from "@/components/loading-skeleton";
import { TablePagination } from "@/components/table-pagination";
import { EmptyState } from "@/components/empty-state";
import { UploadDialog } from "@/components/evidence/upload-dialog";
import { EvidenceDetailDrawer } from "@/components/evidence/evidence-detail-drawer";
import { useEvidenceList, useDeleteEvidence } from "@/hooks/use-evidence";
import {
  EVIDENCE_STATUSES,
  EVIDENCE_TYPES,
  EVIDENCE_TYPE_LABELS,
  EVIDENCE_STATUS_LABELS,
} from "@/types/evidence";
import type {
  EvidenceFilters,
  EvidenceStatus,
  EvidenceType,
  Evidence,
} from "@/types/evidence";

const STATUS_VARIANT: Record<EvidenceStatus, "default" | "secondary" | "outline" | "low" | "critical"> = {
  pending: "outline",
  processing: "default",
  processed: "low",
  failed: "critical",
  archived: "secondary",
};

function formatDate(dateStr: string | null): string {
  if (!dateStr) return "--";
  return new Date(dateStr).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export default function EvidencePage() {
  const [filters, setFilters] = useState<EvidenceFilters>({
    page: 1,
    page_size: 10,
    sort_by: "created_at",
    sort_order: "desc",
  });
  const [uploadOpen, setUploadOpen] = useState(false);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [drawerOpen, setDrawerOpen] = useState(false);

  const { evidence, total, isLoading, error, refetch } = useEvidenceList(filters);
  const { deleteEvidence } = useDeleteEvidence();

  const updateFilter = useCallback(
    <K extends keyof EvidenceFilters>(key: K, value: EvidenceFilters[K]) => {
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

  async function handleDelete(item: Evidence) {
    try {
      await deleteEvidence(item.id);
      toast.success(`Deleted ${item.filename}`);
      refetch();
    } catch (err) {
      toast.error((err as { message?: string }).message || "Delete failed");
    }
  }

  function openDetail(id: string) {
    setSelectedId(id);
    setDrawerOpen(true);
  }

  const totalPages = Math.ceil(total / (filters.page_size || 10));
  const currentPage = (filters.page || 1) - 1;
  const hasFilters = filters.search || filters.status || filters.document_type;

  if (error) {
    toast.error(error);
  }

  return (
    <>
      <PageHeader
        title="Evidence"
        description="Manage evidence artifacts and documentation"
        actions={
          <Button onClick={() => setUploadOpen(true)}>
            <Upload className="h-4 w-4 mr-1" />
            Upload Evidence
          </Button>
        }
      />

      <div className="space-y-4">
        {/* Filters */}
        <EvidenceFiltersBar
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
        ) : evidence.length === 0 ? (
          <EmptyState
            icon={FileCheck}
            title="No evidence found"
            description={
              hasFilters
                ? "Try adjusting your filters."
                : "Upload your first evidence document to get started."
            }
            actionLabel={!hasFilters ? "Upload Evidence" : undefined}
            onAction={!hasFilters ? () => setUploadOpen(true) : undefined}
          />
        ) : (
          <div className="space-y-4">
            <div className="rounded-xl border border-surface-card-border bg-white overflow-hidden">
              <Table>
                <TableHeader>
                  <TableRow className="hover:bg-transparent">
                    <SortableHead
                      label="Filename"
                      col="filename"
                      current={filters.sort_by}
                      order={filters.sort_order}
                      onSort={handleSort}
                    />
                    <TableHead className="w-[140px]">Type</TableHead>
                    <TableHead className="w-[120px]">Vendor</TableHead>
                    <TableHead className="w-[100px]">Status</TableHead>
                    <TableHead className="w-[80px]">Size</TableHead>
                    <TableHead className="w-[90px]">Extractions</TableHead>
                    <SortableHead
                      label="Uploaded"
                      col="created_at"
                      current={filters.sort_by}
                      order={filters.sort_order}
                      onSort={handleSort}
                    />
                    <TableHead className="w-[50px]" />
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {evidence.map((item) => (
                    <TableRow
                      key={item.id}
                      className="cursor-pointer"
                      onClick={() => openDetail(item.id)}
                    >
                      <TableCell>
                        <span className="font-medium text-text-primary">
                          {item.filename}
                        </span>
                      </TableCell>
                      <TableCell className="text-text-secondary text-sm">
                        {EVIDENCE_TYPE_LABELS[item.document_type as EvidenceType] ||
                          item.document_type}
                      </TableCell>
                      <TableCell className="text-text-secondary text-sm">
                        {item.vendor_name}
                      </TableCell>
                      <TableCell>
                        <Badge variant={STATUS_VARIANT[item.status]}>
                          {EVIDENCE_STATUS_LABELS[item.status]}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-text-muted text-sm">
                        {formatFileSize(item.file_size)}
                      </TableCell>
                      <TableCell className="text-text-secondary text-sm">
                        {item.extraction_count}
                      </TableCell>
                      <TableCell className="text-text-secondary text-sm">
                        {formatDate(item.created_at)}
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
                                openDetail(item.id);
                              }}
                            >
                              <Eye className="h-4 w-4 mr-2" />
                              View Details
                            </DropdownMenuItem>
                            <DropdownMenuItem
                              onClick={(e) => {
                                e.stopPropagation();
                                handleDelete(item);
                              }}
                              className="text-risk-critical focus:text-risk-critical"
                            >
                              <Trash2 className="h-4 w-4 mr-2" />
                              Delete
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
                setFilters((prev) => ({ ...prev, page_size: size, page: 1 }))
              }
            />
          </div>
        )}
      </div>

      <UploadDialog
        open={uploadOpen}
        onOpenChange={setUploadOpen}
        onSuccess={refetch}
      />

      <EvidenceDetailDrawer
        evidenceId={selectedId}
        open={drawerOpen}
        onClose={() => {
          setDrawerOpen(false);
          setSelectedId(null);
        }}
        onMappingUpdated={refetch}
      />
    </>
  );
}

/* --- Filters Bar --- */

function EvidenceFiltersBar({
  filters,
  onFilterChange,
  onClear,
  hasFilters,
}: {
  filters: EvidenceFilters;
  onFilterChange: <K extends keyof EvidenceFilters>(
    key: K,
    value: EvidenceFilters[K]
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
          placeholder="Search evidence..."
          value={localSearch}
          onChange={(e) => setLocalSearch(e.target.value)}
          className="pl-9"
        />
      </div>
      <Select
        value={filters.status || "all"}
        onValueChange={(v) =>
          onFilterChange("status", v === "all" ? "" : (v as EvidenceStatus))
        }
      >
        <SelectTrigger className="w-[160px]">
          <SelectValue placeholder="All Statuses" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">All Statuses</SelectItem>
          {EVIDENCE_STATUSES.map((s) => (
            <SelectItem key={s} value={s}>
              {EVIDENCE_STATUS_LABELS[s]}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
      <Select
        value={filters.document_type || "all"}
        onValueChange={(v) =>
          onFilterChange("document_type", v === "all" ? "" : (v as EvidenceType))
        }
      >
        <SelectTrigger className="w-[180px]">
          <SelectValue placeholder="All Types" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">All Types</SelectItem>
          {EVIDENCE_TYPES.map((t) => (
            <SelectItem key={t} value={t}>
              {EVIDENCE_TYPE_LABELS[t]}
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

/* --- Sort Helpers --- */

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
      <span className="text-text-muted/40 text-xs ml-0.5">&uarr;&darr;</span>
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
