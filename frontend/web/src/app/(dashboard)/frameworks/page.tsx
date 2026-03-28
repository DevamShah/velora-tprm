"use client";

import React from "react";
import { useRouter } from "next/navigation";
import { Shield, BookOpen, ChevronRight } from "lucide-react";
import { PageHeader } from "@/components/page-header";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { EmptyState } from "@/components/empty-state";
import { Skeleton } from "@/components/ui/skeleton";
import { useFrameworks } from "@/hooks/use-frameworks";
import type { Framework, FrameworkStatus } from "@/types/framework";

function getStatusVariant(status: FrameworkStatus): "default" | "secondary" | "outline" | "destructive" {
  switch (status) {
    case "active":
      return "default";
    case "draft":
      return "secondary";
    case "deprecated":
      return "destructive";
    case "archived":
      return "outline";
    default:
      return "outline";
  }
}

function FrameworkCard({ framework, onClick }: { framework: Framework; onClick: () => void }) {
  return (
    <Card
      className="cursor-pointer group hover:shadow-md hover:border-accent-primary/30 transition-all duration-200"
      onClick={onClick}
    >
      <CardContent className="pt-6">
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center justify-center w-10 h-10 rounded-lg bg-accent-primary/10">
            <Shield className="w-5 h-5 text-accent-primary" />
          </div>
          <Badge variant={getStatusVariant(framework.status)} className="text-xs capitalize">
            {framework.status}
          </Badge>
        </div>

        <h3 className="text-sm font-semibold text-text-primary mb-0.5 group-hover:text-accent-primary transition-colors">
          {framework.name}
        </h3>

        {framework.description && (
          <p className="text-xs text-text-muted line-clamp-2 mb-3">
            {framework.description}
          </p>
        )}

        <div className="flex items-center justify-between pt-3 border-t border-surface-card-border">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-1.5">
              <BookOpen className="h-3.5 w-3.5 text-text-muted" />
              <span className="text-xs text-text-secondary">
                {framework.clause_count} clause{framework.clause_count !== 1 ? "s" : ""}
              </span>
            </div>
            <span className="text-xs text-text-muted">v{framework.version}</span>
          </div>
          <ChevronRight className="h-4 w-4 text-text-muted group-hover:text-accent-primary transition-colors" />
        </div>
      </CardContent>
    </Card>
  );
}

function FrameworkGridSkeleton() {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 animate-fade-in">
      {Array.from({ length: 6 }).map((_, i) => (
        <Card key={i}>
          <CardContent className="pt-6 space-y-3">
            <div className="flex items-start justify-between">
              <Skeleton className="h-10 w-10 rounded-lg" />
              <Skeleton className="h-5 w-16 rounded-full" />
            </div>
            <Skeleton className="h-4 w-3/4" />
            <Skeleton className="h-3 w-full" />
            <Skeleton className="h-3 w-2/3" />
            <div className="pt-3 border-t border-surface-card-border">
              <Skeleton className="h-3 w-24" />
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}

export default function FrameworksPage() {
  const router = useRouter();
  const { frameworks, isLoading, error } = useFrameworks();

  return (
    <>
      <PageHeader
        title="Frameworks"
        description="Manage compliance frameworks and control mappings"
      />

      {isLoading ? (
        <FrameworkGridSkeleton />
      ) : error ? (
        <EmptyState
          icon={Shield}
          title="Failed to load frameworks"
          description={error}
        />
      ) : frameworks.length === 0 ? (
        <EmptyState
          icon={Shield}
          title="No frameworks configured"
          description="Compliance frameworks will appear here once configured in the backend."
        />
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {frameworks.map((fw) => (
            <FrameworkCard
              key={fw.id}
              framework={fw}
              onClick={() => router.push(`/frameworks/${fw.id}`)}
            />
          ))}
        </div>
      )}
    </>
  );
}
