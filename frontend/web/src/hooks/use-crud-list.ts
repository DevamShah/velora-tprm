"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import { api, type ApiError } from "@/lib/api";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

/** Standard paginated response shape returned by all list endpoints. */
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  [key: string]: unknown; // allows extra fields (e.g. unread_count)
}

/** Base filter shape shared by every list hook. */
export interface BaseFilters {
  search?: string;
  sort_by?: string;
  sort_order?: "asc" | "desc";
  page?: number;
  page_size?: number;
  [key: string]: string | number | undefined;
}

/** Return value of useCrudList. */
export interface CrudListResult<T> {
  items: T[];
  total: number;
  isLoading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
}

/** Return value of useCrudDetail. */
export interface CrudDetailResult<T> {
  data: T | null;
  isLoading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
}

/** Return value of useCrudMutation. */
export interface CrudMutationResult<TArgs extends unknown[], TReturn> {
  mutate: (...args: TArgs) => Promise<TReturn>;
  isLoading: boolean;
}

/** Options for useCrudList. */
export interface CrudListOptions {
  /** Human-readable entity name used in fallback error messages (e.g. "vendors"). */
  entityName?: string;
  /** Set to false to skip initial fetch (useful for conditional fetching). */
  enabled?: boolean;
}

// ---------------------------------------------------------------------------
// Utilities
// ---------------------------------------------------------------------------

/**
 * Convert a filters object into the Record<string, string> that api.get expects.
 *
 * Handles the generic case: skips undefined/empty values and converts numbers
 * to strings. This replaces all the per-hook `buildParams` functions which
 * are currently copy-pasted across use-vendors, use-assessments, use-findings,
 * use-monitoring, use-evidence, etc.
 */
export function buildFilterParams(
  filters: Record<string, string | number | undefined>
): Record<string, string> {
  const params: Record<string, string> = {};
  for (const [key, value] of Object.entries(filters)) {
    if (value === undefined || value === null || value === "") continue;
    params[key] = typeof value === "number" ? String(value) : value;
  }
  return params;
}

// ---------------------------------------------------------------------------
// useCrudList — replaces the duplicated list-fetch pattern
// ---------------------------------------------------------------------------

/**
 * Generic hook for fetching a paginated list from any API endpoint.
 *
 * Replaces the identical useState/useCallback/useEffect pattern found in:
 *   - useVendors (use-vendors.ts)
 *   - useAssessments (use-assessments.ts)
 *   - useFindings (use-findings.ts)
 *   - useAlerts (use-monitoring.ts)
 *   - useEvidenceList (use-evidence.ts)
 *   - useNotifications, useCommunicationLogs (use-communications.ts)
 *   - useReviewQueue (use-assessments.ts)
 *
 * Usage:
 * ```ts
 * const { items, total, isLoading, error, refetch } = useCrudList<Vendor>(
 *   "/vendors",
 *   filters,
 *   { entityName: "vendors" }
 * );
 * ```
 */
export function useCrudList<T>(
  endpoint: string,
  filters: BaseFilters = {},
  options: CrudListOptions = {}
): CrudListResult<T> {
  const { entityName = "items", enabled = true } = options;

  const [items, setItems] = useState<T[]>([]);
  const [total, setTotal] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Serialize filters to a stable string for the dependency array so that
  // consumers don't need to memoize their filter objects.
  const filterJson = JSON.stringify(filters);

  const fetchData = useCallback(async () => {
    if (!enabled) return;
    setIsLoading(true);
    setError(null);
    try {
      const params = buildFilterParams(JSON.parse(filterJson));
      const res = await api.get<PaginatedResponse<T>>(endpoint, params);
      setItems(res.items ?? []);
      setTotal(res.total ?? 0);
    } catch (err) {
      const apiErr = err as ApiError;
      setError(apiErr.message || `Failed to load ${entityName}`);
    } finally {
      setIsLoading(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [endpoint, filterJson, entityName, enabled]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return { items, total, isLoading, error, refetch: fetchData };
}

// ---------------------------------------------------------------------------
// useCrudDetail — replaces the duplicated single-item fetch pattern
// ---------------------------------------------------------------------------

/**
 * Generic hook for fetching a single item by ID.
 *
 * Replaces the identical pattern in useVendor, useAssessment, useFinding,
 * useAlert, useEvidence.
 *
 * Usage:
 * ```ts
 * const { data: vendor, isLoading, error, refetch } = useCrudDetail<VendorDetail>(
 *   "/vendors",
 *   id,
 *   { entityName: "vendor" }
 * );
 * ```
 */
export function useCrudDetail<T>(
  endpoint: string,
  id: string,
  options: { entityName?: string } = {}
): CrudDetailResult<T> {
  const { entityName = "item" } = options;

  const [data, setData] = useState<T | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    if (!id) return;
    setIsLoading(true);
    setError(null);
    try {
      const res = await api.get<T>(`${endpoint}/${id}`);
      setData(res);
    } catch (err) {
      const apiErr = err as ApiError;
      setError(apiErr.message || `Failed to load ${entityName}`);
    } finally {
      setIsLoading(false);
    }
  }, [endpoint, id, entityName]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return { data, isLoading, error, refetch: fetchData };
}

// ---------------------------------------------------------------------------
// useCrudMutation — replaces the duplicated action/mutation pattern
// ---------------------------------------------------------------------------

/**
 * Generic hook for mutations (create, update, delete, actions).
 *
 * Replaces the identical pattern in useCreateVendor, useUpdateVendor,
 * useDeleteVendor, useCreateAssessment, useCloseFinding, etc.
 *
 * Usage:
 * ```ts
 * const { mutate: createVendor, isLoading } = useCrudMutation<
 *   [CreateVendorPayload],
 *   Vendor
 * >(async (data) => api.post<Vendor>("/vendors", data));
 * ```
 */
export function useCrudMutation<
  TArgs extends unknown[] = [],
  TReturn = void,
>(
  mutationFn: (...args: TArgs) => Promise<TReturn>
): CrudMutationResult<TArgs, TReturn> {
  const [isLoading, setIsLoading] = useState(false);
  // Keep a stable reference to the latest mutationFn without causing
  // the returned `mutate` callback to change identity on every render.
  const fnRef = useRef(mutationFn);
  fnRef.current = mutationFn;

  const mutate = useCallback(async (...args: TArgs): Promise<TReturn> => {
    setIsLoading(true);
    try {
      return await fnRef.current(...args);
    } finally {
      setIsLoading(false);
    }
  }, []);

  return { mutate, isLoading };
}

// ---------------------------------------------------------------------------
// useCrudArray — replaces the non-paginated array-fetch pattern
// ---------------------------------------------------------------------------

/**
 * Generic hook for fetching a simple array (no pagination wrapper).
 *
 * Replaces the pattern in useAssessmentTemplates, useAlertRules,
 * useEmailTemplates, useVendorTimeline, etc.
 *
 * Usage:
 * ```ts
 * const { items: templates, isLoading, error, refetch } = useCrudArray<AssessmentTemplate>(
 *   "/assessments/templates",
 *   { entityName: "templates" }
 * );
 * ```
 */
export function useCrudArray<T>(
  endpoint: string,
  options: { entityName?: string; enabled?: boolean } = {}
): CrudListResult<T> {
  const { entityName = "items", enabled = true } = options;

  const [items, setItems] = useState<T[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    if (!enabled) return;
    setIsLoading(true);
    setError(null);
    try {
      const res = await api.get<T[]>(endpoint);
      setItems(res ?? []);
    } catch (err) {
      const apiErr = err as ApiError;
      setError(apiErr.message || `Failed to load ${entityName}`);
    } finally {
      setIsLoading(false);
    }
  }, [endpoint, entityName, enabled]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return { items, total: items.length, isLoading, error, refetch: fetchData };
}
