import { cn } from "@/lib/utils";

function getRiskColor(score: number): string {
  if (score >= 80) return "text-risk-critical";
  if (score >= 60) return "text-risk-high";
  if (score >= 40) return "text-amber-700";
  return "text-risk-low";
}

function getRiskBg(score: number): string {
  if (score >= 80) return "bg-risk-critical/10";
  if (score >= 60) return "bg-risk-high/10";
  if (score >= 40) return "bg-risk-medium/10";
  return "bg-risk-low/10";
}

function getRiskLabel(score: number): string {
  if (score >= 80) return "Critical";
  if (score >= 60) return "High";
  if (score >= 40) return "Medium";
  return "Low";
}

interface VendorRiskScoreProps {
  score: number | null;
  label?: string;
  showLabel?: boolean;
  size?: "sm" | "md" | "lg";
  className?: string;
}

export function VendorRiskScore({
  score,
  label,
  showLabel = false,
  size = "sm",
  className,
}: VendorRiskScoreProps) {
  if (score === null || score === undefined) {
    return <span className="text-text-muted text-sm">--</span>;
  }

  const sizeClasses = {
    sm: "text-sm font-medium",
    md: "text-lg font-semibold",
    lg: "text-2xl font-bold",
  };

  return (
    <div className={cn("flex flex-col items-start gap-0.5", className)}>
      {label && (
        <span className="text-xs text-text-muted">{label}</span>
      )}
      <div className="flex items-center gap-2">
        <span
          className={cn(
            "inline-flex items-center justify-center rounded-md px-2 py-0.5",
            getRiskBg(score),
            getRiskColor(score),
            sizeClasses[size]
          )}
        >
          {score}
        </span>
        {showLabel && (
          <span className={cn("text-xs", getRiskColor(score))}>
            {getRiskLabel(score)}
          </span>
        )}
      </div>
    </div>
  );
}
