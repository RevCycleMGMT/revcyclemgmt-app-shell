"use client";

import { useMemo } from "react";
import Link from "next/link";

import { Cms1500Form } from "@/components/pipeline/Cms1500Form";
import { GeneratePdfButton } from "@/components/pipeline/GeneratePdfButton";
import { StepIndicator } from "@/components/pipeline/StepIndicator";
import { TeachingNotePanel } from "@/components/pipeline/TeachingNotePanel";
import { X12EdiDisplay } from "@/components/pipeline/X12EdiDisplay";
import { Button } from "@/components/ui/button";
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@/components/ui/tabs";
import { buildClaimFormData } from "@/lib/claims/form-data";
import { getScenarioById } from "@/lib/scenarios";

interface FormsPageProps {
  params: {
    scenarioId: string;
  };
}

export default function FormsPage({ params }: FormsPageProps) {
  const scenario = getScenarioById(params.scenarioId);
  const formData = useMemo(
    () => (scenario ? buildClaimFormData(scenario) : null),
    [scenario]
  );

  if (!scenario || !formData) {
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
    scenario.teachingNotes.find((note) => note.step === "forms")?.text ??
    "The CMS-1500 and X12 837P communicate the same claim information in human-readable and electronic formats.";

  return (
    <main className="min-h-dvh overflow-x-hidden bg-slate-50 px-6 pb-28 pt-10 text-slate-700">
      <div className="mx-auto w-full max-w-6xl space-y-8">
        <StepIndicator currentStep={5} />

        <section>
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-teal-600">
            Forms Generation
          </p>
          <h1 className="mt-3 text-2xl font-semibold tracking-[0] text-slate-900">
            Generate Forms
          </h1>
          <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-600">
            The claim is now rendered as a CMS-1500 and as an X12 837P EDI
            transaction.
          </p>
        </section>

        <Tabs defaultValue="cms" className="w-full">
          <TabsList className="rounded-xl bg-white p-1 shadow-sm ring-1 ring-slate-200">
            <TabsTrigger
              value="cms"
              className="rounded-lg px-5 data-[state=active]:bg-teal-600 data-[state=active]:text-white"
            >
              CMS-1500 Form
            </TabsTrigger>
            <TabsTrigger
              value="edi"
              className="rounded-lg px-5 data-[state=active]:bg-teal-600 data-[state=active]:text-white"
            >
              X12 837P EDI
            </TabsTrigger>
          </TabsList>

          <TabsContent value="cms" className="mt-6">
            <Cms1500Form formData={formData} />
          </TabsContent>

          <TabsContent value="edi" className="mt-6">
            <X12EdiDisplay edi={formData.x12} />
          </TabsContent>
        </Tabs>
      </div>

      <TeachingNotePanel text={teachingNote} />

      <nav className="fixed inset-x-0 bottom-0 z-30 border-t border-slate-200 bg-white/95 backdrop-blur">
        <div className="mx-auto flex max-w-6xl items-center justify-between gap-4 p-4">
          <Button asChild variant="ghost" className="rounded-lg">
            <Link href={`/demo/${scenario.id}/claim`}>&larr; Back to Claim</Link>
          </Button>
          <div className="flex items-center gap-3">
            <GeneratePdfButton formData={formData} />
            <Button asChild className="rounded-lg bg-teal-600 text-white hover:bg-teal-700">
              <Link href={`/demo/${scenario.id}/submit`}>
                Continue to Submit &rarr;
              </Link>
            </Button>
          </div>
        </div>
      </nav>
    </main>
  );
}
