"use client";

import React, { useState } from "react";
import { useRouter, useParams } from "next/navigation";
import {
  ArrowLeft,
  ChevronRight,
  ChevronDown,
  Shield,
  Link2,
  Layers,
  BookOpen,
  AlertTriangle,
} from "lucide-react";
import { PageHeader } from "@/components/page-header";
import { PageLoadingSkeleton } from "@/components/loading-skeleton";
import { EmptyState } from "@/components/empty-state";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Skeleton } from "@/components/ui/skeleton";
import { Progress } from "@/components/ui/progress";
import {
  useFramework,
  useFrameworkClauses,
  useClauseMappings,
  useUnifiedControls,
} from "@/hooks/use-frameworks";
import type { ClauseTreeNode, CrossFrameworkMapping, UnifiedControl } from "@/types/framework";

export default function FrameworkDetailPage() {
  const router = useRouter();
  const params = useParams();
  const frameworkId = params.id as string;

  const { framework, isLoading, error } = useFramework(frameworkId);

  if (isLoading) return <PageLoadingSkeleton />;

  if (error || !framework) {
    return (
      <EmptyState
        icon={Shield}
        title="Framework not found"
        description={error || "The requested framework could not be loaded."}
        actionLabel="Back to Frameworks"
        onAction={() => router.push("/frameworks")}
      />
    );
  }

  return (
    <>
      <div className="flex items-center gap-2 mb-4">
        <Button variant="ghost" size="sm" onClick={() => router.push("/frameworks")}>
          <ArrowLeft className="h-4 w-4 mr-1" />
          Frameworks
        </Button>
      </div>

      <PageHeader
        title={framework.name}
        description={`Version ${framework.version} — ${framework.clause_count} clauses`}
        actions={
          <Badge
            variant={framework.status === "active" ? "default" : "secondary"}
            className="capitalize"
          >
            {framework.status}
          </Badge>
        }
      />

      {framework.description && (
        <p className="text-sm text-text-secondary mb-6 -mt-2">
          {framework.description}
        </p>
      )}

      <Tabs defaultValue="clauses">
        <TabsList>
          <TabsTrigger value="clauses">
            <BookOpen className="h-3.5 w-3.5 mr-1.5" />
            Clauses
          </TabsTrigger>
          <TabsTrigger value="mappings">
            <Link2 className="h-3.5 w-3.5 mr-1.5" />
            Mappings
          </TabsTrigger>
          <TabsTrigger value="controls">
            <Layers className="h-3.5 w-3.5 mr-1.5" />
            Unified Controls
          </TabsTrigger>
        </TabsList>

        <TabsContent value="clauses">
          <ClausesTab frameworkId={frameworkId} />
        </TabsContent>

        <TabsContent value="mappings">
          <MappingsTab frameworkId={frameworkId} />
        </TabsContent>

        <TabsContent value="controls">
          <ControlsTab />
        </TabsContent>
      </Tabs>
    </>
  );
}

/* --- Clauses Tab --- */

function ClausesTab({ frameworkId }: { frameworkId: string }) {
  const { clauses, isLoading, error } = useFrameworkClauses(frameworkId);

  if (isLoading) {
    return (
      <div className="space-y-2 animate-fade-in">
        {Array.from({ length: 8 }).map((_, i) => (
          <Skeleton key={i} className="h-10 w-full rounded-lg" />
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <EmptyState
        icon={AlertTriangle}
        title="Failed to load clauses"
        description={error}
      />
    );
  }

  if (!clauses || clauses.length === 0) {
    return (
      <EmptyState
        icon={BookOpen}
        title="No clauses"
        description="This framework has no clauses defined yet."
      />
    );
  }

  return (
    <Card>
      <CardContent className="pt-4 pb-2">
        <div className="divide-y divide-surface-card-border">
          {clauses.map((clause) => (
            <ClauseNode key={clause.id} clause={clause} depth={0} />
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

function ClauseNode({ clause, depth }: { clause: ClauseTreeNode; depth: number }) {
  const [expanded, setExpanded] = useState(depth === 0);
  const hasChildren = clause.children && clause.children.length > 0;

  return (
    <div>
      <button
        className="flex items-start gap-2 w-full text-left py-2.5 px-2 rounded-md hover:bg-surface-main/50 transition-colors"
        style={{ paddingLeft: `${depth * 20 + 8}px` }}
        onClick={() => hasChildren && setExpanded(!expanded)}
      >
        {hasChildren ? (
          expanded ? (
            <ChevronDown className="h-4 w-4 text-text-muted mt-0.5 shrink-0" />
          ) : (
            <ChevronRight className="h-4 w-4 text-text-muted mt-0.5 shrink-0" />
          )
        ) : (
          <span className="w-4 shrink-0" />
        )}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <span className="text-xs font-mono text-accent-primary font-medium">
              {clause.clause_number}
            </span>
            <span className="text-sm font-medium text-text-primary truncate">
              {clause.title}
            </span>
          </div>
          {clause.description && (
            <p className="text-xs text-text-muted mt-0.5 line-clamp-1">
              {clause.description}
            </p>
          )}
        </div>
      </button>
      {expanded && hasChildren && (
        <div className="animate-fade-in">
          {clause.children.map((child) => (
            <ClauseNode key={child.id} clause={child} depth={depth + 1} />
          ))}
        </div>
      )}
    </div>
  );
}

/* --- Mappings Tab --- */

function MappingsTab({ frameworkId }: { frameworkId: string }) {
  const { clauses, isLoading: clausesLoading } = useFrameworkClauses(frameworkId);
  const [selectedClauseId, setSelectedClauseId] = useState<string>("");

  if (clausesLoading) {
    return (
      <div className="space-y-2 animate-fade-in">
        {Array.from({ length: 4 }).map((_, i) => (
          <Skeleton key={i} className="h-10 w-full rounded-lg" />
        ))}
      </div>
    );
  }

  const flatClauses = flattenClauses(clauses || []);

  return (
    <div className="space-y-4">
      <Card>
        <CardContent className="pt-6">
          <label className="text-xs font-semibold text-text-muted uppercase tracking-wider mb-2 block">
            Select a clause to view cross-framework mappings
          </label>
          <select
            className="w-full rounded-lg border border-surface-card-border bg-white px-3 py-2 text-sm text-text-primary focus:outline-none focus:ring-2 focus:ring-accent-primary/20 focus:border-accent-primary"
            value={selectedClauseId}
            onChange={(e) => setSelectedClauseId(e.target.value)}
          >
            <option value="">Choose a clause...</option>
            {flatClauses.map((c) => (
              <option key={c.id} value={c.id}>
                {c.clause_number} — {c.title}
              </option>
            ))}
          </select>
        </CardContent>
      </Card>

      {selectedClauseId && (
        <MappingResults frameworkId={frameworkId} clauseId={selectedClauseId} />
      )}
    </div>
  );
}

function MappingResults({
  frameworkId,
  clauseId,
}: {
  frameworkId: string;
  clauseId: string;
}) {
  const { mappings, isLoading, error } = useClauseMappings(frameworkId, clauseId);

  if (isLoading) {
    return (
      <div className="space-y-2 animate-fade-in">
        {Array.from({ length: 3 }).map((_, i) => (
          <Skeleton key={i} className="h-14 w-full rounded-lg" />
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <EmptyState
        icon={AlertTriangle}
        title="Failed to load mappings"
        description={error}
      />
    );
  }

  if (!mappings || mappings.length === 0) {
    return (
      <EmptyState
        icon={Link2}
        title="No mappings found"
        description="This clause has no cross-framework mappings."
      />
    );
  }

  return (
    <Card>
      <CardContent className="p-0">
        <div className="rounded-xl overflow-hidden">
          <Table>
            <TableHeader>
              <TableRow className="hover:bg-transparent">
                <TableHead>Target Framework</TableHead>
                <TableHead>Clause</TableHead>
                <TableHead>Title</TableHead>
                <TableHead className="w-[100px]">Type</TableHead>
                <TableHead className="w-[140px]">Confidence</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {mappings.map((mapping) => (
                <MappingRow key={mapping.id} mapping={mapping} />
              ))}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  );
}

function MappingRow({ mapping }: { mapping: CrossFrameworkMapping }) {
  const confidencePercent = Math.round(mapping.confidence * 100);

  return (
    <TableRow>
      <TableCell className="font-medium text-text-primary text-sm">
        {mapping.target_framework_name}
      </TableCell>
      <TableCell>
        <span className="text-xs font-mono text-accent-primary">
          {mapping.target_clause_number}
        </span>
      </TableCell>
      <TableCell className="text-sm text-text-secondary">
        {mapping.target_clause_title}
      </TableCell>
      <TableCell>
        <Badge variant="outline" className="text-xs capitalize">
          {mapping.mapping_type}
        </Badge>
      </TableCell>
      <TableCell>
        <div className="flex items-center gap-2">
          <Progress value={confidencePercent} className="h-1.5 flex-1" />
          <span className="text-xs font-medium text-text-primary w-8 text-right">
            {confidencePercent}%
          </span>
        </div>
      </TableCell>
    </TableRow>
  );
}

/* --- Controls Tab --- */

function ControlsTab() {
  const { controls, isLoading, error } = useUnifiedControls();

  if (isLoading) {
    return (
      <div className="space-y-2 animate-fade-in">
        {Array.from({ length: 6 }).map((_, i) => (
          <Skeleton key={i} className="h-14 w-full rounded-lg" />
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <EmptyState
        icon={AlertTriangle}
        title="Failed to load controls"
        description={error}
      />
    );
  }

  if (!controls || controls.length === 0) {
    return (
      <EmptyState
        icon={Layers}
        title="No unified controls"
        description="Unified controls will appear once framework mappings are configured."
      />
    );
  }

  return (
    <Card>
      <CardContent className="p-0">
        <div className="rounded-xl overflow-hidden">
          <Table>
            <TableHeader>
              <TableRow className="hover:bg-transparent">
                <TableHead className="w-[120px]">Control ID</TableHead>
                <TableHead>Title</TableHead>
                <TableHead>Category</TableHead>
                <TableHead className="w-[100px]">Mapped</TableHead>
                <TableHead>Frameworks</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {controls.map((control) => (
                <ControlRow key={control.id} control={control} />
              ))}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  );
}

function ControlRow({ control }: { control: UnifiedControl }) {
  return (
    <TableRow>
      <TableCell>
        <span className="text-xs font-mono text-accent-primary font-medium">
          {control.control_id}
        </span>
      </TableCell>
      <TableCell>
        <div>
          <span className="text-sm font-medium text-text-primary">
            {control.title}
          </span>
          {control.description && (
            <p className="text-xs text-text-muted line-clamp-1 mt-0.5">
              {control.description}
            </p>
          )}
        </div>
      </TableCell>
      <TableCell>
        <Badge variant="outline" className="text-xs capitalize">
          {control.category}
        </Badge>
      </TableCell>
      <TableCell className="text-sm text-text-secondary text-center">
        {control.mapped_clauses}
      </TableCell>
      <TableCell>
        <div className="flex flex-wrap gap-1">
          {control.framework_coverage.map((fw) => (
            <Badge key={fw} variant="secondary" className="text-[10px] px-1.5 py-0">
              {fw}
            </Badge>
          ))}
        </div>
      </TableCell>
    </TableRow>
  );
}

/* --- Helpers --- */

function flattenClauses(nodes: ClauseTreeNode[]): ClauseTreeNode[] {
  const result: ClauseTreeNode[] = [];
  function walk(list: ClauseTreeNode[]) {
    for (const node of list) {
      result.push(node);
      if (node.children && node.children.length > 0) {
        walk(node.children);
      }
    }
  }
  walk(nodes);
  return result;
}
