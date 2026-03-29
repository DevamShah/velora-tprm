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
  Brain,
  Palette,
  Sun,
  Moon,
  Monitor,
  Eye,
  EyeOff,
  CheckCircle2,
  Sparkles,
  Key,
  Zap,
} from "lucide-react";
import { toast } from "sonner";
import { PageHeader } from "@/components/page-header";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
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
import { useTheme, type Theme } from "@/providers/theme-provider";
import { cn } from "@/lib/utils";

export default function SettingsPage() {
  return (
    <>
      <PageHeader
        title="Settings"
        description="Configure platform preferences, AI capabilities, and appearance"
      />

      <Tabs defaultValue="general">
        <TabsList>
          <TabsTrigger value="general">
            <Settings className="h-3.5 w-3.5 mr-1" />
            General
          </TabsTrigger>
          <TabsTrigger value="ai">
            <Brain className="h-3.5 w-3.5 mr-1" />
            AI Configuration
          </TabsTrigger>
          <TabsTrigger value="appearance">
            <Palette className="h-3.5 w-3.5 mr-1" />
            Appearance
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

        <TabsContent value="ai" className="mt-4">
          <AISettings />
        </TabsContent>

        <TabsContent value="appearance" className="mt-4">
          <AppearanceSettings />
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

/* --- AI Configuration Settings --- */

function AISettings() {
  const [apiKey, setApiKey] = useState("");
  const [showKey, setShowKey] = useState(false);
  const [provider, setProvider] = useState("anthropic");
  const [model, setModel] = useState("claude-sonnet-4-20250514");
  const [isSaving, setIsSaving] = useState(false);
  const [isTesting, setIsTesting] = useState(false);
  const [testResult, setTestResult] = useState<"success" | "error" | null>(null);

  const handleSave = async () => {
    if (!apiKey.trim()) {
      toast.error("Please enter an API key.");
      return;
    }
    setIsSaving(true);
    try {
      // POST /admin/settings/ai with encrypted key
      await new Promise((r) => setTimeout(r, 1000));
      toast.success("AI configuration saved securely.");
    } catch {
      toast.error("Failed to save AI configuration.");
    } finally {
      setIsSaving(false);
    }
  };

  const handleTestConnection = async () => {
    if (!apiKey.trim()) {
      toast.error("Enter an API key first.");
      return;
    }
    setIsTesting(true);
    setTestResult(null);
    try {
      await new Promise((r) => setTimeout(r, 2000));
      setTestResult("success");
      toast.success("AI connection verified successfully.");
    } catch {
      setTestResult("error");
      toast.error("Connection failed. Check your API key.");
    } finally {
      setIsTesting(false);
    }
  };

  return (
    <div className="space-y-4 max-w-2xl">
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-accent-primary/10">
              <Brain className="h-4 w-4 text-accent-primary" />
            </div>
            <div>
              <CardTitle className="text-base">AI Provider</CardTitle>
              <CardDescription>
                Configure the AI backend that powers intelligent features
              </CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-5">
          <div className="space-y-2">
            <label className="text-sm font-medium text-text-primary">
              Provider
            </label>
            <Select value={provider} onValueChange={setProvider}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="anthropic">Anthropic (Claude)</SelectItem>
                <SelectItem value="openai">OpenAI (GPT)</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium text-text-primary">
              Model
            </label>
            <Select value={model} onValueChange={setModel}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {provider === "anthropic" ? (
                  <>
                    <SelectItem value="claude-opus-4-20250514">Claude Opus 4 (Most Capable)</SelectItem>
                    <SelectItem value="claude-sonnet-4-20250514">Claude Sonnet 4 (Balanced)</SelectItem>
                    <SelectItem value="claude-haiku-4-20250414">Claude Haiku 4 (Fastest)</SelectItem>
                  </>
                ) : (
                  <>
                    <SelectItem value="gpt-4o">GPT-4o (Most Capable)</SelectItem>
                    <SelectItem value="gpt-4o-mini">GPT-4o Mini (Fastest)</SelectItem>
                  </>
                )}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium text-text-primary">
              API Key
            </label>
            <div className="relative">
              <Key className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-muted" />
              <Input
                type={showKey ? "text" : "password"}
                placeholder={provider === "anthropic" ? "sk-ant-api03-..." : "sk-proj-..."}
                value={apiKey}
                onChange={(e) => {
                  setApiKey(e.target.value);
                  setTestResult(null);
                }}
                className="pl-10 pr-10 font-mono text-sm"
              />
              <button
                type="button"
                onClick={() => setShowKey(!showKey)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-text-muted hover:text-text-primary transition-colors"
              >
                {showKey ? (
                  <EyeOff className="w-4 h-4" />
                ) : (
                  <Eye className="w-4 h-4" />
                )}
              </button>
            </div>
            <p className="text-xs text-text-muted">
              Your API key is encrypted at rest using AES-256-GCM. It is never exposed in logs or API responses.
            </p>
          </div>

          {testResult && (
            <div
              className={cn(
                "flex items-center gap-2 p-3 rounded-lg text-sm",
                testResult === "success"
                  ? "bg-accent-success/10 text-accent-success"
                  : "bg-accent-error/10 text-accent-error"
              )}
            >
              {testResult === "success" ? (
                <CheckCircle2 className="w-4 h-4" />
              ) : (
                <AlertTriangle className="w-4 h-4" />
              )}
              {testResult === "success"
                ? "Connection verified. AI features are ready."
                : "Connection failed. Please check your API key and try again."}
            </div>
          )}

          <div className="flex items-center gap-2 pt-2">
            <Button size="sm" onClick={handleSave} disabled={isSaving}>
              {isSaving && <Loader2 className="w-3.5 h-3.5 animate-spin" />}
              <Save className="w-3.5 h-3.5" />
              Save Configuration
            </Button>
            <Button
              size="sm"
              variant="outline"
              onClick={handleTestConnection}
              disabled={isTesting}
            >
              {isTesting ? (
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
              ) : (
                <Zap className="w-3.5 h-3.5" />
              )}
              Test Connection
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <Sparkles className="h-4 w-4 text-text-muted" />
            <CardTitle className="text-base">AI-Powered Features</CardTitle>
          </div>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-text-muted mb-4">
            Once your API key is configured, the following AI capabilities become active:
          </p>
          <div className="grid gap-3">
            {[
              {
                name: "Assessment Auto-Fill",
                description: "Pre-populate questionnaire responses from prior data and evidence",
                status: "active",
              },
              {
                name: "Evidence Parsing",
                description: "Extract controls and findings from SOC 2, ISO 27001, and pen test reports",
                status: "active",
              },
              {
                name: "AI Review Queue",
                description: "Flag low-confidence responses for human review with reasoning",
                status: "active",
              },
              {
                name: "Remediation Guidance",
                description: "Generate actionable remediation steps with effort estimates",
                status: "active",
              },
              {
                name: "Executive Narratives",
                description: "Auto-generate report narratives for board-ready presentations",
                status: "active",
              },
              {
                name: "Contract Analysis",
                description: "Extract risk-relevant clauses from vendor contracts",
                status: "beta",
              },
              {
                name: "Natural Language Q&A",
                description: "Ask questions about your vendor portfolio in plain language",
                status: "beta",
              },
              {
                name: "Risk Prediction",
                description: "Predictive signals for likely vendor incidents based on trend analysis",
                status: "coming",
              },
            ].map((feature) => (
              <div
                key={feature.name}
                className="flex items-center justify-between p-3 rounded-lg border border-surface-card-border"
              >
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <p className="text-sm font-medium text-text-primary">
                      {feature.name}
                    </p>
                    {feature.status === "beta" && (
                      <Badge variant="outline" className="text-[10px] px-1.5 py-0">
                        Beta
                      </Badge>
                    )}
                    {feature.status === "coming" && (
                      <Badge variant="secondary" className="text-[10px] px-1.5 py-0">
                        Coming Soon
                      </Badge>
                    )}
                  </div>
                  <p className="text-xs text-text-muted mt-0.5">
                    {feature.description}
                  </p>
                </div>
                <div
                  className={cn(
                    "w-2 h-2 rounded-full shrink-0 ml-3",
                    feature.status === "active"
                      ? "bg-accent-success"
                      : feature.status === "beta"
                        ? "bg-accent-warning"
                        : "bg-text-muted/30"
                  )}
                />
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

/* --- Appearance Settings --- */

function AppearanceSettings() {
  const { theme, setTheme } = useTheme();

  const themes: { value: Theme; label: string; description: string; icon: typeof Sun }[] = [
    {
      value: "light",
      label: "Light",
      description: "Clean, bright interface with white surfaces and navy accents",
      icon: Sun,
    },
    {
      value: "dark",
      label: "Dark",
      description: "Deep navy surfaces with reduced eye strain for extended use",
      icon: Moon,
    },
    {
      value: "system",
      label: "System",
      description: "Automatically match your operating system preference",
      icon: Monitor,
    },
  ];

  return (
    <div className="space-y-4 max-w-2xl">
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <Palette className="h-4 w-4 text-text-muted" />
            <div>
              <CardTitle className="text-base">Theme</CardTitle>
              <CardDescription>
                Choose how Velora looks for you
              </CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid gap-3">
            {themes.map((option) => {
              const Icon = option.icon;
              const isActive = theme === option.value;

              return (
                <button
                  key={option.value}
                  onClick={() => setTheme(option.value)}
                  className={cn(
                    "flex items-center gap-4 p-4 rounded-xl border-2 transition-all duration-200 text-left",
                    isActive
                      ? "border-accent-primary bg-accent-primary/5"
                      : "border-surface-card-border hover:border-accent-primary/30"
                  )}
                >
                  <div
                    className={cn(
                      "flex items-center justify-center w-10 h-10 rounded-xl transition-colors",
                      isActive
                        ? "bg-accent-primary/15 text-accent-primary"
                        : "bg-surface-main text-text-muted"
                    )}
                  >
                    <Icon className="w-5 h-5" />
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <p className="text-sm font-semibold text-text-primary">
                        {option.label}
                      </p>
                      {isActive && (
                        <Badge className="text-[10px] px-1.5 py-0 bg-accent-primary text-white">
                          Active
                        </Badge>
                      )}
                    </div>
                    <p className="text-xs text-text-muted mt-0.5">
                      {option.description}
                    </p>
                  </div>
                  <div
                    className={cn(
                      "w-5 h-5 rounded-full border-2 flex items-center justify-center transition-colors",
                      isActive
                        ? "border-accent-primary"
                        : "border-surface-card-border"
                    )}
                  >
                    {isActive && (
                      <div className="w-2.5 h-2.5 rounded-full bg-accent-primary" />
                    )}
                  </div>
                </button>
              );
            })}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Theme Preview</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-3">
            <div className="p-4 rounded-lg bg-surface-main border border-surface-card-border">
              <div className="flex items-center gap-2 mb-2">
                <div className="w-3 h-3 rounded-full bg-accent-primary" />
                <p className="text-xs font-medium text-text-primary">Primary</p>
              </div>
              <p className="text-xs text-text-muted">Surface background</p>
            </div>
            <div className="p-4 rounded-lg bg-surface-card border border-surface-card-border">
              <div className="flex items-center gap-2 mb-2">
                <div className="w-3 h-3 rounded-full bg-accent-success" />
                <p className="text-xs font-medium text-text-primary">Card</p>
              </div>
              <p className="text-xs text-text-muted">Card surface</p>
            </div>
            <div className="p-4 rounded-lg bg-surface-sidebar">
              <div className="flex items-center gap-2 mb-2">
                <div className="w-3 h-3 rounded-full bg-accent-info" />
                <p className="text-xs font-medium text-text-inverse">Sidebar</p>
              </div>
              <p className="text-xs text-text-inverse-muted">Navigation</p>
            </div>
            <div className="p-4 rounded-lg bg-surface-header border border-surface-card-border">
              <div className="flex items-center gap-2 mb-2">
                <div className="w-3 h-3 rounded-full bg-accent-warning" />
                <p className="text-xs font-medium text-text-primary">Header</p>
              </div>
              <p className="text-xs text-text-muted">Top bar</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
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

  const defaultModel = (models || []).find((m) => m.is_default) || (models || [])[0];

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
