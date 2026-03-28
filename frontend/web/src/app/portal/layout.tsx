"use client";

import { ReactNode } from "react";

export default function PortalLayout({
  children,
}: {
  children: ReactNode;
}) {
  return (
    <div className="min-h-screen bg-surface-main">
      {/* Portal Header */}
      <header className="border-b border-border-default bg-white px-6 py-4">
        <div className="mx-auto flex max-w-5xl items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-accent-primary/10">
              <svg
                className="h-5 w-5 text-accent-primary"
                fill="none"
                viewBox="0 0 24 24"
                strokeWidth={2}
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z"
                />
              </svg>
            </div>
            <span className="text-lg font-semibold text-text-primary">
              Velora Vendor Portal
            </span>
          </div>
          <nav className="flex items-center gap-6 text-sm text-text-secondary">
            <a href="/portal" className="hover:text-text-primary transition-colors">
              Dashboard
            </a>
            <a href="/portal/assessments" className="hover:text-text-primary transition-colors">
              Assessments
            </a>
            <a href="/portal/evidence" className="hover:text-text-primary transition-colors">
              Evidence
            </a>
            <a href="/portal/findings" className="hover:text-text-primary transition-colors">
              Findings
            </a>
          </nav>
        </div>
      </header>

      {/* Portal Content */}
      <main className="mx-auto max-w-5xl px-6 py-8">
        {children}
      </main>
    </div>
  );
}
