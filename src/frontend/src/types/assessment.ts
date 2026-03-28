// Assessment domain types — maps 1:1 to backend API schema

export type AssessmentStatus =
  | "draft"
  | "distributed"
  | "in_progress"
  | "submitted"
  | "under_review"
  | "completed"
  | "cancelled";

export type QuestionType =
  | "yes_no"
  | "multiple_choice"
  | "text"
  | "file_upload"
  | "scale"
  | "date";

export type ReviewStatus =
  | "pending"
  | "accepted"
  | "modified"
  | "flagged";

export interface AssessmentTemplate {
  id: string;
  name: string;
  description: string | null;
  question_count: number;
  created_at: string;
  updated_at: string;
}

export interface AssessmentQuestion {
  id: string;
  section: string;
  question_text: string;
  question_type: QuestionType;
  options: string[] | null;
  required: boolean;
  weight: number;
  order: number;
}

export interface AssessmentResponse {
  id: string;
  question_id: string;
  question: AssessmentQuestion;
  response_value: string | null;
  confidence_score: number | null;
  review_status: ReviewStatus;
  reviewer_notes: string | null;
  responded_at: string | null;
  reviewed_at: string | null;
}

export interface Assessment {
  id: string;
  tenant_id: string;
  vendor_id: string;
  vendor_name: string;
  template_id: string;
  template_name: string;
  title: string;
  description: string | null;
  status: AssessmentStatus;
  score: number | null;
  due_date: string | null;
  distributed_at: string | null;
  submitted_at: string | null;
  completed_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface AssessmentDetail extends Assessment {
  responses: AssessmentResponse[];
  template: AssessmentTemplate;
  vendor: {
    id: string;
    name: string;
    domain: string | null;
    tier: string;
    status: string;
  };
}

export interface AssessmentListResponse {
  items: Assessment[];
  total: number;
  page: number;
  page_size: number;
}

export interface AssessmentFilters {
  status?: AssessmentStatus | "";
  vendor_id?: string;
  template_id?: string;
  search?: string;
  sort_by?: string;
  sort_order?: "asc" | "desc";
  page?: number;
  page_size?: number;
}

export interface CreateAssessmentPayload {
  vendor_id: string;
  template_id: string;
  title: string;
  description?: string;
  due_date?: string;
}

export interface UpdateResponsePayload {
  review_status: ReviewStatus;
  reviewer_notes?: string;
}

export interface ReviewQueueItem {
  id: string;
  assessment_id: string;
  assessment_title: string;
  vendor_name: string;
  question_text: string;
  question_section: string;
  response_value: string | null;
  confidence_score: number | null;
  review_status: ReviewStatus;
  submitted_at: string | null;
}

export interface ReviewQueueResponse {
  items: ReviewQueueItem[];
  total: number;
}

export const ASSESSMENT_STATUSES: AssessmentStatus[] = [
  "draft",
  "distributed",
  "in_progress",
  "submitted",
  "under_review",
  "completed",
  "cancelled",
];

export const QUESTION_TYPES: QuestionType[] = [
  "yes_no",
  "multiple_choice",
  "text",
  "file_upload",
  "scale",
  "date",
];

export const REVIEW_STATUSES: ReviewStatus[] = [
  "pending",
  "accepted",
  "modified",
  "flagged",
];
