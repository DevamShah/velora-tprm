"use client";

import { useState, useEffect, useCallback } from "react";
import { api, type ApiError } from "@/lib/api";
import type {
  ScoringModel,
  ScoringModelListResponse,
  CreateScoringModelPayload,
  ScoreBreakdown,
  VendorScore,
  ScoreHistoryItem,
  ScoreHistoryResponse,
  PortfolioSummary,
} from "@/types/scoring";

export function useScoringModels() {
  const [models, setModels] = useState<ScoringModel[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetch = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await api.get<ScoringModelListResponse>("/scoring/models");
      setModels(res.items);
    } catch (err) {
      const apiErr = err as ApiError;
      setError(apiErr.message || "Failed to load scoring models");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetch();
  }, [fetch]);

  return { models, isLoading, error, refetch: fetch };
}

export function useCreateScoringModel() {
  const [isLoading, setIsLoading] = useState(false);

  const createModel = useCallback(
    async (data: CreateScoringModelPayload): Promise<ScoringModel> => {
      setIsLoading(true);
      try {
        return await api.post<ScoringModel>("/scoring/models", data);
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  return { createModel, isLoading };
}

export function useCalculateScore() {
  const [isLoading, setIsLoading] = useState(false);

  const calculateScore = useCallback(
    async (vendorId: string): Promise<ScoreBreakdown> => {
      setIsLoading(true);
      try {
        return await api.post<ScoreBreakdown>(
          `/scoring/calculate/${vendorId}`
        );
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  return { calculateScore, isLoading };
}

export function useVendorScore(vendorId: string) {
  const [score, setScore] = useState<VendorScore | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetch = useCallback(async () => {
    if (!vendorId) return;
    setIsLoading(true);
    setError(null);
    try {
      const res = await api.get<VendorScore>(
        `/scoring/vendors/${vendorId}`
      );
      setScore(res);
    } catch (err) {
      const apiErr = err as ApiError;
      setError(apiErr.message || "Failed to load vendor score");
    } finally {
      setIsLoading(false);
    }
  }, [vendorId]);

  useEffect(() => {
    fetch();
  }, [fetch]);

  return { score, isLoading, error, refetch: fetch };
}

export function useScoreHistory(vendorId: string) {
  const [history, setHistory] = useState<ScoreHistoryItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetch = useCallback(async () => {
    if (!vendorId) return;
    setIsLoading(true);
    setError(null);
    try {
      const res = await api.get<ScoreHistoryResponse>(
        `/scoring/vendors/${vendorId}/history`
      );
      setHistory(res.items);
    } catch (err) {
      const apiErr = err as ApiError;
      setError(apiErr.message || "Failed to load score history");
    } finally {
      setIsLoading(false);
    }
  }, [vendorId]);

  useEffect(() => {
    fetch();
  }, [fetch]);

  return { history, isLoading, error, refetch: fetch };
}

export function usePortfolioSummary() {
  const [portfolio, setPortfolio] = useState<PortfolioSummary | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetch = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await api.get<PortfolioSummary>("/scoring/portfolio");
      setPortfolio(res);
    } catch (err) {
      const apiErr = err as ApiError;
      setError(apiErr.message || "Failed to load portfolio summary");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetch();
  }, [fetch]);

  return { portfolio, isLoading, error, refetch: fetch };
}
