"use client";

import React, { useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { Plus, Upload, MoreHorizontal, Eye, Pencil, Trash2, Building2 } from "lucide-react";
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
import { VendorTierBadge } from "@/components/vendors/vendor-tier-badge";
import { VendorStatusBadge } from "@/components/vendors/vendor-status-badge";
import { VendorRiskScore } from "@/components/vendors/vendor-risk-score";
import { VendorFiltersBar } from "@/components/vendors/vendor-filters";
import { BulkImportDialog } from "@/components/vendors/bulk-import-dialog";
import { DeleteVendorDialog } from "@/components/vendors/delete-vendor-dialog";
import { useVendors } from "@/hooks/use-vendors";
import type { Vendor, VendorStatus, VendorTier, VendorFilters } from "@/types/vendor";

function formatDate(dateStr: string | null): string {
  if (!dateStr) return "--";
  return new Date(dateStr).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

export default function VendorsPage() {
  const router = useRouter();
  const [filters, setFilters] = useState<VendorFilters>({
    page: 1,
    page_size: 10,
    sort_by: "name",
    sort_order: "asc",
  });
  const [importOpen, setImportOpen] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState<Vendor | null>(null);

  const { vendors, total, isLoading, error, refetch } = useVendors(filters);

  const updateFilter = useCallback(
    <K extends keyof VendorFilters>(key: K, value: VendorFilters[K]) => {
      setFilters((prev) => ({
        ...prev,
        [key]: value,
        page: key === "page" ? (value as number) : 1,
      }));
    },
    []
  );

  const handleSort = useCallback(
    (col: string) => {
      setFilters((prev) => ({
        ...prev,
        sort_by: col,
        sort_order:
          prev.sort_by === col && prev.sort_order === "asc" ? "desc" : "asc",
        page: 1,
      }));
    },
    []
  );

  const totalPages = Math.ceil(total / (filters.page_size || 10));
  const currentPage = (filters.page || 1) - 1;

  if (error) {
    toast.error(error);
  }

  return (
    <>
      <PageHeader
        title="Vendors"
        description="Manage your third-party vendor portfolio"
        actions={
          <div className="flex items-center gap-2">
            <Button variant="outline" onClick={() => setImportOpen(true)}>
              <Upload className="h-4 w-4 mr-1" />
              Bulk Import
            </Button>
            <Button onClick={() => router.push("/vendors/new")}>
              <Plus className="h-4 w-4 mr-1" />
              Add Vendor
            </Button>
          </div>
        }
      />

      <div className="space-y-4">
        <VendorFiltersBar
          search={filters.search || ""}
          status={(filters.status as VendorStatus) || ""}
          tier={(filters.tier as VendorTier) || ""}
          onSearchChange={(v) => updateFilter("search", v)}
          onStatusChange={(v) => updateFilter("status", v)}
          onTierChange={(v) => updateFilter("tier", v)}
        />

        {isLoading ? (
          <TableLoadingSkeleton rows={5} />
        ) : vendors.length === 0 ? (
          <EmptyState
            icon={Building2}
            title="No vendors found"
            description={
              filters.search || filters.status || filters.tier
                ? "Try adjusting your filters."
                : "Add your first vendor to begin tracking third-party risk."
            }
            actionLabel={!filters.search && !filters.status && !filters.tier ? "Add Vendor" : undefined}
            onAction={
              !filters.search && !filters.status && !filters.tier
                ? () => router.push("/vendors/new")
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
                      label="Name"
                      col="name"
                      current={filters.sort_by}
                      order={filters.sort_order}
                      onSort={handleSort}
                    />
                    <TableHead className="w-[100px]">Tier</TableHead>
                    <TableHead className="w-[110px]">Status</TableHead>
                    <TableHead className="w-[100px]">
                      <button
                        onClick={() => handleSort("inherent_risk_score")}
                        className="flex items-center gap-1 hover:text-text-primary transition-colors"
                      >
                        Risk
                        <SortIndicator col="inherent_risk_score" current={filters.sort_by} order={filters.sort_order} />
                      </button>
                    </TableHead>
                    <SortableHead
                      label="Industry"
                      col="industry"
                      current={filters.sort_by}
                      order={filters.sort_order}
                      onSort={handleSort}
                    />
                    <SortableHead
                      label="Updated"
                      col="updated_at"
                      current={filters.sort_by}
                      order={filters.sort_order}
                      onSort={handleSort}
                    />
                    <TableHead className="w-[50px]" />
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {vendors.map((vendor) => (
                    <TableRow
                      key={vendor.id}
                      className="cursor-pointer"
                      onClick={() => router.push(`/vendors/${vendor.id}`)}
                    >
                      <TableCell>
                        <div>
                          <span className="font-medium text-text-primary">
                            {vendor.name}
                          </span>
                          {vendor.domain && (
                            <span className="block text-xs text-text-muted">
                              {vendor.domain}
                            </span>
                          )}
                        </div>
                      </TableCell>
                      <TableCell>
                        <VendorTierBadge tier={vendor.tier} />
                      </TableCell>
                      <TableCell>
                        <VendorStatusBadge status={vendor.status} />
                      </TableCell>
                      <TableCell>
                        <VendorRiskScore score={vendor.inherent_risk_score} />
                      </TableCell>
                      <TableCell className="text-text-secondary text-sm">
                        {vendor.industry || "--"}
                      </TableCell>
                      <TableCell className="text-text-secondary text-sm">
                        {formatDate(vendor.updated_at)}
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
                                router.push(`/vendors/${vendor.id}`);
                              }}
                            >
                              <Eye className="h-4 w-4 mr-2" />
                              View
                            </DropdownMenuItem>
                            <DropdownMenuItem
                              onClick={(e) => {
                                e.stopPropagation();
                                router.push(`/vendors/${vendor.id}`);
                              }}
                            >
                              <Pencil className="h-4 w-4 mr-2" />
                              Edit
                            </DropdownMenuItem>
                            <DropdownMenuItem
                              onClick={(e) => {
                                e.stopPropagation();
                                setDeleteTarget(vendor);
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

      <BulkImportDialog
        open={importOpen}
        onOpenChange={setImportOpen}
        onSuccess={refetch}
      />

      {deleteTarget && (
        <DeleteVendorDialog
          open={!!deleteTarget}
          onOpenChange={(v) => { if (!v) setDeleteTarget(null); }}
          vendorId={deleteTarget.id}
          vendorName={deleteTarget.name}
          onDeleted={() => {
            setDeleteTarget(null);
            refetch();
          }}
        />
      )}
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
  if (col !== current) return <span className="text-text-muted/40 text-xs ml-0.5">&uarr;&darr;</span>;
  return <span className="text-xs ml-0.5">{order === "asc" ? "\u2191" : "\u2193"}</span>;
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
