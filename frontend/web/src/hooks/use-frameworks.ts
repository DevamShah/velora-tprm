"use client";

import { useState, useEffect, useCallback } from "react";
import { api, type ApiError } from "@/lib/api";
import type {
  Framework,
  FrameworkDetail,
  FrameworkListResponse,
  ClauseTreeNode,
  ClauseListResponse,
  CrossFrameworkMapping,
  MappingListResponse,
  UnifiedControl,
  UnifiedControlListResponse,
} from "@/types/framework";

export function useFrameworks() {
  const [frameworks, setFrameworks] = useState<Framework[]>([]);
  const [total, setTotal] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetch = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await api.get<FrameworkListResponse>("/frameworks");
      setFrameworks(res.items);
      setTotal(res.total);
    } catch (err) {
      const apiErr = err as ApiError;
      setError(apiErr.message || "Failed to load frameworks");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetch();
  }, [fetch]);

  return { frameworks, total, isLoading, error, refetch: fetch };
}

export function useFramework(id: string) {
  const [framework, setFramework] = useState<FrameworkDetail | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetch = useCallback(async () => {
    if (!id) return;
    setIsLoading(true);
    setError(null);
    try {
      const res = await api.get<FrameworkDetail>(`/frameworks/${id}`);
      setFramework(res);
    } catch (err) {
      const apiErr = err as ApiError;
      setError(apiErr.message || "Failed to load framework");
    } finally {
      setIsLoading(false);
    }
  }, [id]);

  useEffect(() => {
    fetch();
  }, [fetch]);

  return { framework, isLoading, error, refetch: fetch };
}

export function useFrameworkClauses(frameworkId: string) {
  const [clauses, setClauses] = useState<ClauseTreeNode[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetch = useCallback(async () => {
    if (!frameworkId) return;
    setIsLoading(true);
    setError(null);
    try {
      const res = await api.get<ClauseListResponse>(
        `/frameworks/${frameworkId}/clauses`
      );
      setClauses(res.clauses);
    } catch (err) {
      const apiErr = err as ApiError;
      setError(apiErr.message || "Failed to load clauses");
    } finally {
      setIsLoading(false);
    }
  }, [frameworkId]);

  useEffect(() => {
    fetch();
  }, [fetch]);

  return { clauses, isLoading, error, refetch: fetch };
}

export function useClauseMappings(frameworkId: string, clauseId: string) {
  const [mappings, setMappings] = useState<CrossFrameworkMapping[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetch = useCallback(async () => {
    if (!frameworkId || !clauseId) return;
    setIsLoading(true);
    setError(null);
    try {
      const res = await api.get<MappingListResponse>(
        `/frameworks/${frameworkId}/clauses/${clauseId}/mappings`
      );
      setMappings(res.mappings);
    } catch (err) {
      const apiErr = err as ApiError;
      setError(apiErr.message || "Failed to load mappings");
    } finally {
      setIsLoading(false);
    }
  }, [frameworkId, clauseId]);

  useEffect(() => {
    fetch();
  }, [fetch]);

  return { mappings, isLoading, error, refetch: fetch };
}

export function useUnifiedControls() {
  const [controls, setControls] = useState<UnifiedControl[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetch = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await api.get<UnifiedControlListResponse>(
        "/frameworks/unified-controls"
      );
      setControls(res.controls);
    } catch (err) {
      const apiErr = err as ApiError;
      setError(apiErr.message || "Failed to load unified controls");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetch();
  }, [fetch]);

  return { controls, isLoading, error, refetch: fetch };
}
