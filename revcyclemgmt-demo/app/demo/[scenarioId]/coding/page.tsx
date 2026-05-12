"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import Link from "next/link";
import { AnimatePresence, motion } from "framer-motion";
import { FastForward } from "lucide-react";

import { ClinicalNote } from "@/components/pipeline/ClinicalNote";
import { CodeCard } from "@/components/pipeline/CodeCard";
import { StepIndicator } from "@/components/pipeline/StepIndicator";
import { TeachingNotePanel } from "@/components/pipeline/TeachingNotePanel";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { getScenarioById } from "@/lib/scenarios";
import type { Diagnosis, Procedure, Scenario } from "@/lib/scenarios";

interface CodingPageProps {
  params: {
    scenarioId: string;
  };
}

type CodeItem =
  | {
      id: string;
      type: "ICD-10";
      code: string;
      description: string;
      why: string;
    }
  | {
      id: string;
      type: "CPT";
      code: string;
      modifiers: string[];
      description: string;
      why: string;
    };

const INITIAL_DELAY_MS = 800;
const PULSE_MS = 500;
const CARD_DELAY_AFTER_PULSE_MS = 400;
const NEXT_PHRASE_DWELL_MS = 3300;

function codeIdsForHighlight(scenario: Scenario, linkedCodeId: string) {
  if (scenario.id === "scenario-02-laceration" && linkedCodeId === "proc-90471") {
    return ["proc-90471", "proc-90714"];
  }

  return [linkedCodeId];
}

function toCodeItems(
  diagnoses: Diagnosis[],
  procedures: Procedure[]
): Map<string, CodeItem> {
  const items = new Map<string, CodeItem>();

  diagnoses.forEach((diagnosis) => {
    items.set(diagnosis.id, {
      id: diagnosis.id,
      type: "ICD-10",
      code: diagnosis.code,
      description: diagnosis.description,
      why: diagnosis.why,
    });
  });

  procedures.forEach((procedure) => {
    items.set(procedure.id, {
      id: procedure.id,
      type: "CPT",
      code: procedure.cpt,
      modifiers: procedure.modifiers,
      description: procedure.description,
      why: procedure.why,
    });
  });

  return items;
}

function CodingPanel({
  codeItems,
  revealedCodeIds,
  isComplete,
  diagnosisCount,
  procedureCount,
}: {
  codeItems: Map<string, CodeItem>;
  revealedCodeIds: string[];
  isComplete: boolean;
  diagnosisCount: number;
  procedureCount: number;
}) {
  const visibleCodes = revealedCodeIds
    .map((codeId) => codeItems.get(codeId))
    .filter((item): item is CodeItem => Boolean(item));

  return (
    <Card className="sticky top-6 rounded-xl border-slate-200 bg-white p-6 shadow-sm">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h2 className="text-lg font-semibold tracking-[0] text-slate-900">
            Assigned Codes
          </h2>
          <p className="mt-1 text-sm text-slate-500">
            Codes populate as documentation evidence is revealed.
          </p>
        </div>
      </div>

      <AnimatePresence>
        {visibleCodes.length === 0 && !isComplete ? (
          <motion.div
            key="loading"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="mt-6 flex items-center gap-2 text-sm text-slate-500"
          >
            <span className="size-2 rounded-full bg-teal-600 motion-safe:animate-pulse" />
            Analyzing clinical documentation...
          </motion.div>
        ) : null}
      </AnimatePresence>

      <div className="mt-5 space-y-3">
        <AnimatePresence initial={false}>
          {visibleCodes.map((item) => (
            <motion.div
              key={item.id}
              initial={{ x: 20, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              exit={{ x: 20, opacity: 0 }}
              transition={{ duration: 0.5, ease: "easeOut" }}
            >
              <CodeCard
                type={item.type}
                code={item.code}
                modifiers={item.type === "CPT" ? item.modifiers : undefined}
                description={item.description}
                why={item.why}
              />
            </motion.div>
          ))}
        </AnimatePresence>
      </div>

      <AnimatePresence>
        {isComplete ? (
          <motion.div
            key="summary"
            initial={{ y: 18, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            exit={{ y: 18, opacity: 0 }}
            transition={{ duration: 0.45, ease: "easeOut" }}
            className="mt-5 rounded-lg border border-emerald-200 bg-emerald-50 p-4"
          >
            <p className="text-sm font-semibold text-emerald-800">
              Code set complete: {diagnosisCount} diagnoses, {procedureCount}{" "}
              procedures
            </p>
          </motion.div>
        ) : null}
      </AnimatePresence>
    </Card>
  );
}

export default function CodingPage({ params }: CodingPageProps) {
  const scenario = getScenarioById(params.scenarioId);
  const [activeHighlightIndex, setActiveHighlightIndex] = useState<number | null>(
    null
  );
  const [revealedHighlightIndexes, setRevealedHighlightIndexes] = useState<
    number[]
  >([]);
  const [revealedCodeIds, setRevealedCodeIds] = useState<string[]>([]);
  const [isComplete, setIsComplete] = useState(false);
  const timeoutsRef = useRef<ReturnType<typeof setTimeout>[]>([]);

  const codeItems = useMemo(() => {
    if (!scenario) {
      return new Map<string, CodeItem>();
    }

    return toCodeItems(scenario.diagnoses, scenario.procedures);
  }, [scenario]);

  const clearScheduledAnimation = useCallback(() => {
    timeoutsRef.current.forEach((timeout) => clearTimeout(timeout));
    timeoutsRef.current = [];
  }, []);

  const revealCodes = useCallback((codeIds: string[]) => {
    setRevealedCodeIds((current) => {
      const next = [...current];
      codeIds.forEach((codeId) => {
        if (!next.includes(codeId)) {
          next.push(codeId);
        }
      });
      return next;
    });
  }, []);

  const revealEverything = useCallback(() => {
    if (!scenario) {
      return;
    }

    clearScheduledAnimation();
    setActiveHighlightIndex(null);
    setRevealedHighlightIndexes(
      scenario.encounter.highlightedPhrases.map((_, index) => index)
    );

    const allCodeIds = scenario.encounter.highlightedPhrases.flatMap((highlight) =>
      codeIdsForHighlight(scenario, highlight.linksToCodeId)
    );
    revealCodes(allCodeIds);
    setIsComplete(true);
  }, [clearScheduledAnimation, revealCodes, scenario]);

  useEffect(() => {
    if (!scenario) {
      return;
    }

    clearScheduledAnimation();
    setActiveHighlightIndex(null);
    setRevealedHighlightIndexes([]);
    setRevealedCodeIds([]);
    setIsComplete(false);

    let cursor = INITIAL_DELAY_MS;

    scenario.encounter.highlightedPhrases.forEach((highlight, index) => {
      timeoutsRef.current.push(
        setTimeout(() => {
          setActiveHighlightIndex(index);
        }, cursor)
      );

      cursor += PULSE_MS;

      timeoutsRef.current.push(
        setTimeout(() => {
          setActiveHighlightIndex(null);
          setRevealedHighlightIndexes((current) =>
            current.includes(index) ? current : [...current, index]
          );
        }, cursor)
      );

      cursor += CARD_DELAY_AFTER_PULSE_MS;

      timeoutsRef.current.push(
        setTimeout(() => {
          revealCodes(codeIdsForHighlight(scenario, highlight.linksToCodeId));
        }, cursor)
      );

      cursor += NEXT_PHRASE_DWELL_MS;
    });

    timeoutsRef.current.push(
      setTimeout(() => {
        setActiveHighlightIndex(null);
        setIsComplete(true);
      }, cursor + 400)
    );

    return clearScheduledAnimation;
  }, [clearScheduledAnimation, revealCodes, scenario]);

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
    scenario.teachingNotes.find((note) => note.step === "coding")?.text ??
    "Review the coding logic and connect each assigned code to the documentation evidence.";

  return (
    <main className="min-h-dvh overflow-x-hidden bg-slate-50 px-6 pb-28 pt-10 text-slate-700">
      <div className="mx-auto w-full max-w-7xl space-y-8">
        <StepIndicator currentStep={3} />

        <section className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-teal-600">
              Code It
            </p>
            <h1 className="mt-3 text-3xl font-semibold tracking-[0] text-slate-900">
              AI-assisted coding sequence
            </h1>
            <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-600">
              Watch each documentation phrase light up before its diagnosis,
              procedure, or modifier logic appears in the code set.
            </p>
          </div>

          <Button
            type="button"
            variant="outline"
            className="rounded-lg border-teal-200 bg-white text-teal-700 hover:bg-teal-50"
            onClick={revealEverything}
          >
            <FastForward className="size-4" aria-hidden="true" />
            Skip animation
          </Button>
        </section>

        <div className="grid gap-6 lg:grid-cols-[1.5fr_1fr]">
          <ClinicalNote
            scenario={scenario}
            activeHighlightIndex={activeHighlightIndex}
            revealedHighlightIndexes={revealedHighlightIndexes}
          />

          <CodingPanel
            codeItems={codeItems}
            revealedCodeIds={revealedCodeIds}
            isComplete={isComplete}
            diagnosisCount={scenario.diagnoses.length}
            procedureCount={scenario.procedures.length}
          />
        </div>
      </div>

      <TeachingNotePanel text={teachingNote} />

      <nav className="fixed inset-x-0 bottom-0 z-30 border-t border-slate-200 bg-white/95 backdrop-blur">
        <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 p-4">
          <Button asChild variant="ghost" className="rounded-lg">
            <Link href={`/demo/${scenario.id}/encounter`}>
              &larr; Back to Encounter
            </Link>
          </Button>

          {isComplete ? (
            <Button asChild className="rounded-lg bg-teal-600 text-white hover:bg-teal-700">
              <Link href={`/demo/${scenario.id}/claim`}>
                Continue to Build Claim &rarr;
              </Link>
            </Button>
          ) : (
            <Button
              type="button"
              disabled
              className="rounded-lg bg-teal-600 text-white opacity-50"
            >
              Continue to Build Claim &rarr;
            </Button>
          )}
        </div>
      </nav>
    </main>
  );
}
