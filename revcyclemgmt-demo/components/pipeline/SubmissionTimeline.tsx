"use client";

import { useEffect, useState } from "react";
import { CheckCircle, Loader2, Send } from "lucide-react";
import { motion } from "framer-motion";

import { Card } from "@/components/ui/card";
import { cn } from "@/lib/utils";

const timelineNodes = [
  {
    id: "submitted",
    delayMs: 0,
    timestamp: "T+0.0s",
    label: "Submitted to clearinghouse",
    description: "837P claim file transmitted",
    icon: Send,
  },
  {
    id: "ack-999",
    delayMs: 1500,
    timestamp: "T+1.5s",
    label: "999 acknowledgment received",
    description: "Clearinghouse confirms file received",
    icon: CheckCircle,
  },
  {
    id: "ack-277ca",
    delayMs: 3000,
    timestamp: "T+3.0s",
    label: "277CA: Accepted by payer",
    description: "Payer accepts claim for adjudication",
    icon: CheckCircle,
  },
  {
    id: "adjudicating",
    delayMs: 4500,
    timestamp: "T+4.5s",
    label: "Adjudicating...",
    description: "Payer is applying contract and benefit rules",
    icon: Loader2,
  },
  {
    id: "remit-ready",
    delayMs: 7000,
    timestamp: "T+7.0s",
    label: "835 remittance ready",
    description: "Payment and adjustment details returned",
    icon: CheckCircle,
  },
];

export function SubmissionTimeline() {
  const [activeStep, setActiveStep] = useState(1);
  const [completedStep, setCompletedStep] = useState(1);

  useEffect(() => {
    const timers = timelineNodes.map((node, index) =>
      window.setTimeout(() => {
        const step = index + 1;

        setActiveStep(step);
        setCompletedStep(step);
      }, node.delayMs)
    );

    return () => {
      timers.forEach((timer) => window.clearTimeout(timer));
    };
  }, []);

  return (
    <Card className="rounded-xl border-slate-200 bg-white p-6 shadow-sm">
      <div className="mb-6">
        <p className="text-xs font-semibold uppercase tracking-[0.18em] text-teal-600">
          Clearinghouse Submission
        </p>
        <h2 className="mt-2 text-xl font-semibold tracking-[0] text-slate-900">
          Claim Status Timeline
        </h2>
      </div>

      <div className="space-y-0">
        {timelineNodes.map((node, index) => {
          const step = index + 1;
          const isActive = step === activeStep && completedStep < timelineNodes.length;
          const isComplete = step <= completedStep;
          const isFuture = step > completedStep;
          const Icon = node.icon;
          const showSpinner = node.id === "adjudicating" && isActive;

          return (
            <div key={node.id} className="relative flex gap-4">
              {index < timelineNodes.length - 1 ? (
                <div
                  className={cn(
                    "absolute left-5 top-10 h-full border-l-2",
                    step < completedStep ? "border-teal-600" : "border-slate-200"
                  )}
                  aria-hidden="true"
                />
              ) : null}

              <motion.div
                initial={{ scale: 0, opacity: 0 }}
                animate={{
                  scale: isFuture ? 0.9 : 1,
                  opacity: isFuture ? 0.45 : 1,
                }}
                transition={{ duration: 0.28, ease: "easeOut" }}
                className={cn(
                  "relative z-10 flex size-10 shrink-0 items-center justify-center rounded-full border shadow-sm",
                  isComplete
                    ? "border-teal-600 bg-teal-600 text-white"
                    : "border-slate-200 bg-slate-100 text-slate-500",
                  isActive && "ring-4 ring-teal-100"
                )}
              >
                {isActive ? (
                  <motion.span
                    className="absolute inset-0 rounded-full bg-teal-400/20"
                    animate={{ scale: [1, 1.35, 1], opacity: [0.4, 0, 0.4] }}
                    transition={{
                      duration: 1.4,
                      repeat: Infinity,
                      ease: "easeInOut",
                    }}
                  />
                ) : null}
                <Icon
                  className={cn("relative size-5", showSpinner && "animate-spin")}
                  aria-hidden="true"
                />
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 8 }}
                animate={{
                  opacity: isFuture ? 0.5 : 1,
                  y: 0,
                }}
                transition={{ duration: 0.28, delay: isFuture ? 0 : 0.05 }}
                className="min-h-[82px] flex-1 pb-5"
              >
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <h3
                      className={cn(
                        "text-sm font-semibold",
                        isFuture ? "text-slate-500" : "text-slate-900"
                      )}
                    >
                      {node.label}
                    </h3>
                    <p className="mt-1 text-sm leading-6 text-slate-500">
                      {node.description}
                    </p>
                  </div>
                  <span className="rounded-lg bg-slate-50 px-2 py-1 font-mono text-xs text-slate-500">
                    {node.timestamp}
                  </span>
                </div>
              </motion.div>
            </div>
          );
        })}
      </div>
    </Card>
  );
}
