"use client";

export default function PortalFindingsPage() {
  return (
    <div className="animate-fade-in space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-text-primary">
          Findings & Remediation
        </h1>
        <p className="mt-1 text-sm text-text-secondary">
          View findings from assessments and track remediation progress.
        </p>
      </div>

      <div className="rounded-xl border border-border-default bg-white p-6 shadow-sm">
        <div className="flex flex-col items-center py-12 text-center">
          <svg
            className="mb-4 h-12 w-12 text-text-tertiary"
            fill="none"
            viewBox="0 0 24 24"
            strokeWidth={1.5}
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z"
            />
          </svg>
          <h3 className="text-base font-medium text-text-primary">
            No findings
          </h3>
          <p className="mt-1 text-sm text-text-secondary">
            When findings are raised from your assessments, they will appear here with remediation guidance.
          </p>
        </div>
      </div>
    </div>
  );
}
