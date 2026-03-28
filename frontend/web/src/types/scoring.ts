// Scoring domain types — maps 1:1 to backend API schema

export type ScoreTier = "critical" | "high" | "medium" | "low" | "minimal";

export interface ScoringDimension {
  name: string;
  weight: number;
  description: string | null;
}

export interface ScoringModel {
  id: string;
  tenant_id: string;
  name: string;
  description: string | null;
  is_default: boolean;
  dimensions: ScoringDimension[];
  created_at: string;
  updated_at: string;
}

export interface ScoringModelListResponse {
  items: ScoringModel[];
  total: number;
}

export interface CreateScoringModelPayload {
  name: string;
  description?: string;
  is_default?: boolean;
  dimensions: ScoringDimension[];
}

export interface DimensionScore {
  dimension: string;
  score: number;
  weight: number;
  weighted_score: number;
}

export interface ScoreBreakdown {
  vendor_id: string;
  overall_score: number;
  tier: ScoreTier;
  dimensions: DimensionScore[];
  calculated_at: string;
}

export interface VendorScore {
  vendor_id: string;
  vendor_name: string;
  overall_score: number;
  tier: ScoreTier;
  dimensions: DimensionScore[];
  last_calculated: string;
}

export interface ScoreHistoryItem {
  id: string;
  vendor_id: string;
  overall_score: number;
  tier: ScoreTier;
  dimensions: DimensionScore[];
  calculated_at: string;
  triggered_by: string | null;
}

export interface ScoreHistoryResponse {
  items: ScoreHistoryItem[];
}

export interface PortfolioSummary {
  average_score: number;
  vendor_count: number;
  tier_distribution: Record<string, number>;
  risk_distribution: Record<string, number>;
}

export const SCORE_TIERS: ScoreTier[] = [
  "critical",
  "high",
  "medium",
  "low",
  "minimal",
];

export function getScoreColor(score: number): string {
  if (score >= 80) return "#10b981"; // green — low risk
  if (score >= 60) return "#f59e0b"; // amber — medium risk
  if (score >= 40) return "#f97316"; // orange — high risk
  return "#ef4444"; // red — critical risk
}

export function getScoreLabel(score: number): string {
  if (score >= 80) return "Low Risk";
  if (score >= 60) return "Medium Risk";
  if (score >= 40) return "High Risk";
  return "Critical Risk";
}

export function getTierColor(tier: ScoreTier): string {
  switch (tier) {
    case "minimal":
      return "#10b981";
    case "low":
      return "#22c55e";
    case "medium":
      return "#f59e0b";
    case "high":
      return "#f97316";
    case "critical":
      return "#ef4444";
    default:
      return "#6b7280";
  }
}
