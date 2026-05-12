import { Check } from "lucide-react";

import { cn } from "@/lib/utils";

const stepLabels = [
  "Choose Scenario",
  "Review Encounter",
  "Code It",
  "Build Claim",
  "Generate Forms",
  "Submit",
  "Outcome",
];

interface StepIndicatorProps {
  currentStep?: number;
}

export function StepIndicator({ currentStep = 1 }: StepIndicatorProps) {
  return (
    <div className="w-full" aria-label="Demo progress">
      <div className="grid grid-cols-7 items-start">
        {stepLabels.map((label, index) => {
          const step = index + 1;
          const isCompleted = step < currentStep;
          const isCurrent = step === currentStep;
          const isFuture = step > currentStep;
          const isLineActive = step < currentStep;

          return (
            <div key={label} className="relative flex min-w-0 flex-col items-center">
              {index < stepLabels.length - 1 ? (
                <div
                  className={cn(
                    "absolute left-1/2 top-5 h-px w-full",
                    isLineActive ? "bg-teal-600" : "bg-slate-200"
                  )}
                  aria-hidden="true"
                />
              ) : null}

              <div
                className={cn(
                  "relative z-10 flex size-10 items-center justify-center rounded-full text-sm font-semibold shadow-sm ring-4 ring-slate-50",
                  isCompleted && "bg-emerald-600 text-white",
                  isCurrent && "bg-teal-600 text-white",
                  isFuture && "bg-slate-200 text-slate-500"
                )}
                aria-current={isCurrent ? "step" : undefined}
              >
                {isCompleted ? (
                  <Check className="size-4" aria-hidden="true" />
                ) : (
                  step
                )}
              </div>

              <p
                className={cn(
                  "mt-3 max-w-24 text-center text-xs font-medium leading-4",
                  isCurrent ? "text-slate-900" : "text-slate-500"
                )}
              >
                {label}
              </p>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export { stepLabels };
