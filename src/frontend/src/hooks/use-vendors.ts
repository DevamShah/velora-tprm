"use client";

import { useState, useEffect, useCallback } from "react";
import { api, type ApiError } from "@/lib/api";
import type {
  Vendor,
  VendorDetail,
  VendorListResponse,
  VendorFilters,
  CreateVendorPayload,
  CreateContactPayload,
  VendorContact,
  BulkImportResponse,
  TierCalculationResponse,
} from "@/types/vendor";

function buildParams(filters: VendorFilters): Record<string, string> {
  const params: Record<string, string> = {};
  if (filters.search) params.search = filters.search;
  if (filters.status) params.status = filters.status;
  if (filters.tier) params.tier = filters.tier;
  if (filters.sort_by) params.sort_by = filters.sort_by;
  if (filters.sort_order) params.sort_order = filters.sort_order;
  if (filters.page) params.page = String(filters.page);
  if (filters.page_size) params.page_size = String(filters.page_size);
  return params;
}

export function useVendors(filters: VendorFilters) {
  const [vendors, setVendors] = useState<Vendor[]>([]);
  const [total, setTotal] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetch = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const params = buildParams(filters);
      const res = await api.get<VendorListResponse>("/vendors", params);
      setVendors(res.items);
      setTotal(res.total);
    } catch (err) {
      const apiErr = err as ApiError;
      setError(apiErr.message || "Failed to load vendors");
    } finally {
      setIsLoading(false);
    }
  }, [
    filters.search,
    filters.status,
    filters.tier,
    filters.sort_by,
    filters.sort_order,
    filters.page,
    filters.page_size,
  ]);

  useEffect(() => {
    fetch();
  }, [fetch]);

  return { vendors, total, isLoading, error, refetch: fetch };
}

export function useVendor(id: string) {
  const [vendor, setVendor] = useState<VendorDetail | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetch = useCallback(async () => {
    if (!id) return;
    setIsLoading(true);
    setError(null);
    try {
      const res = await api.get<VendorDetail>(`/vendors/${id}`);
      setVendor(res);
    } catch (err) {
      const apiErr = err as ApiError;
      setError(apiErr.message || "Failed to load vendor");
    } finally {
      setIsLoading(false);
    }
  }, [id]);

  useEffect(() => {
    fetch();
  }, [fetch]);

  return { vendor, isLoading, error, refetch: fetch };
}

export function useCreateVendor() {
  const [isLoading, setIsLoading] = useState(false);

  const createVendor = useCallback(
    async (data: CreateVendorPayload): Promise<Vendor> => {
      setIsLoading(true);
      try {
        return await api.post<Vendor>("/vendors", data);
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  return { createVendor, isLoading };
}

export function useUpdateVendor() {
  const [isLoading, setIsLoading] = useState(false);

  const updateVendor = useCallback(
    async (id: string, data: Partial<CreateVendorPayload>): Promise<Vendor> => {
      setIsLoading(true);
      try {
        return await api.put<Vendor>(`/vendors/${id}`, data);
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  return { updateVendor, isLoading };
}

export function useDeleteVendor() {
  const [isLoading, setIsLoading] = useState(false);

  const deleteVendor = useCallback(async (id: string): Promise<void> => {
    setIsLoading(true);
    try {
      await api.delete(`/vendors/${id}`);
    } finally {
      setIsLoading(false);
    }
  }, []);

  return { deleteVendor, isLoading };
}

export function useCreateContact() {
  const [isLoading, setIsLoading] = useState(false);

  const createContact = useCallback(
    async (
      vendorId: string,
      data: CreateContactPayload
    ): Promise<VendorContact> => {
      setIsLoading(true);
      try {
        return await api.post<VendorContact>(
          `/vendors/${vendorId}/contacts`,
          data
        );
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  return { createContact, isLoading };
}

export function useUpdateContact() {
  const [isLoading, setIsLoading] = useState(false);

  const updateContact = useCallback(
    async (
      vendorId: string,
      contactId: string,
      data: Partial<CreateContactPayload>
    ): Promise<VendorContact> => {
      setIsLoading(true);
      try {
        return await api.put<VendorContact>(
          `/vendors/${vendorId}/contacts/${contactId}`,
          data
        );
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  return { updateContact, isLoading };
}

export function useBulkImport() {
  const [isLoading, setIsLoading] = useState(false);

  const bulkImport = useCallback(
    async (csvData: string): Promise<BulkImportResponse> => {
      setIsLoading(true);
      try {
        return await api.post<BulkImportResponse>("/vendors/bulk-import", {
          csv_data: csvData,
        });
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  return { bulkImport, isLoading };
}

export function useCalculateTier() {
  const [isLoading, setIsLoading] = useState(false);

  const calculateTier = useCallback(
    async (vendorId: string): Promise<TierCalculationResponse> => {
      setIsLoading(true);
      try {
        return await api.post<TierCalculationResponse>(
          `/vendors/${vendorId}/calculate-tier`
        );
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  return { calculateTier, isLoading };
}
