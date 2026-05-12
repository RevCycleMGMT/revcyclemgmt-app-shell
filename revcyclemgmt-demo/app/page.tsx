"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import type { Variants } from "framer-motion";
import {
  ArrowRight,
  BadgeCheck,
  ClipboardList,
  FileText,
  Landmark,
  Layers3,
  ReceiptText,
  ShieldCheck,
  Sparkles,
  Stethoscope,
} from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { scenarios } from "@/lib/scenarios";

const workflowSteps = [
  {
    label: "Encounter Review",
    description: "Clinical note",
    icon: Stethoscope,
    status: "Ready",
  },
  {
    label: "AI-Assisted Coding",
    description: "ICD-10 + CPT",
    icon: Sparkles,
    status: "Ready",
  },
  {
    label: "Claim Builder",
    description: "Diagnosis pointers",
    icon: ClipboardList,
    status: "Ready",
  },
  {
    label: "CMS-1500 + 837",
    description: "Forms and EDI",
    icon: FileText,
    status: "Preview",
  },
  {
    label: "Clearinghouse",
    description: "Timed response",
    icon: Layers3,
    status: "Simulated",
  },
  {
    label: "835 Remittance",
    description: "Payment outcome",
    icon: ReceiptText,
    status: "Simulated",
  },
];

const claimSignals = [
  { label: "Clean-claim readiness", value: 94 },
  { label: "Modifier 25 decision", value: 88 },
  { label: "Remittance comprehension", value: 82 },
];

const container: Variants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.6,
      ease: "easeOut",
      staggerChildren: 0.1,
    },
  },
};

const item: Variants = {
  hidden: { opacity: 0, y: 12 },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.5,
      ease: "easeOut",
    },
  },
};

export default function Home() {
  const [primaryScenario, secondaryScenario] = scenarios;

  return (
    <main className="min-h-dvh overflow-x-hidden bg-slate-50 text-slate-700">
      <motion.div
        className="mx-auto grid min-h-dvh w-full max-w-[1440px] grid-cols-[280px_minmax(0,1fr)_340px] gap-6 px-6 py-6 max-xl:grid-cols-[248px_minmax(0,1fr)] max-lg:grid-cols-1"
        variants={container}
        initial="hidden"
        animate="visible"
      >
        <motion.aside
          className="flex min-h-[calc(100dvh-48px)] flex-col rounded-xl border border-slate-200 bg-white p-5 shadow-sm max-lg:min-h-0"
          variants={item}
        >
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-teal-600">
              RevCycleMGMT
            </p>
            <h2 className="mt-3 text-xl font-semibold tracking-[0] text-slate-900">
              Training Platform
            </h2>
            <p className="mt-2 text-sm leading-6 text-slate-500">
              Synthetic RCM scenarios from chart review through payment.
            </p>
          </div>

          <nav className="mt-8 space-y-2" aria-label="Revenue cycle workflow">
            {workflowSteps.map((step) => (
              <div
                key={step.label}
                className="group grid grid-cols-[36px_minmax(0,1fr)] gap-3 rounded-lg border border-transparent p-3 transition-colors duration-200 hover:border-teal-100 hover:bg-teal-50/60"
              >
                <span className="flex size-9 items-center justify-center rounded-lg bg-slate-100 text-slate-600 group-hover:bg-teal-100 group-hover:text-teal-700">
                  <step.icon className="size-4" aria-hidden="true" />
                </span>
                <span className="min-w-0">
                  <span className="block text-sm font-semibold text-slate-900">
                    {step.label}
                  </span>
                  <span className="mt-0.5 flex items-center justify-between gap-2 text-xs text-slate-500">
                    {step.description}
                    <span className="shrink-0 text-[11px] font-medium text-teal-700">
                      {step.status}
                    </span>
                  </span>
                </span>
              </div>
            ))}
          </nav>

          <div className="mt-auto rounded-lg border border-slate-200 bg-slate-50 p-4">
            <div className="flex items-center gap-2 text-sm font-semibold text-slate-900">
              <ShieldCheck className="size-4 text-teal-600" aria-hidden="true" />
              Synthetic only
            </div>
            <p className="mt-2 text-xs leading-5 text-slate-500">
              Built for classroom practice with no PHI, no payer credentials,
              and no live clearinghouse traffic.
            </p>
          </div>
        </motion.aside>

        <motion.section
          className="flex min-h-[calc(100dvh-48px)] flex-col justify-center rounded-xl border border-slate-200 bg-white p-8 shadow-sm max-lg:min-h-0 max-sm:p-5"
          variants={item}
        >
          <div className="mx-auto w-full max-w-3xl">
            <motion.div variants={item}>
              <Badge className="rounded-lg bg-teal-50 px-3 py-1 text-xs font-semibold uppercase tracking-[0.14em] text-teal-700 hover:bg-teal-50">
                RevCycleMGMT Training Platform
              </Badge>
            </motion.div>

            <motion.h1
              className="mt-6 text-balance text-5xl font-semibold leading-[1.04] tracking-[0] text-slate-900 max-sm:text-4xl"
              variants={item}
            >
              Learn the revenue cycle on realistic claims.
            </motion.h1>

            <motion.p
              className="mt-6 max-w-xl text-lg leading-8 text-slate-600"
              variants={item}
            >
              Where future coders, billers, and RCM professionals practice the
              full claims pipeline on synthetic patient scenarios, built by
              AAPC-credentialed practitioners.
            </motion.p>

            <motion.div
              className="mt-8 flex flex-wrap items-center gap-4"
              variants={item}
            >
              <Button
                asChild
                size="lg"
                className="h-12 rounded-lg bg-teal-600 px-8 py-3 text-base font-semibold text-white shadow-sm transition-all duration-200 ease-in-out hover:-translate-y-0.5 hover:bg-teal-700 hover:shadow-md"
              >
                <Link href="/demo" aria-label="Start the RevCycleMGMT demo">
                  Start Demo
                  <ArrowRight className="size-4" aria-hidden="true" />
                </Link>
              </Button>
              <p className="text-sm text-slate-500">
                Built by an AAPC RCM Specialist &middot; MSHI &middot; MBA
              </p>
            </motion.div>

            <motion.div
              className="mt-10 grid grid-cols-2 gap-4 max-md:grid-cols-1"
              variants={item}
            >
              {[primaryScenario, secondaryScenario].map((scenario) => (
                <Card
                  key={scenario.id}
                  className="rounded-xl border-slate-200 bg-slate-50 shadow-none transition-all duration-200 hover:-translate-y-0.5 hover:border-teal-200 hover:bg-white hover:shadow-md"
                >
                  <CardHeader className="p-5 pb-3">
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <CardTitle className="text-base font-semibold tracking-[0] text-slate-900">
                          {scenario.patient.name}
                        </CardTitle>
                        <CardDescription className="mt-1 text-sm text-slate-500">
                          {scenario.patient.age}
                          {scenario.patient.sex} &middot;{" "}
                          {scenario.complexity} &middot;{" "}
                          {scenario.estimatedMinutes} min
                        </CardDescription>
                      </div>
                      <Badge
                        variant="outline"
                        className="rounded-lg border-teal-200 bg-white text-teal-700"
                      >
                        {scenario.patient.insurance.payer}
                      </Badge>
                    </div>
                  </CardHeader>
                  <CardContent className="px-5 pb-5">
                    <p className="text-sm leading-6 text-slate-600">
                      {scenario.shortDescription}
                    </p>
                    <div className="mt-4 flex items-center justify-between border-t border-slate-200 pt-4 text-sm">
                      <span className="text-slate-500">Charges</span>
                      <span className="font-semibold text-slate-900">
                        ${scenario.totalCharges}
                      </span>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </motion.div>
          </div>
        </motion.section>

        <motion.aside
          className="flex min-h-[calc(100dvh-48px)] flex-col gap-4 max-xl:col-span-2 max-xl:grid max-xl:min-h-0 max-xl:grid-cols-3 max-lg:col-span-1 max-lg:grid-cols-1"
          variants={item}
        >
          <Card className="rounded-xl border-slate-200 bg-white shadow-sm">
            <CardHeader className="p-5 pb-3">
              <div className="flex items-center gap-2 text-sm font-semibold text-slate-900">
                <BadgeCheck className="size-4 text-emerald-600" aria-hidden="true" />
                Demo readiness
              </div>
              <CardDescription className="text-sm text-slate-500">
                Scenario engine loaded and ready for guided instruction.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4 px-5 pb-5">
              {claimSignals.map((signal) => (
                <div key={signal.label}>
                  <div className="mb-2 flex items-center justify-between text-sm">
                    <span className="text-slate-500">{signal.label}</span>
                    <span className="font-semibold text-slate-900">
                      {signal.value}%
                    </span>
                  </div>
                  <Progress value={signal.value} className="h-2" />
                </div>
              ))}
            </CardContent>
          </Card>

          <Card className="rounded-xl border-slate-200 bg-white shadow-sm">
            <CardHeader className="p-5 pb-3">
              <div className="flex items-center gap-2 text-sm font-semibold text-slate-900">
                <Landmark className="size-4 text-teal-600" aria-hidden="true" />
                Remittance preview
              </div>
            </CardHeader>
            <CardContent className="space-y-3 px-5 pb-5">
              {scenarios.map((scenario) => (
                <div
                  key={scenario.id}
                  className="rounded-lg border border-slate-200 bg-slate-50 p-3"
                >
                  <div className="flex items-center justify-between gap-3 text-sm">
                    <span className="font-medium text-slate-700">
                      {scenario.patient.name}
                    </span>
                    <span className="font-semibold text-emerald-700">
                      ${scenario.expectedRemittance.totalPaid}
                    </span>
                  </div>
                  <p className="mt-1 text-xs text-slate-500">
                    Patient responsibility: $
                    {scenario.expectedRemittance.totalPatientResponsibility}
                  </p>
                </div>
              ))}
            </CardContent>
          </Card>

          <Card className="rounded-xl border-teal-100 bg-teal-50 shadow-sm">
            <CardHeader className="p-5 pb-3">
              <CardTitle className="text-base font-semibold tracking-[0] text-slate-900">
                Friday demo path
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 px-5 pb-5 text-sm leading-6 text-slate-600">
              <p>
                Open with the two reviewed clinical notes, then move through
                coding, claim build, CMS-1500, X12, clearinghouse response, and
                835 outcome.
              </p>
              <p className="text-xs font-medium uppercase tracking-[0.14em] text-teal-700">
                Synthetic data, no PHI
              </p>
            </CardContent>
          </Card>
        </motion.aside>
      </motion.div>

      <p className="pb-5 text-center text-xs text-slate-400">
        &copy; 2026 RevCycleMGMT &middot; Synthetic data, no PHI
      </p>
    </main>
  );
}
