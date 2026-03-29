"use client";

import React, { useState, useRef, useEffect } from "react";
import {
  Sparkles,
  Send,
  Loader2,
  Building2,
  Shield,
  AlertTriangle,
  FileCheck,
  ArrowRight,
  Bot,
  User,
} from "lucide-react";
import { PageHeader } from "@/components/page-header";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
  sources?: { label: string; type: string }[];
}

const SUGGESTED_QUERIES = [
  {
    icon: Building2,
    label: "Which vendors have PHI access but no SOC 2?",
    category: "Compliance Gap",
  },
  {
    icon: AlertTriangle,
    label: "Show me all critical-risk vendors with overdue assessments",
    category: "Risk",
  },
  {
    icon: Shield,
    label: "What's our DORA compliance posture across all vendors?",
    category: "Framework",
  },
  {
    icon: FileCheck,
    label: "Which vendors had rating drops in the last 30 days?",
    category: "Monitoring",
  },
];

const MOCK_RESPONSES: Record<string, { content: string; sources: { label: string; type: string }[] }> = {
  "Which vendors have PHI access but no SOC 2?": {
    content:
      "Based on your vendor inventory, **3 vendors** have PHI access but lack SOC 2 certification:\n\n1. **CloudMed Analytics** — Tier 1 (Critical), handles patient records. Last assessment: 6 months ago. Currently has ISO 27001 but no SOC 2.\n2. **DataVault Health** — Tier 2 (High), processes billing data with PHI. No SOC 2 or ISO 27001.\n3. **RxFlow Systems** — Tier 2 (High), pharmacy management system with PHI access. SOC 2 expired 3 months ago.\n\n**Recommended actions:**\n- Initiate fast-track assessments for all 3 vendors\n- Escalate DataVault Health as highest priority (no certifications)\n- Request SOC 2 renewal from RxFlow Systems",
    sources: [
      { label: "Vendor Inventory", type: "vendor" },
      { label: "Framework Mappings", type: "framework" },
      { label: "Assessment History", type: "assessment" },
    ],
  },
};

export default function AskVeloraPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function handleSubmit(query?: string) {
    const q = query || input.trim();
    if (!q || isLoading) return;

    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: "user",
      content: q,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    // Simulate AI response (in production, this calls /ai/query)
    await new Promise((r) => setTimeout(r, 1500 + Math.random() * 1000));

    const mockResponse = MOCK_RESPONSES[q];
    const assistantMessage: Message = {
      id: crypto.randomUUID(),
      role: "assistant",
      content: mockResponse?.content ||
        `I analyzed your vendor portfolio to answer: "${q}"\n\nThis feature connects to the AI service to run natural language queries against your vendor data, assessments, findings, and monitoring signals. Configure your AI API key in **Settings > AI Configuration** to enable live responses.\n\nIn production, this query would be translated to structured filters and aggregations across your vendor database, returning real-time results with source citations.`,
      timestamp: new Date(),
      sources: mockResponse?.sources || [
        { label: "Vendor Database", type: "vendor" },
        { label: "Risk Scores", type: "scoring" },
      ],
    };

    setMessages((prev) => [...prev, assistantMessage]);
    setIsLoading(false);
  }

  return (
    <>
      <PageHeader
        title="Ask Velora"
        description="Ask questions about your vendor portfolio in plain language"
        actions={
          <Badge variant="outline" className="gap-1">
            <Sparkles className="w-3 h-3" />
            AI-Powered
          </Badge>
        }
      />

      <div className="flex flex-col h-[calc(100vh-200px)]">
        {messages.length === 0 ? (
          <div className="flex-1 flex flex-col items-center justify-center animate-fade-in">
            <div className="flex items-center justify-center w-16 h-16 rounded-2xl bg-accent-primary/10 mb-6">
              <Sparkles className="w-8 h-8 text-accent-primary" />
            </div>
            <h2 className="text-xl font-semibold text-text-primary mb-2">
              What would you like to know?
            </h2>
            <p className="text-sm text-text-muted mb-8 max-w-md text-center">
              Ask about vendors, risk scores, compliance gaps, assessments, findings —
              anything in your TPRM portfolio.
            </p>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 max-w-2xl w-full">
              {SUGGESTED_QUERIES.map((query) => {
                const Icon = query.icon;
                return (
                  <button
                    key={query.label}
                    onClick={() => handleSubmit(query.label)}
                    className="flex items-start gap-3 p-4 rounded-xl border border-surface-card-border bg-surface-card hover:border-accent-primary/30 hover:bg-accent-primary/[0.02] transition-all duration-200 text-left group velora-card-hover"
                  >
                    <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-surface-main shrink-0 group-hover:bg-accent-primary/10 transition-colors">
                      <Icon className="w-4 h-4 text-text-muted group-hover:text-accent-primary transition-colors" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <Badge variant="secondary" className="text-[10px] mb-1.5">
                        {query.category}
                      </Badge>
                      <p className="text-sm text-text-primary leading-snug">
                        {query.label}
                      </p>
                    </div>
                    <ArrowRight className="w-4 h-4 text-text-muted opacity-0 group-hover:opacity-100 transition-opacity mt-1 shrink-0" />
                  </button>
                );
              })}
            </div>
          </div>
        ) : (
          <div className="flex-1 overflow-y-auto space-y-4 pb-4">
            {messages.map((message) => (
              <div
                key={message.id}
                className={cn(
                  "flex gap-3 animate-fade-in",
                  message.role === "user" ? "justify-end" : "justify-start"
                )}
              >
                {message.role === "assistant" && (
                  <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-accent-primary/10 shrink-0 mt-1">
                    <Bot className="w-4 h-4 text-accent-primary" />
                  </div>
                )}
                <div
                  className={cn(
                    "max-w-[600px] rounded-xl px-4 py-3",
                    message.role === "user"
                      ? "bg-accent-primary text-white"
                      : "bg-surface-card border border-surface-card-border"
                  )}
                >
                  <div
                    className={cn(
                      "text-sm leading-relaxed whitespace-pre-wrap",
                      message.role === "user" ? "text-white" : "text-text-primary"
                    )}
                  >
                    {message.content.split(/(\*\*[^*]+\*\*)/).map((part, i) => {
                      if (part.startsWith("**") && part.endsWith("**")) {
                        return <strong key={i}>{part.slice(2, -2)}</strong>;
                      }
                      return part;
                    })}
                  </div>
                  {message.sources && message.sources.length > 0 && (
                    <div className="flex items-center gap-1.5 mt-3 pt-2 border-t border-surface-card-border">
                      <span className="text-[10px] text-text-muted uppercase tracking-wider">Sources:</span>
                      {message.sources.map((source) => (
                        <Badge
                          key={source.label}
                          variant="secondary"
                          className="text-[10px] px-1.5 py-0"
                        >
                          {source.label}
                        </Badge>
                      ))}
                    </div>
                  )}
                </div>
                {message.role === "user" && (
                  <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-surface-main shrink-0 mt-1">
                    <User className="w-4 h-4 text-text-muted" />
                  </div>
                )}
              </div>
            ))}
            {isLoading && (
              <div className="flex gap-3 animate-fade-in">
                <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-accent-primary/10 shrink-0">
                  <Bot className="w-4 h-4 text-accent-primary" />
                </div>
                <div className="bg-surface-card border border-surface-card-border rounded-xl px-4 py-3">
                  <div className="flex items-center gap-2 text-sm text-text-muted">
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Analyzing your portfolio...
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}

        {/* Input area */}
        <div className="border-t border-surface-card-border pt-4">
          <div className="flex items-end gap-2">
            <div className="flex-1 relative">
              <textarea
                ref={inputRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    handleSubmit();
                  }
                }}
                placeholder="Ask about vendors, risk, compliance, assessments..."
                className="w-full resize-none rounded-xl border border-surface-card-border bg-surface-card px-4 py-3 text-sm text-text-primary placeholder:text-text-muted focus:outline-none focus:ring-2 focus:ring-accent-primary/20 focus:border-accent-primary transition-all duration-150 min-h-[48px] max-h-[120px]"
                rows={1}
              />
            </div>
            <Button
              onClick={() => handleSubmit()}
              disabled={!input.trim() || isLoading}
              className="h-12 w-12 rounded-xl shrink-0"
              size="icon"
            >
              {isLoading ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Send className="w-4 h-4" />
              )}
            </Button>
          </div>
          <p className="text-[10px] text-text-muted mt-2 text-center">
            Velora AI analyzes your vendor data to answer questions. Responses are generated — always verify critical findings.
          </p>
        </div>
      </div>
    </>
  );
}
