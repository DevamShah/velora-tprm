"use client";

import React, { useState, useEffect } from "react";
import { Search, X } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { VENDOR_STATUSES, VENDOR_TIERS } from "@/types/vendor";
import type { VendorStatus, VendorTier } from "@/types/vendor";

interface VendorFiltersProps {
  search: string;
  status: VendorStatus | "";
  tier: VendorTier | "";
  onSearchChange: (value: string) => void;
  onStatusChange: (value: VendorStatus | "") => void;
  onTierChange: (value: VendorTier | "") => void;
}

function capitalize(s: string): string {
  return s.charAt(0).toUpperCase() + s.slice(1);
}

export function VendorFiltersBar({
  search,
  status,
  tier,
  onSearchChange,
  onStatusChange,
  onTierChange,
}: VendorFiltersProps) {
  const [localSearch, setLocalSearch] = useState(search);

  useEffect(() => {
    const timer = setTimeout(() => onSearchChange(localSearch), 300);
    return () => clearTimeout(timer);
  }, [localSearch, onSearchChange]);

  useEffect(() => {
    setLocalSearch(search);
  }, [search]);

  const hasFilters = search || status || tier;

  function clearAll() {
    setLocalSearch("");
    onSearchChange("");
    onStatusChange("");
    onTierChange("");
  }

  return (
    <div className="flex flex-wrap items-center gap-3">
      <div className="relative flex-1 min-w-[200px] max-w-sm">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-text-muted" />
        <Input
          placeholder="Search vendors..."
          value={localSearch}
          onChange={(e) => setLocalSearch(e.target.value)}
          className="pl-9"
        />
      </div>
      <Select
        value={status || "all"}
        onValueChange={(v) => onStatusChange(v === "all" ? "" : (v as VendorStatus))}
      >
        <SelectTrigger className="w-[160px]">
          <SelectValue placeholder="All Statuses" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">All Statuses</SelectItem>
          {VENDOR_STATUSES.map((s) => (
            <SelectItem key={s} value={s}>
              {capitalize(s)}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
      <Select
        value={tier || "all"}
        onValueChange={(v) => onTierChange(v === "all" ? "" : (v as VendorTier))}
      >
        <SelectTrigger className="w-[160px]">
          <SelectValue placeholder="All Tiers" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">All Tiers</SelectItem>
          {VENDOR_TIERS.map((t) => (
            <SelectItem key={t} value={t}>
              {capitalize(t)}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
      {hasFilters && (
        <Button variant="ghost" size="sm" onClick={clearAll}>
          <X className="h-3 w-3 mr-1" />
          Clear
        </Button>
      )}
    </div>
  );
}
