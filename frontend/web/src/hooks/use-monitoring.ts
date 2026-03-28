"use client";

import { useState, useEffect, useCallback } from "react";
import { api, type ApiError } from "@/lib/api";
import type {
  Alert,
  AlertDetail,
  AlertListResponse,
  AlertFilters,
  AlertRule,
  CreateAlertRulePayload,
  TimelineEvent,
} from "@/types/monitoring";

function buildParams(filters: AlertFilters): Record<string, string> {
  const params: Record<string, string> = {};
  if (filters.search) params.search = filters.search;
  if (filters.priority) params.priority = filters.priority;
  if (filters.status) params.status = filters.status;
  if (filters.source) params.source = filters.source;
  if (filters.vendor_id) params.vendor_id = filters.vendor_id;
  if (filters.sort_by) params.sort_by = filters.sort_by;
  if (filters.sort_order) params.sort_order = filters.sort_order;
  if (filters.page) params.page = String(filters.page);
  if (filters.page_size) params.page_size = String(filters.page_size);
  return params;
}

export function useAlerts(filters: AlertFilters) {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [total, setTotal] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetch = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const params = buildParams(filters);
      const res = await api.get<AlertListResponse>("/monitoring/alerts", params);
      setAlerts(res.items);
      setTotal(res.total);
    } catch (err) {
      const apiErr = err as ApiError;
      setError(apiErr.message || "Failed to load alerts");
    } finally {
      setIsLoading(false);
    }
  }, [
    filters.search,
    filters.priority,
    filters.status,
    filters.source,
    filters.vendor_id,
    filters.sort_by,
    filters.sort_order,
    filters.page,
    filters.page_size,
  ]);

  useEffect(() => {
    fetch();
  }, [fetch]);

  return { alerts, total, isLoading, error, refetch: fetch };
}

export function useAlert(id: string) {
  const [alert, setAlert] = useState<AlertDetail | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetch = useCallback(async () => {
    if (!id) return;
    setIsLoading(true);
    setError(null);
    try {
      const res = await api.get<AlertDetail>(`/monitoring/alerts/${id}`);
      setAlert(res);
    } catch (err) {
      const apiErr = err as ApiError;
      setError(apiErr.message || "Failed to load alert detail");
    } finally {
      setIsLoading(false);
    }
  }, [id]);

  useEffect(() => {
    fetch();
  }, [fetch]);

  return { alert, isLoading, error, refetch: fetch };
}

export function useAcknowledgeAlert() {
  const [isLoading, setIsLoading] = useState(false);

  const acknowledge = useCallback(async (id: string): Promise<void> => {
    setIsLoading(true);
    try {
      await api.put(`/monitoring/alerts/${id}/acknowledge`);
    } finally {
      setIsLoading(false);
    }
  }, []);

  return { acknowledge, isLoading };
}

export function useResolveAlert() {
  const [isLoading, setIsLoading] = useState(false);

  const resolve = useCallback(
    async (id: string, resolutionNotes: string): Promise<void> => {
      setIsLoading(true);
      try {
        await api.put(`/monitoring/alerts/${id}/resolve`, {
          resolution_notes: resolutionNotes,
        });
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  return { resolve, isLoading };
}

export function useSuppressAlert() {
  const [isLoading, setIsLoading] = useState(false);

  const suppress = useCallback(async (id: string): Promise<void> => {
    setIsLoading(true);
    try {
      await api.put(`/monitoring/alerts/${id}/suppress`);
    } finally {
      setIsLoading(false);
    }
  }, []);

  return { suppress, isLoading };
}

export function useVendorTimeline(vendorId: string) {
  const [events, setEvents] = useState<TimelineEvent[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetch = useCallback(async () => {
    if (!vendorId) return;
    setIsLoading(true);
    setError(null);
    try {
      const res = await api.get<TimelineEvent[]>(
        `/monitoring/vendors/${vendorId}/timeline`
      );
      setEvents(res);
    } catch (err) {
      const apiErr = err as ApiError;
      setError(apiErr.message || "Failed to load vendor timeline");
    } finally {
      setIsLoading(false);
    }
  }, [vendorId]);

  useEffect(() => {
    fetch();
  }, [fetch]);

  return { events, isLoading, error, refetch: fetch };
}

export function useAlertRules() {
  const [rules, setRules] = useState<AlertRule[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetch = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await api.get<AlertRule[]>("/monitoring/alert-rules");
      setRules(res);
    } catch (err) {
      const apiErr = err as ApiError;
      setError(apiErr.message || "Failed to load alert rules");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetch();
  }, [fetch]);

  return { rules, isLoading, error, refetch: fetch };
}

export function useCreateAlertRule() {
  const [isLoading, setIsLoading] = useState(false);

  const createRule = useCallback(
    async (data: CreateAlertRulePayload): Promise<AlertRule> => {
      setIsLoading(true);
      try {
        return await api.post<AlertRule>("/monitoring/alert-rules", data);
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  return { createRule, isLoading };
}

export function useUpdateAlertRule() {
  const [isLoading, setIsLoading] = useState(false);

  const updateRule = useCallback(
    async (
      id: string,
      data: Partial<CreateAlertRulePayload>
    ): Promise<AlertRule> => {
      setIsLoading(true);
      try {
        return await api.put<AlertRule>(`/monitoring/alert-rules/${id}`, data);
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  return { updateRule, isLoading };
}
