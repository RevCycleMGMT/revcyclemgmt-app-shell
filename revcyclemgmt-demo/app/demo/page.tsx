"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import type { Variants } from "framer-motion";
import { ArrowRight, Clock, User } from "lucide-react";

import { StepIndicator } from "@/components/pipeline/StepIndicator";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { cn } from "@/lib/utils";
import { scenarios } from "@/lib/scenarios";
import type { Scenario } from "@/lib/scenarios";

const gridVariants: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
    },
  },
};

const cardVariants: Variants = {
  hidden: { opacity: 0, y: 18 },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.45,
      ease: "easeOut",
    },
  },
};

const complexityStyles: Record<Scenario["complexity"], string> = {
  Beginner: "border-emerald-200 bg-emerald-50 text-emerald-700",
  Intermediate: "border-amber-200 bg-amber-50 text-amber-700",
  Advanced: "border-rose-200 bg-rose-50 text-rose-700",
};

function ScenarioCard({ scenario }: { scenario: Scenario }) {
  return (
    <motion.div
      variants={cardVariants}
      whileHover={{ scale: 1.02 }}
      transition={{ duration: 0.2, ease: "easeOut" }}
      className="h-full"
    >
      <Link
        href={`/demo/${scenario.id}/encounter`}
        className="group block h-full rounded-xl focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-600 focus-visible:ring-offset-2"
        aria-label={`Start ${scenario.patient.name} scenario`}
      >
        <Card className="flex h-full flex-col rounded-xl border-slate-200 bg-white p-6 shadow-sm transition-all duration-200 ease-in-out group-hover:border-teal-200 group-hover:shadow-md">
          <CardHeader className="p-0">
            <div className="flex size-16 items-center justify-center rounded-full bg-teal-50 text-teal-700">
              <User className="size-12" aria-hidden="true" />
            </div>

            <div className="pt-5">
              <CardTitle className="text-xl font-semibold tracking-[0] text-slate-900">
                {scenario.patient.name}
              </CardTitle>
              <p className="mt-1 text-sm text-slate-500">
                {scenario.patient.age} &middot; {scenario.patient.sex} &middot;{" "}
                {scenario.patient.mrn}
              </p>
            </div>
          </CardHeader>

          <CardContent className="flex flex-1 flex-col p-0 pt-5">
            <h2 className="text-lg font-medium tracking-[0] text-slate-900">
              {scenario.title}
            </h2>
            <p className="mt-2 text-sm leading-6 text-slate-600">
              {scenario.shortDescription}
            </p>

            <div className="mt-5 flex flex-wrap items-center gap-3">
              <Badge
                variant="outline"
                className={cn(
                  "rounded-lg px-2.5 py-1",
                  complexityStyles[scenario.complexity]
                )}
              >
                {scenario.complexity}
              </Badge>
              <span className="inline-flex items-center gap-1.5 text-xs text-slate-500">
                <Clock className="size-3.5" aria-hidden="true" />~
                {scenario.estimatedMinutes} minute walkthrough
              </span>
            </div>

            <div className="mt-auto flex items-center justify-between border-t border-slate-200 pt-5">
              <span className="text-xs font-medium uppercase tracking-[0.14em] text-slate-500">
                {scenario.patient.insurance.payer}
              </span>
              <span className="inline-flex items-center gap-1 text-sm font-semibold text-teal-600 transition-transform duration-200 group-hover:translate-x-1">
                Start
                <ArrowRight className="size-4" aria-hidden="true" />
              </span>
            </div>
          </CardContent>
        </Card>
      </Link>
    </motion.div>
  );
}

export default function DemoPage() {
  return (
    <main className="min-h-dvh overflow-x-hidden bg-slate-50 px-6 py-10 text-slate-700">
      <div className="mx-auto flex w-full max-w-4xl flex-col gap-10">
        <StepIndicator currentStep={1} />

        <section className="text-center">
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-teal-600">
            Choose Scenario
          </p>
          <h1 className="mt-4 text-4xl font-semibold tracking-[0] text-slate-900">
            Pick the case to walk through.
          </h1>
          <p className="mx-auto mt-4 max-w-2xl text-base leading-7 text-slate-600">
            Start with a synthetic patient note, then move through coding, claim
            construction, form generation, submission, and remittance outcome.
          </p>
        </section>

        <motion.section
          className="grid grid-cols-2 gap-6 max-md:grid-cols-1"
          variants={gridVariants}
          initial="hidden"
          animate="visible"
        >
          {scenarios.map((scenario) => (
            <ScenarioCard key={scenario.id} scenario={scenario} />
          ))}
        </motion.section>
      </div>
    </main>
  );
}
