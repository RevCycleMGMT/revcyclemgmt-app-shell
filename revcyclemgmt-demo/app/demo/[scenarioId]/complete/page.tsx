"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { CheckCircle } from "lucide-react";
import { motion } from "framer-motion";

import { StepIndicator } from "@/components/pipeline/StepIndicator";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { formatCurrency } from "@/lib/claims/form-data";
import { getScenarioById } from "@/lib/scenarios";
import { cn } from "@/lib/utils";

interface CompletePageProps {
  params: {
    scenarioId: string;
  };
}

function useCountUp(target: number, durationMs = 900) {
  const [value, setValue] = useState(0);

  useEffect(() => {
    let animationFrame: number;
    let startedAt: number | null = null;

    const tick = (timestamp: number) => {
      if (startedAt === null) {
        startedAt = timestamp;
      }

      const elapsed = timestamp - startedAt;
      const progress = Math.min(elapsed / durationMs, 1);
      const easedProgress = 1 - Math.pow(1 - progress, 3);

      setValue(target * easedProgress);

      if (progress < 1) {
        animationFrame = window.requestAnimationFrame(tick);
      } else {
        setValue(target);
      }
    };

    animationFrame = window.requestAnimationFrame(tick);

    return () => window.cancelAnimationFrame(animationFrame);
  }, [durationMs, target]);

  return value;
}

function SummaryStat({
  label,
  value,
  className,
}: {
  label: string;
  value: number;
  className?: string;
}) {
  const animatedValue = useCountUp(value);

  return (
    <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
      <p className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
        {label}
      </p>
      <p
        className={cn(
          "mt-3 font-mono text-2xl font-semibold",
          className ?? "text-slate-900"
        )}
      >
        {formatCurrency(animatedValue)}
      </p>
    </div>
  );
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
      <div className="mx-auto w-full max-w-4xl space-y-8">
        <StepIndicator currentStep={7} complete />

        <motion.div
          initial={{ scale: 0.95, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 0.5, ease: "easeOut" }}
          className="mx-auto max-w-2xl"
        >
          <Card className="rounded-xl border-slate-200 bg-white p-12 text-center shadow-md">
            <motion.div
              initial={{ scale: 0, rotate: -10 }}
              animate={{ scale: 1, rotate: 0 }}
              transition={{
                type: "spring",
                stiffness: 280,
                damping: 14,
                delay: 0.12,
              }}
              className="mx-auto text-emerald-600"
            >
              <CheckCircle className="size-16" aria-hidden="true" />
            </motion.div>

            <h1 className="mt-3 text-3xl font-semibold tracking-[0] text-slate-900">
              Demo Complete
            </h1>
            <p className="mx-auto mt-4 max-w-xl text-sm leading-6 text-slate-600">
              You walked through the full revenue cycle for{" "}
              {scenario.patient.name}.
            </p>

            <div className="mt-8 grid grid-cols-3 gap-4 max-sm:grid-cols-1">
              <SummaryStat label="Total Charges" value={scenario.totalCharges} />
              <SummaryStat
                label="Paid by Payer"
                value={scenario.expectedRemittance.totalPaid}
                className="text-emerald-600"
              />
              <SummaryStat
                label="Patient Responsibility"
                value={scenario.expectedRemittance.totalPatientResponsibility}
                className="text-amber-600"
              />
            </div>

            <div className="mt-8 flex flex-wrap justify-center gap-3">
              <Button
                asChild
                className="rounded-lg bg-teal-600 text-white hover:bg-teal-700"
              >
                <Link href="/demo">Try Another Scenario</Link>
              </Button>
              <Button
                asChild
                variant="outline"
                className="rounded-lg border-slate-200"
              >
                <Link href="/">Back to RevCycleMGMT</Link>
              </Button>
              <Button
                asChild
                variant="ghost"
                className="rounded-lg text-slate-600"
              >
                <a href="mailto:hello@revcyclemgmt.com?subject=Institutional%20pilot%20inquiry">
                  Request institutional pilot
                </a>
              </Button>
            </div>
          </Card>
        </motion.div>
      </div>
    </main>
  );
}
