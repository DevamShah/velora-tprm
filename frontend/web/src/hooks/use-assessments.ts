"use client";

import { useState, useEffect, useCallback } from "react";
import { api, type ApiError } from "@/lib/api";
import type {
  Assessment,
  AssessmentDetail,
  AssessmentListResponse,
  AssessmentFilters,
  CreateAssessmentPayload,
  UpdateResponsePayload,
  AssessmentTemplate,
  ReviewQueueItem,
  ReviewQueueResponse,
  AssessmentResponse as AssessmentResponseType,
} from "@/types/assessment";

function buildParams(filters: AssessmentFilters): Record<string, string> {
  const params: Record<string, string> = {};
  if (filters.search) params.search = filters.search;
  if (filters.status) params.status = filters.status;
  if (filters.vendor_id) params.vendor_id = filters.vendor_id;
  if (filters.template_id) params.template_id = filters.template_id;
  if (filters.sort_by) params.sort_by = filters.sort_by;
  if (filters.sort_order) params.sort_order = filters.sort_order;
  if (filters.page) params.page = String(filters.page);
  if (filters.page_size) params.page_size = String(filters.page_size);
  return params;
}

export function useAssessments(filters: AssessmentFilters) {
  const [assessments, setAssessments] = useState<Assessment[]>([]);
  const [total, setTotal] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetch = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const params = buildParams(filters);
      const res = await api.get<AssessmentListResponse>("/assessments", params);
      setAssessments(res.items);
      setTotal(res.total);
    } catch (err) {
      const apiErr = err as ApiError;
      setError(apiErr.message || "Failed to load assessments");
    } finally {
      setIsLoading(false);
    }
  }, [
    filters.search,
    filters.status,
    filters.vendor_id,
    filters.template_id,
    filters.sort_by,
    filters.sort_order,
    filters.page,
    filters.page_size,
  ]);

  useEffect(() => {
    fetch();
  }, [fetch]);

  return { assessments, total, isLoading, error, refetch: fetch };
}

export function useAssessment(id: string) {
  const [assessment, setAssessment] = useState<AssessmentDetail | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetch = useCallback(async () => {
    if (!id) return;
    setIsLoading(true);
    setError(null);
    try {
      const res = await api.get<AssessmentDetail>(`/assessments/${id}`);
      setAssessment(res);
    } catch (err) {
      const apiErr = err as ApiError;
      setError(apiErr.message || "Failed to load assessment");
    } finally {
      setIsLoading(false);
    }
  }, [id]);

  useEffect(() => {
    fetch();
  }, [fetch]);

  return { assessment, isLoading, error, refetch: fetch };
}

export function useCreateAssessment() {
  const [isLoading, setIsLoading] = useState(false);

  const createAssessment = useCallback(
    async (data: CreateAssessmentPayload): Promise<Assessment> => {
      setIsLoading(true);
      try {
        return await api.post<Assessment>("/assessments", data);
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  return { createAssessment, isLoading };
}

export function useAssessmentTemplates() {
  const [templates, setTemplates] = useState<AssessmentTemplate[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetch = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await api.get<AssessmentTemplate[]>("/assessments/templates");
      setTemplates(res);
    } catch (err) {
      const apiErr = err as ApiError;
      setError(apiErr.message || "Failed to load templates");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetch();
  }, [fetch]);

  return { templates, isLoading, error, refetch: fetch };
}

export function useDistributeAssessment() {
  const [isLoading, setIsLoading] = useState(false);

  const distribute = useCallback(async (id: string): Promise<void> => {
    setIsLoading(true);
    try {
      await api.post(`/assessments/${id}/distribute`);
    } finally {
      setIsLoading(false);
    }
  }, []);

  return { distribute, isLoading };
}

export function useSubmitAssessment() {
  const [isLoading, setIsLoading] = useState(false);

  const submit = useCallback(async (id: string): Promise<void> => {
    setIsLoading(true);
    try {
      await api.post(`/assessments/${id}/submit`);
    } finally {
      setIsLoading(false);
    }
  }, []);

  return { submit, isLoading };
}

export function useStartReview() {
  const [isLoading, setIsLoading] = useState(false);

  const startReview = useCallback(async (id: string): Promise<void> => {
    setIsLoading(true);
    try {
      await api.post(`/assessments/${id}/start-review`);
    } finally {
      setIsLoading(false);
    }
  }, []);

  return { startReview, isLoading };
}

export function useCompleteAssessment() {
  const [isLoading, setIsLoading] = useState(false);

  const complete = useCallback(async (id: string): Promise<void> => {
    setIsLoading(true);
    try {
      await api.post(`/assessments/${id}/complete`);
    } finally {
      setIsLoading(false);
    }
  }, []);

  return { complete, isLoading };
}

export function useCancelAssessment() {
  const [isLoading, setIsLoading] = useState(false);

  const cancel = useCallback(async (id: string): Promise<void> => {
    setIsLoading(true);
    try {
      await api.post(`/assessments/${id}/cancel`);
    } finally {
      setIsLoading(false);
    }
  }, []);

  return { cancel, isLoading };
}

export function useUpdateResponse() {
  const [isLoading, setIsLoading] = useState(false);

  const updateResponse = useCallback(
    async (
      assessmentId: string,
      responseId: string,
      data: UpdateResponsePayload
    ): Promise<AssessmentResponseType> => {
      setIsLoading(true);
      try {
        return await api.put<AssessmentResponseType>(
          `/assessments/${assessmentId}/responses/${responseId}`,
          data
        );
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  return { updateResponse, isLoading };
}

export function useReviewQueue() {
  const [items, setItems] = useState<ReviewQueueItem[]>([]);
  const [total, setTotal] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetch = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await api.get<ReviewQueueResponse>("/assessments/review-queue");
      setItems(res.items || []);
      setTotal(res.total || 0);
    } catch (err) {
      const apiErr = err as ApiError;
      setError(apiErr.message || "Failed to load review queue");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetch();
  }, [fetch]);

  return { items, total, isLoading, error, refetch: fetch };
}
