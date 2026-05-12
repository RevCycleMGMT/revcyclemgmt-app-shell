"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

import { RemittanceCard } from "@/components/pipeline/RemittanceCard";
import { StepIndicator } from "@/components/pipeline/StepIndicator";
import { SubmissionTimeline } from "@/components/pipeline/SubmissionTimeline";
import { TeachingNotePanel } from "@/components/pipeline/TeachingNotePanel";
import { Button } from "@/components/ui/button";
import { getScenarioById } from "@/lib/scenarios";

interface SubmitPageProps {
  params: {
    scenarioId: string;
  };
}

export default function SubmitPage({ params }: SubmitPageProps) {
  const scenario = getScenarioById(params.scenarioId);
  const [showRemittance, setShowRemittance] = useState(false);

  useEffect(() => {
    const timer = window.setTimeout(() => {
      setShowRemittance(true);
    }, 8000);

    return () => window.clearTimeout(timer);
  }, [params.scenarioId]);

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
    scenario.teachingNotes.find((note) => note.step === "submit")?.text ??
    "The 835 closes the loop: payer payment, contractual adjustments, and patient responsibility are posted back to the account.";

  return (
    <main
      className="min-h-dvh overflow-x-hidden bg-slate-50 px-6 pb-28 pt-10 text-slate-700"
      data-submission-phase={showRemittance ? "outcome" : "submit"}
    >
      <div className="mx-auto w-full max-w-3xl space-y-8">
        <StepIndicator currentStep={showRemittance ? 7 : 6} />

        <section>
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-teal-600">
            Claim Submission
          </p>
          <h1 className="mt-3 text-2xl font-semibold tracking-[0] text-slate-900">
            Submit Claim
          </h1>
          <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-600">
            The simulated clearinghouse sends the 837P, receives
            acknowledgments, and returns the 835 remittance outcome.
          </p>
        </section>

        <SubmissionTimeline />

        {showRemittance ? <RemittanceCard scenario={scenario} /> : null}
      </div>

      <TeachingNotePanel text={teachingNote} />

      <nav className="fixed inset-x-0 bottom-0 z-30 border-t border-slate-200 bg-white/95 backdrop-blur">
        <div className="mx-auto flex max-w-3xl items-center justify-between gap-4 p-4">
          <Button asChild variant="ghost" className="rounded-lg">
            <Link href={`/demo/${scenario.id}/forms`}>&larr; Back to Forms</Link>
          </Button>
          {showRemittance ? (
            <Button asChild className="rounded-lg bg-teal-600 text-white hover:bg-teal-700">
              <Link href={`/demo/${scenario.id}/complete`}>
                Demo Complete &rarr;
              </Link>
            </Button>
          ) : (
            <Button
              type="button"
              disabled
              className="rounded-lg bg-teal-600 text-white"
            >
              Demo Complete &rarr;
            </Button>
          )}
        </div>
      </nav>
    </main>
  );
}
