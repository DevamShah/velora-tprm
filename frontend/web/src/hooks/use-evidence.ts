"use client";

import { useState, useEffect, useCallback } from "react";
import { api, type ApiError } from "@/lib/api";
import type {
  Evidence,
  EvidenceDetail,
  EvidenceListResponse,
  EvidenceFilters,
  EvidenceControlMapping,
  UploadUrlRequest,
  UploadUrlResponse,
} from "@/types/evidence";

function buildParams(filters: EvidenceFilters): Record<string, string> {
  const params: Record<string, string> = {};
  if (filters.search) params.search = filters.search;
  if (filters.vendor_id) params.vendor_id = filters.vendor_id;
  if (filters.status) params.status = filters.status;
  if (filters.document_type) params.document_type = filters.document_type;
  if (filters.sort_by) params.sort_by = filters.sort_by;
  if (filters.sort_order) params.sort_order = filters.sort_order;
  if (filters.page) params.page = String(filters.page);
  if (filters.page_size) params.page_size = String(filters.page_size);
  return params;
}

export function useEvidenceList(filters: EvidenceFilters) {
  const [evidence, setEvidence] = useState<Evidence[]>([]);
  const [total, setTotal] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetch = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const params = buildParams(filters);
      const res = await api.get<EvidenceListResponse>("/evidence", params);
      setEvidence(res.items);
      setTotal(res.total);
    } catch (err) {
      const apiErr = err as ApiError;
      setError(apiErr.message || "Failed to load evidence");
    } finally {
      setIsLoading(false);
    }
  }, [
    filters.search,
    filters.vendor_id,
    filters.status,
    filters.document_type,
    filters.sort_by,
    filters.sort_order,
    filters.page,
    filters.page_size,
  ]);

  useEffect(() => {
    fetch();
  }, [fetch]);

  return { evidence, total, isLoading, error, refetch: fetch };
}

export function useEvidence(id: string) {
  const [evidence, setEvidence] = useState<EvidenceDetail | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetch = useCallback(async () => {
    if (!id) return;
    setIsLoading(true);
    setError(null);
    try {
      const res = await api.get<EvidenceDetail>(`/evidence/${id}`);
      setEvidence(res);
    } catch (err) {
      const apiErr = err as ApiError;
      setError(apiErr.message || "Failed to load evidence detail");
    } finally {
      setIsLoading(false);
    }
  }, [id]);

  useEffect(() => {
    fetch();
  }, [fetch]);

  return { evidence, isLoading, error, refetch: fetch };
}

export function useUploadEvidence() {
  const [isLoading, setIsLoading] = useState(false);

  const getUploadUrl = useCallback(
    async (data: UploadUrlRequest): Promise<UploadUrlResponse> => {
      setIsLoading(true);
      try {
        return await api.post<UploadUrlResponse>("/evidence/upload-url", data);
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  const uploadToPresignedUrl = useCallback(
    async (uploadUrl: string, file: File): Promise<void> => {
      setIsLoading(true);
      try {
        await fetch(uploadUrl, {
          method: "PUT",
          body: file,
          headers: { "Content-Type": file.type },
        });
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  return { getUploadUrl, uploadToPresignedUrl, isLoading };
}

export function useProcessEvidence() {
  const [isLoading, setIsLoading] = useState(false);

  const processEvidence = useCallback(async (id: string): Promise<void> => {
    setIsLoading(true);
    try {
      await api.post(`/evidence/${id}/process`);
    } finally {
      setIsLoading(false);
    }
  }, []);

  return { processEvidence, isLoading };
}

export function useVerifyMapping() {
  const [isLoading, setIsLoading] = useState(false);

  const verifyMapping = useCallback(
    async (
      evidenceId: string,
      mappingId: string,
      verified: boolean
    ): Promise<EvidenceControlMapping> => {
      setIsLoading(true);
      try {
        return await api.put<EvidenceControlMapping>(
          `/evidence/${evidenceId}/mappings/${mappingId}`,
          { verified }
        );
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  return { verifyMapping, isLoading };
}

export function useDeleteEvidence() {
  const [isLoading, setIsLoading] = useState(false);

  const deleteEvidence = useCallback(async (id: string): Promise<void> => {
    setIsLoading(true);
    try {
      await api.delete(`/evidence/${id}`);
    } finally {
      setIsLoading(false);
    }
  }, []);

  return { deleteEvidence, isLoading };
}
