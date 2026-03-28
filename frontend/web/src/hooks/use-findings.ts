"use client";

import { useState, useEffect, useCallback } from "react";
import { api, type ApiError } from "@/lib/api";
import type {
  Finding,
  FindingDetail,
  FindingListResponse,
  FindingFilters,
  CreateFindingPayload,
  CreateRemediationPayload,
  UpdateRemediationPayload,
  RemediationAction,
} from "@/types/finding";

function buildParams(filters: FindingFilters): Record<string, string> {
  const params: Record<string, string> = {};
  if (filters.search) params.search = filters.search;
  if (filters.severity) params.severity = filters.severity;
  if (filters.status) params.status = filters.status;
  if (filters.vendor_id) params.vendor_id = filters.vendor_id;
  if (filters.sort_by) params.sort_by = filters.sort_by;
  if (filters.sort_order) params.sort_order = filters.sort_order;
  if (filters.page) params.page = String(filters.page);
  if (filters.page_size) params.page_size = String(filters.page_size);
  return params;
}

export function useFindings(filters: FindingFilters) {
  const [findings, setFindings] = useState<Finding[]>([]);
  const [total, setTotal] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetch = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const params = buildParams(filters);
      const res = await api.get<FindingListResponse>("/findings", params);
      setFindings(res.items);
      setTotal(res.total);
    } catch (err) {
      const apiErr = err as ApiError;
      setError(apiErr.message || "Failed to load findings");
    } finally {
      setIsLoading(false);
    }
  }, [
    filters.search,
    filters.severity,
    filters.status,
    filters.vendor_id,
    filters.sort_by,
    filters.sort_order,
    filters.page,
    filters.page_size,
  ]);

  useEffect(() => {
    fetch();
  }, [fetch]);

  return { findings, total, isLoading, error, refetch: fetch };
}

export function useFinding(id: string) {
  const [finding, setFinding] = useState<FindingDetail | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetch = useCallback(async () => {
    if (!id) return;
    setIsLoading(true);
    setError(null);
    try {
      const res = await api.get<FindingDetail>(`/findings/${id}`);
      setFinding(res);
    } catch (err) {
      const apiErr = err as ApiError;
      setError(apiErr.message || "Failed to load finding");
    } finally {
      setIsLoading(false);
    }
  }, [id]);

  useEffect(() => {
    fetch();
  }, [fetch]);

  return { finding, isLoading, error, refetch: fetch };
}

export function useCreateFinding() {
  const [isLoading, setIsLoading] = useState(false);

  const createFinding = useCallback(
    async (data: CreateFindingPayload): Promise<Finding> => {
      setIsLoading(true);
      try {
        return await api.post<Finding>("/findings", data);
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  return { createFinding, isLoading };
}

export function useCloseFinding() {
  const [isLoading, setIsLoading] = useState(false);

  const closeFinding = useCallback(async (id: string): Promise<void> => {
    setIsLoading(true);
    try {
      await api.post(`/findings/${id}/close`);
    } finally {
      setIsLoading(false);
    }
  }, []);

  return { closeFinding, isLoading };
}

export function useAddRemediation() {
  const [isLoading, setIsLoading] = useState(false);

  const addRemediation = useCallback(
    async (
      findingId: string,
      data: CreateRemediationPayload
    ): Promise<RemediationAction> => {
      setIsLoading(true);
      try {
        return await api.post<RemediationAction>(
          `/findings/${findingId}/remediation`,
          data
        );
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  return { addRemediation, isLoading };
}

export function useUpdateRemediation() {
  const [isLoading, setIsLoading] = useState(false);

  const updateRemediation = useCallback(
    async (
      findingId: string,
      actionId: string,
      data: UpdateRemediationPayload
    ): Promise<RemediationAction> => {
      setIsLoading(true);
      try {
        return await api.put<RemediationAction>(
          `/findings/${findingId}/remediation/${actionId}`,
          data
        );
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  return { updateRemediation, isLoading };
}
