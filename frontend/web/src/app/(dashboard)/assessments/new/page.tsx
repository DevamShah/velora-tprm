"use client";

import React from "react";
import { useRouter } from "next/navigation";
import { ArrowLeft } from "lucide-react";
import { PageHeader } from "@/components/page-header";
import { Button } from "@/components/ui/button";
import { AssessmentWizard } from "@/components/assessments/assessment-wizard";

export default function NewAssessmentPage() {
  const router = useRouter();

  return (
    <>
      <div className="flex items-center gap-2 mb-4">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => router.push("/assessments")}
        >
          <ArrowLeft className="h-4 w-4 mr-1" />
          Assessments
        </Button>
      </div>

      <PageHeader
        title="Create Assessment"
        description="Set up a new vendor risk assessment"
      />

      <AssessmentWizard />
    </>
  );
}
