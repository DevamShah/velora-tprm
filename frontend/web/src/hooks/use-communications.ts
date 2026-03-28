"use client";

import { useState, useEffect, useCallback } from "react";
import { api, type ApiError } from "@/lib/api";
import type {
  Notification,
  NotificationListResponse,
  NotificationPreferences,
  EmailTemplate,
  CommunicationLog,
  CommunicationLogListResponse,
} from "@/types/communication";

export function useNotifications() {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [total, setTotal] = useState(0);
  const [unreadCount, setUnreadCount] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetch = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await api.get<NotificationListResponse>(
        "/communications/notifications"
      );
      setNotifications(res.items);
      setTotal(res.total);
      setUnreadCount(res.unread_count);
    } catch (err) {
      const apiErr = err as ApiError;
      setError(apiErr.message || "Failed to load notifications");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetch();
  }, [fetch]);

  return { notifications, total, unreadCount, isLoading, error, refetch: fetch };
}

export function useMarkRead() {
  const [isLoading, setIsLoading] = useState(false);

  const markRead = useCallback(async (id: string): Promise<void> => {
    setIsLoading(true);
    try {
      await api.put(`/communications/notifications/${id}/read`);
    } finally {
      setIsLoading(false);
    }
  }, []);

  return { markRead, isLoading };
}

export function useMarkAllRead() {
  const [isLoading, setIsLoading] = useState(false);

  const markAllRead = useCallback(async (): Promise<void> => {
    setIsLoading(true);
    try {
      await api.put("/communications/notifications/read-all");
    } finally {
      setIsLoading(false);
    }
  }, []);

  return { markAllRead, isLoading };
}

export function useNotificationPreferences() {
  const [preferences, setPreferences] =
    useState<NotificationPreferences | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetch = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await api.get<NotificationPreferences>(
        "/communications/preferences"
      );
      setPreferences(res);
    } catch (err) {
      const apiErr = err as ApiError;
      setError(apiErr.message || "Failed to load preferences");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetch();
  }, [fetch]);

  const updatePreferences = useCallback(
    async (data: Partial<NotificationPreferences>): Promise<void> => {
      try {
        const res = await api.put<NotificationPreferences>(
          "/communications/preferences",
          data
        );
        setPreferences(res);
      } catch (err) {
        const apiErr = err as ApiError;
        throw new Error(apiErr.message || "Failed to update preferences");
      }
    },
    []
  );

  return { preferences, isLoading, error, updatePreferences, refetch: fetch };
}

export function useEmailTemplates() {
  const [templates, setTemplates] = useState<EmailTemplate[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetch = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await api.get<EmailTemplate[]>(
        "/communications/templates"
      );
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

export function useCommunicationLogs() {
  const [logs, setLogs] = useState<CommunicationLog[]>([]);
  const [total, setTotal] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetch = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await api.get<CommunicationLogListResponse>(
        "/communications/logs"
      );
      setLogs(res.items);
      setTotal(res.total);
    } catch (err) {
      const apiErr = err as ApiError;
      setError(apiErr.message || "Failed to load communication logs");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetch();
  }, [fetch]);

  return { logs, total, isLoading, error, refetch: fetch };
}
