// Vendor domain types — maps 1:1 to backend API schema

export type VendorStatus =
  | "discovered"
  | "classified"
  | "assessing"
  | "active"
  | "monitoring"
  | "reassessing"
  | "offboarding"
  | "offboarded"
  | "archived";

export type VendorTier =
  | "critical"
  | "high"
  | "medium"
  | "low"
  | "unclassified";

export type DataClassification =
  | "public"
  | "internal"
  | "confidential"
  | "restricted";

export type BusinessCriticality = "critical" | "high" | "medium" | "low";

export interface Vendor {
  id: string;
  tenant_id: string;
  name: string;
  domain: string | null;
  description: string | null;
  status: VendorStatus;
  tier: VendorTier;
  industry: string | null;
  country: string | null;
  employee_count: number | null;
  annual_revenue: number | null;
  data_classification: DataClassification | null;
  business_criticality: BusinessCriticality | null;
  contract_start_date: string | null;
  contract_end_date: string | null;
  contract_value: number | null;
  primary_contact_name: string | null;
  primary_contact_email: string | null;
  tags: string[];
  notes: string | null;
  inherent_risk_score: number | null;
  residual_risk_score: number | null;
  external_rating_score: number | null;
  contacts_count: number;
  created_at: string;
  updated_at: string;
}

export interface VendorContact {
  id: string;
  first_name: string;
  last_name: string;
  email: string;
  phone: string | null;
  role: string | null;
  is_primary: boolean;
}

export interface VendorDetail extends Vendor {
  contacts: VendorContact[];
  enrichments: unknown[];
}

export interface VendorListResponse {
  items: Vendor[];
  total: number;
  page: number;
  page_size: number;
}

export interface VendorFilters {
  status?: VendorStatus | "";
  tier?: VendorTier | "";
  search?: string;
  tags?: string[];
  sort_by?: string;
  sort_order?: "asc" | "desc";
  page?: number;
  page_size?: number;
}

export interface CreateVendorPayload {
  name: string;
  domain?: string;
  description?: string;
  industry?: string;
  country?: string;
  status?: VendorStatus;
  tier?: VendorTier;
  data_classification?: DataClassification;
  business_criticality?: BusinessCriticality;
  contract_start_date?: string;
  contract_end_date?: string;
  contract_value?: number;
  tags?: string[];
  notes?: string;
}

export interface CreateContactPayload {
  first_name: string;
  last_name: string;
  email: string;
  phone?: string;
  role?: string;
  is_primary?: boolean;
}

export interface BulkImportResponse {
  success_count: number;
  error_count: number;
  errors: Array<{ row: number; message: string }>;
}

export interface TierCalculationResponse {
  tier: VendorTier;
}

export const VENDOR_STATUSES: VendorStatus[] = [
  "discovered",
  "classified",
  "assessing",
  "active",
  "monitoring",
  "reassessing",
  "offboarding",
  "offboarded",
  "archived",
];

export const VENDOR_TIERS: VendorTier[] = [
  "critical",
  "high",
  "medium",
  "low",
  "unclassified",
];

export const DATA_CLASSIFICATIONS: DataClassification[] = [
  "public",
  "internal",
  "confidential",
  "restricted",
];

export const BUSINESS_CRITICALITIES: BusinessCriticality[] = [
  "critical",
  "high",
  "medium",
  "low",
];
