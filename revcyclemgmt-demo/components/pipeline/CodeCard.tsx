"use client";

import { useState } from "react";
import { HelpCircle } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";

interface CodeCardProps {
  type: "ICD-10" | "CPT";
  code: string;
  modifiers?: string[];
  description: string;
  why: string;
}

export function CodeCard({
  type,
  code,
  modifiers = [],
  description,
  why,
}: CodeCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <Card className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
      <div className="flex items-start justify-between gap-3">
        <Badge
          variant="outline"
          className="rounded-lg border-teal-200 bg-teal-50 text-teal-700"
        >
          {type}
        </Badge>
        {modifiers.length > 0 ? (
          <div className="flex flex-wrap justify-end gap-1.5">
            {modifiers.map((modifier) => (
              <Badge
                key={modifier}
                variant="outline"
                className="rounded-lg border-slate-200 bg-slate-50 text-slate-700"
              >
                -{modifier}
              </Badge>
            ))}
          </div>
        ) : null}
      </div>

      <div className="mt-3 font-mono text-2xl font-semibold tracking-[0] text-slate-900">
        {code}
        {modifiers.length > 0 ? (
          <span className="text-slate-500">-{modifiers.join("-")}</span>
        ) : null}
      </div>
      <p className="mt-1 text-sm leading-6 text-slate-700">{description}</p>

      <button
        type="button"
        className="mt-3 inline-flex items-center gap-1.5 text-xs font-semibold text-teal-600 hover:underline"
        onClick={() => setIsExpanded((value) => !value)}
        aria-expanded={isExpanded}
      >
        <HelpCircle className="size-3.5" aria-hidden="true" />
        Why?
      </button>

      {isExpanded ? (
        <div className="mt-3 border-l-2 border-teal-300 pl-3 text-sm italic leading-6 text-slate-600">
          {why}
        </div>
      ) : null}
    </Card>
  );
}
