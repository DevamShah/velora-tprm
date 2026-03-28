import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium transition-colors",
  {
    variants: {
      variant: {
        default: "bg-accent-primary/10 text-accent-primary",
        secondary: "bg-surface-main text-text-secondary",
        destructive: "bg-accent-error/10 text-accent-error",
        outline: "border border-surface-card-border text-text-secondary",
        critical: "bg-risk-critical/10 text-risk-critical",
        high: "bg-risk-high/10 text-risk-high",
        medium: "bg-risk-medium/10 text-amber-700",
        low: "bg-risk-low/10 text-risk-low",
        minimal: "bg-risk-minimal/10 text-risk-minimal",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
);

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return (
    <div className={cn(badgeVariants({ variant }), className)} {...props} />
  );
}

export { Badge, badgeVariants };
