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
import { ASSESSMENT_STATUSES } from "@/types/assessment";
import type { AssessmentStatus } from "@/types/assessment";

const STATUS_LABEL: Record<AssessmentStatus, string> = {
  draft: "Draft",
  distributed: "Distributed",
  in_progress: "In Progress",
  submitted: "Submitted",
  under_review: "Under Review",
  completed: "Completed",
  cancelled: "Cancelled",
};

interface AssessmentFiltersBarProps {
  search: string;
  status: AssessmentStatus | "";
  onSearchChange: (value: string) => void;
  onStatusChange: (value: AssessmentStatus | "") => void;
}

export function AssessmentFiltersBar({
  search,
  status,
  onSearchChange,
  onStatusChange,
}: AssessmentFiltersBarProps) {
  const [localSearch, setLocalSearch] = useState(search);

  useEffect(() => {
    const timer = setTimeout(() => onSearchChange(localSearch), 300);
    return () => clearTimeout(timer);
  }, [localSearch, onSearchChange]);

  useEffect(() => {
    setLocalSearch(search);
  }, [search]);

  const hasFilters = search || status;

  function clearAll() {
    setLocalSearch("");
    onSearchChange("");
    onStatusChange("");
  }

  return (
    <div className="flex flex-wrap items-center gap-3">
      <div className="relative flex-1 min-w-[200px] max-w-sm">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-text-muted" />
        <Input
          placeholder="Search assessments..."
          value={localSearch}
          onChange={(e) => setLocalSearch(e.target.value)}
          className="pl-9"
        />
      </div>
      <Select
        value={status || "all"}
        onValueChange={(v) => onStatusChange(v === "all" ? "" : (v as AssessmentStatus))}
      >
        <SelectTrigger className="w-[180px]">
          <SelectValue placeholder="All Statuses" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">All Statuses</SelectItem>
          {ASSESSMENT_STATUSES.map((s) => (
            <SelectItem key={s} value={s}>
              {STATUS_LABEL[s]}
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
