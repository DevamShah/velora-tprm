"use client";

import React, { useState } from "react";
import {
  Settings,
  Scale,
  Bell,
  GitBranch,
  AlertTriangle,
  Save,
  Loader2,
} from "lucide-react";
import { toast } from "sonner";
import { PageHeader } from "@/components/page-header";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { useScoringModels } from "@/hooks/use-scoring";
import { useNotificationPreferences } from "@/hooks/use-communications";
import { cn } from "@/lib/utils";

export default function SettingsPage() {
  return (
    <>
      <PageHeader
        title="Settings"
        description="Configure platform preferences and defaults"
      />

      <Tabs defaultValue="general">
        <TabsList>
          <TabsTrigger value="general">
            <Settings className="h-3.5 w-3.5 mr-1" />
            General
          </TabsTrigger>
          <TabsTrigger value="scoring">
            <Scale className="h-3.5 w-3.5 mr-1" />
            Scoring
          </TabsTrigger>
          <TabsTrigger value="workflow">
            <GitBranch className="h-3.5 w-3.5 mr-1" />
            Workflow
          </TabsTrigger>
          <TabsTrigger value="notifications">
            <Bell className="h-3.5 w-3.5 mr-1" />
            Notifications
          </TabsTrigger>
        </TabsList>

        <TabsContent value="general" className="mt-4">
          <GeneralSettings />
        </TabsContent>

        <TabsContent value="scoring" className="mt-4">
          <ScoringSettings />
        </TabsContent>

        <TabsContent value="workflow" className="mt-4">
          <WorkflowSettings />
        </TabsContent>

        <TabsContent value="notifications" className="mt-4">
          <NotificationSettings />
        </TabsContent>
      </Tabs>
    </>
  );
}

/* --- General Settings --- */

function GeneralSettings() {
  const [orgName, setOrgName] = useState("Acme Corp");
  const [timezone, setTimezone] = useState("UTC");

  return (
    <div className="space-y-4 max-w-2xl">
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Organization</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <label className="text-sm font-medium text-text-primary">
              Organization Name
            </label>
            <Input
              value={orgName}
              onChange={(e) => setOrgName(e.target.value)}
            />
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium text-text-primary">
              Timezone
            </label>
            <Select value={timezone} onValueChange={setTimezone}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="UTC">UTC</SelectItem>
                <SelectItem value="America/New_York">Eastern Time</SelectItem>
                <SelectItem value="America/Chicago">Central Time</SelectItem>
                <SelectItem value="America/Denver">Mountain Time</SelectItem>
                <SelectItem value="America/Los_Angeles">Pacific Time</SelectItem>
                <SelectItem value="Europe/London">London</SelectItem>
                <SelectItem value="Asia/Kolkata">India (IST)</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="pt-2">
            <Button size="sm">
              <Save className="w-3.5 h-3.5 mr-1" />
              Save Changes
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Data Retention</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <label className="text-sm font-medium text-text-primary">
              Audit Log Retention (days)
            </label>
            <Input type="number" defaultValue="365" className="w-32" />
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium text-text-primary">
              Communication Log Retention (days)
            </label>
            <Input type="number" defaultValue="180" className="w-32" />
          </div>
          <div className="pt-2">
            <Button size="sm">
              <Save className="w-3.5 h-3.5 mr-1" />
              Save Changes
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

/* --- Scoring Settings --- */

function ScoringSettings() {
  const { models, isLoading, error } = useScoringModels();
  const defaultModel = models.find((m) => m.is_default) || models[0];

  if (isLoading) {
    return (
      <div className="space-y-3 animate-fade-in max-w-2xl">
        <Skeleton className="h-5 w-48" />
        <Skeleton className="h-64 rounded-xl" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center gap-2 text-sm text-risk-high">
        <AlertTriangle className="h-4 w-4" />
        {error}
      </div>
    );
  }

  if (!defaultModel) {
    return (
      <Card className="max-w-2xl">
        <CardContent className="pt-5">
          <p className="text-sm text-text-muted">
            No scoring model configured. A default model will be created when
            scoring is first used.
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="max-w-2xl">
      <CardHeader>
        <div className="flex items-center gap-2">
          <Scale className="h-4 w-4 text-text-muted" />
          <CardTitle className="text-base">Scoring Configuration</CardTitle>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-center gap-3">
          <div>
            <p className="text-sm font-semibold text-text-primary">
              {defaultModel.name}
            </p>
            {defaultModel.description && (
              <p className="text-xs text-text-muted mt-0.5">
                {defaultModel.description}
              </p>
            )}
          </div>
          {defaultModel.is_default && (
            <Badge variant="default" className="text-xs">
              Default
            </Badge>
          )}
        </div>

        {defaultModel.dimensions && defaultModel.dimensions.length > 0 && (
          <div>
            <p className="text-xs font-semibold text-text-muted uppercase tracking-wider mb-2">
              Dimensions & Weights
            </p>
            <div className="rounded-lg border border-surface-card-border overflow-hidden">
              <table className="w-full text-sm">
                <thead>
                  <tr className="bg-surface-main/50">
                    <th className="text-left px-4 py-2 text-xs font-semibold text-text-muted">
                      Dimension
                    </th>
                    <th className="text-right px-4 py-2 text-xs font-semibold text-text-muted w-[100px]">
                      Weight
                    </th>
                    <th className="text-left px-4 py-2 text-xs font-semibold text-text-muted">
                      Description
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-surface-card-border">
                  {defaultModel.dimensions.map((dim) => (
                    <tr key={dim.name}>
                      <td className="px-4 py-2.5 font-medium text-text-primary capitalize">
                        {dim.name.replace(/_/g, " ")}
                      </td>
                      <td className="px-4 py-2.5 text-right">
                        <span className="inline-flex items-center justify-center rounded-md px-2 py-0.5 bg-accent-primary/10 text-accent-primary text-xs font-medium">
                          {(dim.weight * 100).toFixed(0)}%
                        </span>
                      </td>
                      <td className="px-4 py-2.5 text-text-secondary text-xs">
                        {dim.description || "--"}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <p className="text-xs text-text-muted mt-2">
              Read-only view. Editing scoring models will be available in a
              future release.
            </p>
          </div>
        )}

        {models.length > 1 && (
          <p className="text-xs text-text-muted">
            {models.length} scoring model{models.length !== 1 ? "s" : ""}{" "}
            configured
          </p>
        )}
      </CardContent>
    </Card>
  );
}

/* --- Workflow Settings --- */

function WorkflowSettings() {
  return (
    <div className="space-y-4 max-w-2xl">
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Assessment Workflow</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <label className="text-sm font-medium text-text-primary">
              Default Assessment SLA (days)
            </label>
            <Input type="number" defaultValue="30" className="w-32" />
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium text-text-primary">
              Auto-reassessment Interval (days)
            </label>
            <Input type="number" defaultValue="365" className="w-32" />
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium text-text-primary">
              Require Reviewer Sign-off
            </label>
            <Select defaultValue="yes">
              <SelectTrigger className="w-32">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="yes">Yes</SelectItem>
                <SelectItem value="no">No</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="pt-2">
            <Button size="sm">
              <Save className="w-3.5 h-3.5 mr-1" />
              Save Changes
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Finding Workflow</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <label className="text-sm font-medium text-text-primary">
              Critical Finding SLA (days)
            </label>
            <Input type="number" defaultValue="7" className="w-32" />
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium text-text-primary">
              High Finding SLA (days)
            </label>
            <Input type="number" defaultValue="14" className="w-32" />
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium text-text-primary">
              Medium Finding SLA (days)
            </label>
            <Input type="number" defaultValue="30" className="w-32" />
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium text-text-primary">
              Low Finding SLA (days)
            </label>
            <Input type="number" defaultValue="90" className="w-32" />
          </div>
          <div className="pt-2">
            <Button size="sm">
              <Save className="w-3.5 h-3.5 mr-1" />
              Save Changes
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

/* --- Notification Settings --- */

function NotificationSettings() {
  const { preferences, isLoading, error, updatePreferences } =
    useNotificationPreferences();
  const [isSaving, setIsSaving] = useState(false);

  if (isLoading) {
    return (
      <div className="space-y-3 animate-fade-in max-w-2xl">
        {Array.from({ length: 3 }).map((_, i) => (
          <Skeleton key={i} className="h-12 rounded-lg" />
        ))}
      </div>
    );
  }

  if (error || !preferences) {
    return (
      <Card className="max-w-2xl">
        <CardContent className="pt-5">
          <div className="flex items-center gap-2 text-sm text-risk-high">
            <AlertTriangle className="h-4 w-4" />
            {error || "Failed to load preferences"}
          </div>
        </CardContent>
      </Card>
    );
  }

  const handleSave = async () => {
    setIsSaving(true);
    try {
      await updatePreferences(preferences);
      toast.success("Notification preferences saved");
    } catch {
      toast.error("Failed to save preferences");
    } finally {
      setIsSaving(false);
    }
  };

  const toggleItems = [
    { key: "email_enabled" as const, label: "Email Notifications" },
    { key: "in_app_enabled" as const, label: "In-App Notifications" },
    { key: "alert_notifications" as const, label: "Alert Notifications" },
    {
      key: "assessment_notifications" as const,
      label: "Assessment Notifications",
    },
    {
      key: "finding_notifications" as const,
      label: "Finding Notifications",
    },
    {
      key: "vendor_notifications" as const,
      label: "Vendor Notifications",
    },
    {
      key: "system_notifications" as const,
      label: "System Notifications",
    },
  ];

  return (
    <Card className="max-w-2xl">
      <CardHeader>
        <CardTitle className="text-base">Notification Preferences</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {toggleItems.map((item) => (
          <div
            key={item.key}
            className="flex items-center justify-between py-2 border-b border-surface-card-border last:border-0"
          >
            <span className="text-sm text-text-primary">{item.label}</span>
            <button
              onClick={() => {
                const newPrefs = { ...preferences };
                (newPrefs[item.key] as boolean) = !preferences[item.key];
                updatePreferences({ [item.key]: !preferences[item.key] });
              }}
              className={cn(
                "relative inline-flex h-5 w-9 items-center rounded-full transition-colors",
                preferences[item.key]
                  ? "bg-accent-primary"
                  : "bg-surface-card-border"
              )}
            >
              <span
                className={cn(
                  "inline-block h-3.5 w-3.5 transform rounded-full bg-white transition-transform shadow-sm",
                  preferences[item.key] ? "translate-x-4" : "translate-x-0.5"
                )}
              />
            </button>
          </div>
        ))}

        <div className="space-y-2 pt-2">
          <label className="text-sm font-medium text-text-primary">
            Digest Frequency
          </label>
          <Select
            value={preferences.digest_frequency}
            onValueChange={(v) =>
              updatePreferences({
                digest_frequency: v as typeof preferences.digest_frequency,
              })
            }
          >
            <SelectTrigger className="w-40">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="realtime">Real-time</SelectItem>
              <SelectItem value="hourly">Hourly</SelectItem>
              <SelectItem value="daily">Daily</SelectItem>
              <SelectItem value="weekly">Weekly</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="pt-2">
          <Button size="sm" onClick={handleSave} disabled={isSaving}>
            {isSaving && <Loader2 className="w-3.5 h-3.5 mr-1 animate-spin" />}
            <Save className="w-3.5 h-3.5 mr-1" />
            Save Preferences
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
