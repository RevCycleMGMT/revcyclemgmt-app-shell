"use client";

import Link from "next/link";

import { ClaimTable } from "@/components/pipeline/ClaimTable";
import { StepIndicator } from "@/components/pipeline/StepIndicator";
import { TeachingNotePanel } from "@/components/pipeline/TeachingNotePanel";
import { Button } from "@/components/ui/button";
import { getScenarioById } from "@/lib/scenarios";

interface ClaimPageProps {
  params: {
    scenarioId: string;
  };
}

export default function ClaimPage({ params }: ClaimPageProps) {
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

  const teachingNote =
    scenario.teachingNotes.find((note) => note.step === "claim")?.text ??
    "Claim lines connect procedure codes, modifiers, units, charges, and diagnosis pointers.";

  return (
    <main className="min-h-dvh overflow-x-hidden bg-slate-50 px-6 pb-28 pt-10 text-slate-700">
      <div className="mx-auto w-full max-w-5xl space-y-8">
        <StepIndicator currentStep={4} />

        <section>
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-teal-600">
            Claim Builder
          </p>
          <h1 className="mt-3 text-2xl font-semibold tracking-[0] text-slate-900">
            Build Claim
          </h1>
          <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-600">
            Codes from the previous step are now flowing into claim lines.
          </p>
        </section>

        <ClaimTable scenario={scenario} />
      </div>

      <TeachingNotePanel text={teachingNote} />

      <nav className="fixed inset-x-0 bottom-0 z-30 border-t border-slate-200 bg-white/95 backdrop-blur">
        <div className="mx-auto flex max-w-5xl items-center justify-between gap-4 p-4">
          <Button asChild variant="ghost" className="rounded-lg">
            <Link href={`/demo/${scenario.id}/coding`}>&larr; Back to Coding</Link>
          </Button>
          <Button asChild className="rounded-lg bg-teal-600 text-white hover:bg-teal-700">
            <Link href={`/demo/${scenario.id}/forms`}>
              Continue to Forms &rarr;
            </Link>
          </Button>
        </div>
      </nav>
    </main>
  );
}
