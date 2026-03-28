"use client";

import { useState, useEffect, useCallback } from "react";
import { api, type ApiError } from "@/lib/api";

export interface AutoFillResult {
  assessment_id: string;
  filled_count: number;
  skipped_count: number;
  confidence_avg: number;
}

export interface AIReviewQueueItem {
  id: string;
  assessment_id: string;
  assessment_title: string;
  vendor_name: string;
  question_text: string;
  ai_response: string;
  confidence_score: number;
  decision: "pending" | "accepted" | "rejected" | "modified";
  notes: string | null;
  created_at: string;
}

export interface AIReviewQueueResponse {
  items: AIReviewQueueItem[];
  total: number;
}

export interface AIUsageStats {
  total_requests: number;
  total_tokens: number;
  auto_fill_count: number;
  avg_confidence: number;
  period_start: string;
  period_end: string;
}

export function useAutoFill() {
  const [isLoading, setIsLoading] = useState(false);

  const autoFill = useCallback(
    async (assessmentId: string): Promise<AutoFillResult> => {
      setIsLoading(true);
      try {
        return await api.post<AutoFillResult>("/ai/auto-fill", {
          assessment_id: assessmentId,
        });
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  return { autoFill, isLoading };
}

export function useAIReviewQueue() {
  const [items, setItems] = useState<AIReviewQueueItem[]>([]);
  const [total, setTotal] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetch = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await api.get<AIReviewQueueResponse>("/ai/review-queue");
      setItems(res.items || []);
      setTotal(res.total || 0);
    } catch (err) {
      const apiErr = err as ApiError;
      setError(apiErr.message || "Failed to load AI review queue");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetch();
  }, [fetch]);

  return { items, total, isLoading, error, refetch: fetch };
}

export function useSubmitAIReview() {
  const [isLoading, setIsLoading] = useState(false);

  const submitReview = useCallback(
    async (
      id: string,
      decision: "accepted" | "rejected" | "modified",
      notes?: string
    ): Promise<void> => {
      setIsLoading(true);
      try {
        await api.put(`/ai/review-queue/${id}`, { decision, notes });
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  return { submitReview, isLoading };
}

export function useAIUsage() {
  const [stats, setStats] = useState<AIUsageStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetch = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await api.get<AIUsageStats>("/ai/usage");
      setStats(res);
    } catch (err) {
      const apiErr = err as ApiError;
      setError(apiErr.message || "Failed to load AI usage stats");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetch();
  }, [fetch]);

  return { stats, isLoading, error, refetch: fetch };
}
