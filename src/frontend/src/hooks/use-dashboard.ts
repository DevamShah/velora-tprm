"use client";

import { useState, useEffect, useCallback } from "react";
import { api, type ApiError } from "@/lib/api";
import type {
  DashboardData,
  Report,
  ReportListResponse,
  GenerateReportPayload,
} from "@/types/dashboard";

export function useDashboard() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetch = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await api.get<DashboardData>(
        "/reports/dashboards/data/executive"
      );
      setData(res);
    } catch (err) {
      const apiErr = err as ApiError;
      setError(apiErr.message || "Failed to load dashboard data");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetch();
  }, [fetch]);

  return { data, isLoading, error, refetch: fetch };
}

export function useReports() {
  const [reports, setReports] = useState<Report[]>([]);
  const [total, setTotal] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetch = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await api.get<ReportListResponse>("/reports");
      setReports(res.items);
      setTotal(res.total);
    } catch (err) {
      const apiErr = err as ApiError;
      setError(apiErr.message || "Failed to load reports");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetch();
  }, [fetch]);

  return { reports, total, isLoading, error, refetch: fetch };
}

export function useReportGeneration() {
  const [isLoading, setIsLoading] = useState(false);

  const generateReport = useCallback(
    async (data: GenerateReportPayload): Promise<Report> => {
      setIsLoading(true);
      try {
        return await api.post<Report>("/reports/generate", data);
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  return { generateReport, isLoading };
}
