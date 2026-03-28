"use client";

import { useState, useEffect, useCallback } from "react";
import { api, type ApiError } from "@/lib/api";
import type {
  AdminUser,
  AdminUserListResponse,
  CreateUserPayload,
  UpdateUserPayload,
  AssignRolesPayload,
  Role,
  CreateRolePayload,
  AuditLogEntry,
  AuditLogListResponse,
  AuditLogFilters,
} from "@/types/admin";

function buildAuditParams(filters: AuditLogFilters): Record<string, string> {
  const params: Record<string, string> = {};
  if (filters.user_id) params.user_id = filters.user_id;
  if (filters.action) params.action = filters.action;
  if (filters.resource_type) params.resource_type = filters.resource_type;
  if (filters.date_from) params.date_from = filters.date_from;
  if (filters.date_to) params.date_to = filters.date_to;
  if (filters.search) params.search = filters.search;
  if (filters.page) params.page = String(filters.page);
  if (filters.page_size) params.page_size = String(filters.page_size);
  return params;
}

export function useUsers() {
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [total, setTotal] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetch = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await api.get<AdminUserListResponse>("/admin/users");
      setUsers(res.items);
      setTotal(res.total);
    } catch (err) {
      const apiErr = err as ApiError;
      setError(apiErr.message || "Failed to load users");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetch();
  }, [fetch]);

  return { users, total, isLoading, error, refetch: fetch };
}

export function useCreateUser() {
  const [isLoading, setIsLoading] = useState(false);

  const createUser = useCallback(
    async (data: CreateUserPayload): Promise<AdminUser> => {
      setIsLoading(true);
      try {
        return await api.post<AdminUser>("/admin/users", data);
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  return { createUser, isLoading };
}

export function useUpdateUser() {
  const [isLoading, setIsLoading] = useState(false);

  const updateUser = useCallback(
    async (id: string, data: UpdateUserPayload): Promise<AdminUser> => {
      setIsLoading(true);
      try {
        return await api.put<AdminUser>(`/admin/users/${id}`, data);
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  return { updateUser, isLoading };
}

export function useDeactivateUser() {
  const [isLoading, setIsLoading] = useState(false);

  const deactivateUser = useCallback(async (id: string): Promise<void> => {
    setIsLoading(true);
    try {
      await api.delete(`/admin/users/${id}`);
    } finally {
      setIsLoading(false);
    }
  }, []);

  return { deactivateUser, isLoading };
}

export function useAssignRoles() {
  const [isLoading, setIsLoading] = useState(false);

  const assignRoles = useCallback(
    async (userId: string, data: AssignRolesPayload): Promise<void> => {
      setIsLoading(true);
      try {
        await api.post(`/admin/users/${userId}/roles`, data);
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  return { assignRoles, isLoading };
}

export function useRoles() {
  const [roles, setRoles] = useState<Role[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetch = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await api.get<Role[]>("/admin/roles");
      setRoles(res);
    } catch (err) {
      const apiErr = err as ApiError;
      setError(apiErr.message || "Failed to load roles");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetch();
  }, [fetch]);

  return { roles, isLoading, error, refetch: fetch };
}

export function useCreateRole() {
  const [isLoading, setIsLoading] = useState(false);

  const createRole = useCallback(
    async (data: CreateRolePayload): Promise<Role> => {
      setIsLoading(true);
      try {
        return await api.post<Role>("/admin/roles", data);
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  return { createRole, isLoading };
}

export function useAuditLogs(filters: AuditLogFilters) {
  const [logs, setLogs] = useState<AuditLogEntry[]>([]);
  const [total, setTotal] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetch = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const params = buildAuditParams(filters);
      const res = await api.get<AuditLogListResponse>(
        "/admin/audit-logs",
        params
      );
      setLogs(res.items);
      setTotal(res.total);
    } catch (err) {
      const apiErr = err as ApiError;
      setError(apiErr.message || "Failed to load audit logs");
    } finally {
      setIsLoading(false);
    }
  }, [
    filters.user_id,
    filters.action,
    filters.resource_type,
    filters.date_from,
    filters.date_to,
    filters.search,
    filters.page,
    filters.page_size,
  ]);

  useEffect(() => {
    fetch();
  }, [fetch]);

  return { logs, total, isLoading, error, refetch: fetch };
}
