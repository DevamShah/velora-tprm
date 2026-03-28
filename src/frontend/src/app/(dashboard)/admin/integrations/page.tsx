"use client";

import React, { useState } from "react";
import { Plug, Settings, ExternalLink, CheckCircle2 } from "lucide-react";
import { toast } from "sonner";
import { PageHeader } from "@/components/page-header";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";

interface Integration {
  id: string;
  name: string;
  description: string;
  icon: string;
  category: "ticketing" | "communication" | "security" | "identity";
  enabled: boolean;
  configRequired: string[];
}

const INTEGRATIONS: Integration[] = [
  {
    id: "jira",
    name: "Jira",
    description: "Sync findings and remediation tasks with Jira issues",
    icon: "J",
    category: "ticketing",
    enabled: false,
    configRequired: ["base_url", "api_token", "project_key"],
  },
  {
    id: "servicenow",
    name: "ServiceNow",
    description: "Create and track incidents in ServiceNow",
    icon: "SN",
    category: "ticketing",
    enabled: false,
    configRequired: ["instance_url", "username", "password"],
  },
  {
    id: "slack",
    name: "Slack",
    description: "Send notifications and alerts to Slack channels",
    icon: "S",
    category: "communication",
    enabled: false,
    configRequired: ["webhook_url", "channel"],
  },
  {
    id: "teams",
    name: "Microsoft Teams",
    description: "Deliver alerts and reports to Teams channels",
    icon: "T",
    category: "communication",
    enabled: false,
    configRequired: ["webhook_url"],
  },
  {
    id: "crowdstrike",
    name: "CrowdStrike",
    description: "Import threat intelligence and breach data",
    icon: "CS",
    category: "security",
    enabled: false,
    configRequired: ["client_id", "client_secret"],
  },
  {
    id: "bitsight",
    name: "BitSight",
    description: "Import external security ratings for vendors",
    icon: "BS",
    category: "security",
    enabled: false,
    configRequired: ["api_key"],
  },
  {
    id: "okta",
    name: "Okta SSO",
    description: "Single sign-on via Okta SAML/OIDC",
    icon: "O",
    category: "identity",
    enabled: false,
    configRequired: ["domain", "client_id", "client_secret"],
  },
  {
    id: "azure_ad",
    name: "Azure AD",
    description: "Single sign-on and directory sync via Azure AD",
    icon: "AD",
    category: "identity",
    enabled: false,
    configRequired: ["tenant_id", "client_id", "client_secret"],
  },
];

const CATEGORY_LABELS: Record<string, string> = {
  ticketing: "Ticketing",
  communication: "Communication",
  security: "Security Intelligence",
  identity: "Identity & SSO",
};

const CATEGORY_ORDER = ["ticketing", "communication", "security", "identity"];

export default function IntegrationsPage() {
  const [configTarget, setConfigTarget] = useState<Integration | null>(null);
  const [configValues, setConfigValues] = useState<Record<string, string>>({});

  const handleConfigure = () => {
    if (!configTarget) return;
    const hasEmpty = configTarget.configRequired.some(
      (key) => !configValues[key]?.trim()
    );
    if (hasEmpty) {
      toast.error("All fields are required");
      return;
    }
    toast.success(`${configTarget.name} configuration saved`);
    setConfigTarget(null);
    setConfigValues({});
  };

  const openConfig = (integration: Integration) => {
    setConfigTarget(integration);
    setConfigValues({});
  };

  const grouped = CATEGORY_ORDER.map((cat) => ({
    category: cat,
    label: CATEGORY_LABELS[cat],
    integrations: INTEGRATIONS.filter((i) => i.category === cat),
  }));

  return (
    <>
      <PageHeader
        title="Integrations"
        description="Connect external services and data sources"
      />

      <div className="space-y-8">
        {grouped.map((group) => (
          <div key={group.category}>
            <h3 className="text-sm font-semibold text-text-muted uppercase tracking-wider mb-3">
              {group.label}
            </h3>
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {group.integrations.map((integration) => (
                <Card
                  key={integration.id}
                  className="hover:shadow-md transition-shadow"
                >
                  <CardContent className="pt-5">
                    <div className="flex items-start gap-3">
                      <div className="flex items-center justify-center w-10 h-10 rounded-lg bg-surface-main text-text-primary font-bold text-sm shrink-0">
                        {integration.icon}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <p className="text-sm font-semibold text-text-primary">
                            {integration.name}
                          </p>
                          {integration.enabled && (
                            <CheckCircle2 className="w-3.5 h-3.5 text-risk-low" />
                          )}
                        </div>
                        <p className="text-xs text-text-muted mt-0.5 line-clamp-2">
                          {integration.description}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center justify-between mt-4 pt-3 border-t border-surface-card-border">
                      <Badge
                        variant={integration.enabled ? "low" : "secondary"}
                        className="text-[10px]"
                      >
                        {integration.enabled ? "Connected" : "Not Connected"}
                      </Badge>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => openConfig(integration)}
                      >
                        <Settings className="w-3.5 h-3.5 mr-1" />
                        Configure
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        ))}
      </div>

      {/* Configure Dialog */}
      <Dialog
        open={!!configTarget}
        onOpenChange={(v) => {
          if (!v) {
            setConfigTarget(null);
            setConfigValues({});
          }
        }}
      >
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>
              Configure {configTarget?.name}
            </DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-2">
            {configTarget?.configRequired.map((field) => (
              <div key={field} className="space-y-2">
                <label className="text-sm font-medium text-text-primary capitalize">
                  {field.replace(/_/g, " ")}
                </label>
                <Input
                  type={
                    field.includes("secret") ||
                    field.includes("password") ||
                    field.includes("token")
                      ? "password"
                      : "text"
                  }
                  placeholder={`Enter ${field.replace(/_/g, " ")}`}
                  value={configValues[field] || ""}
                  onChange={(e) =>
                    setConfigValues((prev) => ({
                      ...prev,
                      [field]: e.target.value,
                    }))
                  }
                />
              </div>
            ))}
          </div>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => {
                setConfigTarget(null);
                setConfigValues({});
              }}
            >
              Cancel
            </Button>
            <Button onClick={handleConfigure}>Save Configuration</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}
