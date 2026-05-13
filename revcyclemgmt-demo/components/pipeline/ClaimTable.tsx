"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { motion, useReducedMotion } from "framer-motion";

import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { cn } from "@/lib/utils";
import type { Scenario } from "@/lib/scenarios";

interface ClaimTableProps {
  scenario: Scenario;
}

const modifierExplanations: Record<string, string> = {
  "25":
    "Significant, separately identifiable evaluation and management service by the same physician on the same day of the procedure or other service.",
};

function formatCurrency(value: number) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: Number.isInteger(value) ? 0 : 2,
  }).format(value);
}

function formatDate(isoDate: string) {
  const [year, month, day] = isoDate.split("-");
  return `${month}/${day}/${year}`;
}

export function ClaimTable({ scenario }: ClaimTableProps) {
  const prefersReducedMotion = Boolean(useReducedMotion());
  const fullTotal = useMemo(
    () =>
      scenario.procedures.reduce(
        (sum, procedure) => sum + procedure.charge * procedure.units,
        0
      ),
    [scenario.procedures]
  );
  const [visibleRowCount, setVisibleRowCount] = useState(() =>
    prefersReducedMotion ? scenario.procedures.length : 0
  );
  const [displayedTotal, setDisplayedTotal] = useState(() =>
    prefersReducedMotion ? fullTotal : 0
  );
  const displayedTotalRef = useRef(prefersReducedMotion ? fullTotal : 0);

  const diagnosisLetters = useMemo(() => {
    return new Map(
      scenario.diagnoses.map((diagnosis, index) => [
        diagnosis.id,
        String.fromCharCode(65 + index),
      ])
    );
  }, [scenario.diagnoses]);

  useEffect(() => {
    setVisibleRowCount(0);
    displayedTotalRef.current = 0;
    setDisplayedTotal(0);

    if (prefersReducedMotion) {
      setVisibleRowCount(scenario.procedures.length);
      displayedTotalRef.current = fullTotal;
      setDisplayedTotal(fullTotal);
      return undefined;
    }

    const timers = scenario.procedures.map((_, index) =>
      setTimeout(() => {
        setVisibleRowCount(index + 1);
      }, index * 250)
    );

    return () => {
      timers.forEach((timer) => clearTimeout(timer));
    };
  }, [fullTotal, prefersReducedMotion, scenario.procedures]);

  const targetTotal = scenario.procedures
    .slice(0, visibleRowCount)
    .reduce((sum, procedure) => sum + procedure.charge * procedure.units, 0);

  useEffect(() => {
    if (prefersReducedMotion) {
      return undefined;
    }

    const startTotal = displayedTotalRef.current;
    const delta = targetTotal - startTotal;
    const duration = 300;
    let animationFrame: number;
    let startedAt: number | null = null;

    if (delta === 0) {
      return undefined;
    }

    const tick = (timestamp: number) => {
      if (startedAt === null) {
        startedAt = timestamp;
      }

      const elapsed = timestamp - startedAt;
      const progress = Math.min(elapsed / duration, 1);
      const easedProgress = 1 - Math.pow(1 - progress, 3);
      const nextTotal = startTotal + delta * easedProgress;

      displayedTotalRef.current = nextTotal;
      setDisplayedTotal(nextTotal);

      if (progress < 1) {
        animationFrame = requestAnimationFrame(tick);
      } else {
        displayedTotalRef.current = targetTotal;
        setDisplayedTotal(targetTotal);
      }
    };

    animationFrame = requestAnimationFrame(tick);

    return () => {
      cancelAnimationFrame(animationFrame);
    };
  }, [prefersReducedMotion, targetTotal]);

  return (
    <TooltipProvider delayDuration={150}>
      <Card className="overflow-hidden rounded-xl border-slate-200 bg-white p-0 shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full min-w-[820px] border-collapse text-left">
            <thead>
              <tr className="bg-slate-50 text-xs uppercase tracking-wider text-slate-600">
                <th className="p-4 font-semibold">Date of Service</th>
                <th className="p-4 font-semibold">CPT Code</th>
                <th className="p-4 font-semibold">Modifiers</th>
                <th className="p-4 font-semibold">Diagnosis Pointers</th>
                <th className="p-4 font-semibold">Units</th>
                <th className="p-4 text-right font-semibold">Charge</th>
              </tr>
            </thead>
            <tbody>
              {scenario.procedures.map((procedure, index) => {
                const isVisible = index < visibleRowCount;

                return (
                  <motion.tr
                    key={procedure.id}
                    initial={prefersReducedMotion ? false : { x: -10, opacity: 0 }}
                    animate={
                      prefersReducedMotion || isVisible
                        ? { x: 0, opacity: 1 }
                        : { x: -10, opacity: 0 }
                    }
                    transition={{
                      duration: prefersReducedMotion ? 0 : 0.3,
                      ease: "easeOut",
                    }}
                    className={cn(
                      "border-b border-slate-100",
                      index % 2 === 0 ? "bg-white" : "bg-slate-50/50"
                    )}
                  >
                    <td className="p-4 text-sm text-slate-700">
                      {formatDate(scenario.encounter.dateOfService)}
                    </td>
                    <td className="p-4 font-mono text-sm font-semibold text-slate-900">
                      {procedure.cpt}
                    </td>
                    <td className="p-4">
                      <div className="flex flex-wrap gap-1.5">
                        {procedure.modifiers.length > 0 ? (
                          procedure.modifiers.map((modifier) => (
                            <Tooltip key={modifier}>
                              <TooltipTrigger asChild>
                                <span className="inline-flex cursor-help">
                                  <Badge
                                    variant="outline"
                                    className="rounded-lg border-teal-200 bg-teal-50 text-teal-700"
                                  >
                                    {modifier}
                                  </Badge>
                                </span>
                              </TooltipTrigger>
                              <TooltipContent className="max-w-xs text-sm leading-5">
                                {modifierExplanations[modifier] ??
                                  "Modifier explanation not configured."}
                              </TooltipContent>
                            </Tooltip>
                          ))
                        ) : (
                          <span className="text-sm text-slate-400">None</span>
                        )}
                      </div>
                    </td>
                    <td className="p-4">
                      <div className="flex flex-wrap gap-1.5">
                        {procedure.diagnosisPointers.map((diagnosisId) => (
                          <Badge
                            key={diagnosisId}
                            variant="outline"
                            className="rounded-lg border-slate-200 bg-slate-50 text-slate-700"
                          >
                            {diagnosisLetters.get(diagnosisId) ?? "?"}
                          </Badge>
                        ))}
                      </div>
                    </td>
                    <td className="p-4 text-sm text-slate-700">
                      {procedure.units}
                    </td>
                    <td className="p-4 text-right font-mono text-sm font-semibold text-slate-900">
                      {formatCurrency(procedure.charge)}
                    </td>
                  </motion.tr>
                );
              })}
            </tbody>
          </table>
        </div>

        <div className="border-t border-slate-200 px-6 py-5">
          <div className="flex items-center justify-end gap-4">
            <span className="text-sm text-slate-600">Total Charges:</span>
            <motion.span
              key={targetTotal}
              initial={prefersReducedMotion ? false : { opacity: 0.5, y: 4 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{
                duration: prefersReducedMotion ? 0 : 0.2,
                ease: "easeOut",
              }}
              className="font-mono text-2xl font-semibold text-slate-900"
            >
              {formatCurrency(displayedTotal)}
            </motion.span>
          </div>
        </div>
      </Card>
    </TooltipProvider>
  );
}
