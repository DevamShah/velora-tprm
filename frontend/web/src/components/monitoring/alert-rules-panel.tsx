"use client";

import React, { useState } from "react";
import {
  Plus,
  Settings2,
  Loader2,
  ToggleLeft,
  ToggleRight,
  Pencil,
} from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import { EmptyState } from "@/components/empty-state";
import {
  useAlertRules,
  useCreateAlertRule,
  useUpdateAlertRule,
} from "@/hooks/use-monitoring";
import { ALERT_PRIORITIES, ALERT_PRIORITY_LABELS } from "@/types/monitoring";
import type {
  AlertRule,
  AlertRuleCondition,
  AlertRuleAction,
  AlertPriority,
} from "@/types/monitoring";

export function AlertRulesPanel() {
  const { rules, isLoading, error, refetch } = useAlertRules();
  const [createOpen, setCreateOpen] = useState(false);
  const [editRule, setEditRule] = useState<AlertRule | null>(null);

  if (isLoading) {
    return (
      <div className="space-y-3">
        {Array.from({ length: 3 }).map((_, i) => (
          <Skeleton key={i} className="h-20 w-full rounded-lg" />
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-8 text-text-muted text-sm">
        Failed to load alert rules: {error}
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-text-primary">
          Alert Rules ({rules.length})
        </h3>
        <Button size="sm" onClick={() => setCreateOpen(true)}>
          <Plus className="h-4 w-4 mr-1" />
          New Rule
        </Button>
      </div>

      {rules.length === 0 ? (
        <EmptyState
          icon={Settings2}
          title="No alert rules"
          description="Create rules to automatically generate alerts based on vendor signals."
          actionLabel="Create Rule"
          onAction={() => setCreateOpen(true)}
        />
      ) : (
        <div className="space-y-3">
          {rules.map((rule) => (
            <Card key={rule.id}>
              <CardContent className="py-4">
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-sm font-medium text-text-primary">
                        {rule.name}
                      </span>
                      {rule.enabled ? (
                        <Badge variant="low" className="text-[10px]">
                          <ToggleRight className="h-3 w-3 mr-0.5" />
                          Active
                        </Badge>
                      ) : (
                        <Badge variant="secondary" className="text-[10px]">
                          <ToggleLeft className="h-3 w-3 mr-0.5" />
                          Disabled
                        </Badge>
                      )}
                    </div>
                    {rule.description && (
                      <p className="text-xs text-text-muted line-clamp-1">
                        {rule.description}
                      </p>
                    )}
                    <div className="flex items-center gap-3 mt-2 text-xs text-text-muted">
                      <span>
                        {rule.conditions.length} condition{rule.conditions.length !== 1 ? "s" : ""}
                      </span>
                      <span>
                        {rule.actions.length} action{rule.actions.length !== 1 ? "s" : ""}
                      </span>
                    </div>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-8 w-8"
                    onClick={() => setEditRule(rule)}
                  >
                    <Pencil className="h-3.5 w-3.5" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      <RuleDialog
        open={createOpen || !!editRule}
        onOpenChange={(v) => {
          if (!v) {
            setCreateOpen(false);
            setEditRule(null);
          }
        }}
        existingRule={editRule}
        onSuccess={() => {
          setCreateOpen(false);
          setEditRule(null);
          refetch();
        }}
      />
    </div>
  );
}

/* --- Rule Create / Edit Dialog --- */

interface RuleDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  existingRule: AlertRule | null;
  onSuccess: () => void;
}

function RuleDialog({
  open,
  onOpenChange,
  existingRule,
  onSuccess,
}: RuleDialogProps) {
  const { createRule, isLoading: creating } = useCreateAlertRule();
  const { updateRule, isLoading: updating } = useUpdateAlertRule();

  const [name, setName] = useState(existingRule?.name || "");
  const [description, setDescription] = useState(existingRule?.description || "");
  const [enabled, setEnabled] = useState(existingRule?.enabled ?? true);
  const [condField, setCondField] = useState("source");
  const [condOperator, setCondOperator] = useState<"eq" | "contains">("eq");
  const [condValue, setCondValue] = useState("");
  const [actionPriority, setActionPriority] = useState<AlertPriority>("p2");

  // Reset form when dialog opens/closes or rule changes
  React.useEffect(() => {
    if (existingRule) {
      setName(existingRule.name);
      setDescription(existingRule.description || "");
      setEnabled(existingRule.enabled);
      if (existingRule.conditions.length > 0) {
        setCondField(existingRule.conditions[0].field);
        setCondOperator(existingRule.conditions[0].operator as "eq" | "contains");
        setCondValue(existingRule.conditions[0].value);
      }
      if (existingRule.actions.length > 0 && existingRule.actions[0].priority) {
        setActionPriority(existingRule.actions[0].priority);
      }
    } else {
      setName("");
      setDescription("");
      setEnabled(true);
      setCondField("source");
      setCondOperator("eq");
      setCondValue("");
      setActionPriority("p2");
    }
  }, [existingRule, open]);

  const saving = creating || updating;

  async function handleSave() {
    if (!name.trim()) {
      toast.error("Rule name is required");
      return;
    }

    const conditions: AlertRuleCondition[] = condValue
      ? [{ field: condField, operator: condOperator, value: condValue }]
      : [];
    const actions: AlertRuleAction[] = [
      { type: "create_alert", priority: actionPriority },
    ];

    try {
      if (existingRule) {
        await updateRule(existingRule.id, {
          name,
          description: description || undefined,
          enabled,
          conditions,
          actions,
        });
        toast.success("Rule updated");
      } else {
        await createRule({
          name,
          description: description || undefined,
          enabled,
          conditions,
          actions,
        });
        toast.success("Rule created");
      }
      onSuccess();
    } catch (err) {
      toast.error(
        (err as { message?: string }).message || "Failed to save rule"
      );
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>
            {existingRule ? "Edit Alert Rule" : "Create Alert Rule"}
          </DialogTitle>
          <DialogDescription>
            Define conditions that trigger automated alerts.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 mt-4">
          <div>
            <label className="text-sm font-medium text-text-primary mb-1.5 block">
              Rule Name
            </label>
            <Input
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g., Critical breach detection"
            />
          </div>

          <div>
            <label className="text-sm font-medium text-text-primary mb-1.5 block">
              Description
            </label>
            <Input
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Optional description"
            />
          </div>

          <div className="grid grid-cols-3 gap-2">
            <div>
              <label className="text-xs font-medium text-text-muted mb-1 block">
                Field
              </label>
              <Select value={condField} onValueChange={setCondField}>
                <SelectTrigger className="h-9">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="source">Source</SelectItem>
                  <SelectItem value="vendor_name">Vendor</SelectItem>
                  <SelectItem value="title">Title</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <label className="text-xs font-medium text-text-muted mb-1 block">
                Operator
              </label>
              <Select
                value={condOperator}
                onValueChange={(v) => setCondOperator(v as "eq" | "contains")}
              >
                <SelectTrigger className="h-9">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="eq">Equals</SelectItem>
                  <SelectItem value="contains">Contains</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <label className="text-xs font-medium text-text-muted mb-1 block">
                Value
              </label>
              <Input
                value={condValue}
                onChange={(e) => setCondValue(e.target.value)}
                placeholder="Value"
                className="h-9"
              />
            </div>
          </div>

          <div>
            <label className="text-sm font-medium text-text-primary mb-1.5 block">
              Alert Priority
            </label>
            <Select
              value={actionPriority}
              onValueChange={(v) => setActionPriority(v as AlertPriority)}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {ALERT_PRIORITIES.map((p) => (
                  <SelectItem key={p} value={p}>
                    {ALERT_PRIORITY_LABELS[p]}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>

        <DialogFooter>
          <Button
            variant="outline"
            onClick={() => onOpenChange(false)}
            disabled={saving}
          >
            Cancel
          </Button>
          <Button onClick={handleSave} disabled={saving || !name.trim()}>
            {saving ? (
              <>
                <Loader2 className="h-4 w-4 mr-1 animate-spin" />
                Saving...
              </>
            ) : existingRule ? (
              "Update Rule"
            ) : (
              "Create Rule"
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
