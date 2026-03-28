"use client";

export default function PortalEvidencePage() {
  return (
    <div className="animate-fade-in space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-text-primary">
            Evidence
          </h1>
          <p className="mt-1 text-sm text-text-secondary">
            Upload and manage security evidence documents.
          </p>
        </div>
        <button className="rounded-lg bg-accent-primary px-4 py-2 text-sm font-medium text-white transition-all hover:bg-accent-hover active:scale-[0.98]">
          Upload Evidence
        </button>
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
              d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m6.75 12l-3-3m0 0l-3 3m3-3v6m-1.5-15H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z"
            />
          </svg>
          <h3 className="text-base font-medium text-text-primary">
            No evidence uploaded
          </h3>
          <p className="mt-1 text-sm text-text-secondary">
            Upload SOC 2 reports, ISO certificates, or pen test reports.
          </p>
        </div>
      </div>
    </div>
  );
}
