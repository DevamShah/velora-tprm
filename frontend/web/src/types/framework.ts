// Framework domain types — maps 1:1 to backend API schema

export type FrameworkStatus = "active" | "draft" | "deprecated" | "archived";

export interface Framework {
  id: string;
  tenant_id: string;
  name: string;
  short_name: string;
  version: string;
  description: string | null;
  authority: string | null;
  status: FrameworkStatus;
  clause_count: number;
  created_at: string;
  updated_at: string;
}

export interface FrameworkDetail extends Framework {
  clause_count: number;
}

export interface FrameworkListResponse {
  items: Framework[];
  total: number;
}

export interface ClauseTreeNode {
  id: string;
  framework_id: string;
  clause_number: string;
  title: string;
  description: string | null;
  depth: number;
  parent_id: string | null;
  children: ClauseTreeNode[];
}

export interface ClauseListResponse {
  clauses: ClauseTreeNode[];
}

export interface CrossFrameworkMapping {
  id: string;
  source_clause_id: string;
  source_clause_number: string;
  source_framework_name: string;
  target_clause_id: string;
  target_clause_number: string;
  target_clause_title: string;
  target_framework_name: string;
  confidence: number;
  mapping_type: string;
}

export interface MappingListResponse {
  mappings: CrossFrameworkMapping[];
}

export interface UnifiedControl {
  id: string;
  control_id: string;
  title: string;
  description: string | null;
  category: string;
  mapped_clauses: number;
  framework_coverage: string[];
}

export interface UnifiedControlListResponse {
  controls: UnifiedControl[];
}

export const FRAMEWORK_STATUSES: FrameworkStatus[] = [
  "active",
  "draft",
  "deprecated",
  "archived",
];
