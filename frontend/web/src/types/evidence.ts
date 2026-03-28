// Evidence domain types — maps 1:1 to backend API schema

export type EvidenceStatus =
  | "pending"
  | "processing"
  | "processed"
  | "failed"
  | "archived";

export type EvidenceType =
  | "soc2_report"
  | "iso27001_cert"
  | "pentest_report"
  | "privacy_policy"
  | "insurance_cert"
  | "contract"
  | "questionnaire_response"
  | "security_policy"
  | "other";

export type MappingVerification = "pending" | "verified" | "rejected";

export interface EvidenceExtraction {
  id: string;
  field_name: string;
  field_value: string;
  confidence: number;
  page_number: number | null;
  source_text: string | null;
}

export interface EvidenceControlMapping {
  id: string;
  evidence_id: string;
  control_id: string;
  control_name: string;
  framework_name: string;
  relevance_score: number;
  verification: MappingVerification;
  verified_by: string | null;
  verified_at: string | null;
}

export interface Evidence {
  id: string;
  tenant_id: string;
  vendor_id: string;
  vendor_name: string;
  filename: string;
  file_size: number;
  mime_type: string;
  document_type: EvidenceType;
  status: EvidenceStatus;
  uploaded_by: string | null;
  processed_at: string | null;
  extraction_count: number;
  mapping_count: number;
  created_at: string;
  updated_at: string;
}

export interface EvidenceDetail extends Evidence {
  extractions: EvidenceExtraction[];
  mappings: EvidenceControlMapping[];
}

export interface EvidenceListResponse {
  items: Evidence[];
  total: number;
  page: number;
  page_size: number;
}

export interface EvidenceFilters {
  vendor_id?: string;
  status?: EvidenceStatus | "";
  document_type?: EvidenceType | "";
  search?: string;
  sort_by?: string;
  sort_order?: "asc" | "desc";
  page?: number;
  page_size?: number;
}

export interface UploadUrlRequest {
  vendor_id: string;
  filename: string;
  file_size: number;
  mime_type: string;
}

export interface UploadUrlResponse {
  upload_url: string;
  evidence_id: string;
}

export const EVIDENCE_STATUSES: EvidenceStatus[] = [
  "pending",
  "processing",
  "processed",
  "failed",
  "archived",
];

export const EVIDENCE_TYPES: EvidenceType[] = [
  "soc2_report",
  "iso27001_cert",
  "pentest_report",
  "privacy_policy",
  "insurance_cert",
  "contract",
  "questionnaire_response",
  "security_policy",
  "other",
];

export const EVIDENCE_TYPE_LABELS: Record<EvidenceType, string> = {
  soc2_report: "SOC 2 Report",
  iso27001_cert: "ISO 27001 Certificate",
  pentest_report: "Pentest Report",
  privacy_policy: "Privacy Policy",
  insurance_cert: "Insurance Certificate",
  contract: "Contract",
  questionnaire_response: "Questionnaire Response",
  security_policy: "Security Policy",
  other: "Other",
};

export const EVIDENCE_STATUS_LABELS: Record<EvidenceStatus, string> = {
  pending: "Pending",
  processing: "Processing",
  processed: "Processed",
  failed: "Failed",
  archived: "Archived",
};
