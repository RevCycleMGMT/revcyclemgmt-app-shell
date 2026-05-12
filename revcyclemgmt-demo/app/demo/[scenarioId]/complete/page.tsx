"use client";

import Link from "next/link";

import { StepIndicator } from "@/components/pipeline/StepIndicator";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { getScenarioById } from "@/lib/scenarios";

interface CompletePageProps {
  params: {
    scenarioId: string;
  };
}

export default function CompletePage({ params }: CompletePageProps) {
  const scenario = getScenarioById(params.scenarioId);

  if (!scenario) {
    return (
      <main className="flex min-h-dvh items-center justify-center bg-slate-50 px-6 text-center">
        <div className="max-w-md rounded-xl border border-slate-200 bg-white p-8 shadow-sm">
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-teal-600">
            Scenario
          </p>
          <h1 className="mt-3 text-2xl font-semibold tracking-[0] text-slate-900">
            Scenario not found
          </h1>
          <p className="mt-3 text-sm leading-6 text-slate-600">
            The requested scenario is not available in the demo data set.
          </p>
          <Button asChild className="mt-6 rounded-lg bg-teal-600 text-white hover:bg-teal-700">
            <Link href="/demo">Back to Scenarios</Link>
          </Button>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-dvh overflow-x-hidden bg-slate-50 px-6 py-10 text-slate-700">
      <div className="mx-auto w-full max-w-3xl space-y-8">
        <StepIndicator currentStep={7} />

        <Card className="rounded-xl border-slate-200 bg-white p-8 text-center shadow-md">
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-teal-600">
            Demo Complete
          </p>
          <h1 className="mt-3 text-3xl font-semibold tracking-[0] text-slate-900">
            Revenue cycle walkthrough complete.
          </h1>
          <p className="mx-auto mt-4 max-w-xl text-sm leading-6 text-slate-600">
            {scenario.patient.name} has moved from clinical documentation to
            coded claim, CMS-1500, X12 837P submission, and 835 remittance.
          </p>
          <div className="mt-8 flex justify-center gap-3">
            <Button asChild variant="outline" className="rounded-lg border-slate-200">
              <Link href={`/demo/${scenario.id}/submit`}>Review Outcome</Link>
            </Button>
            <Button asChild className="rounded-lg bg-teal-600 text-white hover:bg-teal-700">
              <Link href="/demo">Choose Another Scenario</Link>
            </Button>
          </div>
        </Card>
      </div>
    </main>
  );
}
