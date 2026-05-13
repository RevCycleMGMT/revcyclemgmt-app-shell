"use client";

import { CheckCircle } from "lucide-react";
import { motion } from "framer-motion";

import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { formatCurrency } from "@/lib/claims/form-data";
import type { Procedure, RemittanceLine, Scenario } from "@/lib/scenarios";

interface RemittanceCardProps {
  scenario: Scenario;
}

const adjustmentSummaries: Record<string, string> = {
  "CO-45": "Charge exceeds fee schedule or maximum allowable.",
};

function getPaymentId(scenarioId: string) {
  return scenarioId === "scenario-01-preventive-htn"
    ? "2026-EFT-100001"
    : "2026-EFT-100002";
}

function getOutcomeText(scenario: Scenario) {
  return scenario.patient.insurance.payer.toLowerCase().includes("medicare")
    ? "Claim accepted and paid (Medicare rates applied)"
    : "Claim accepted and paid";
}

function getProcedureMap(procedures: Procedure[]) {
  return new Map(procedures.map((procedure) => [procedure.id, procedure]));
}

function getProcedure(
  line: RemittanceLine,
  procedureMap: Map<string, Procedure>
) {
  const procedure = procedureMap.get(line.procedureId);

  if (!procedure) {
    throw new Error(`Missing procedure for remittance line ${line.procedureId}`);
  }

  return procedure;
}

export function RemittanceCard({ scenario }: RemittanceCardProps) {
  const procedureMap = getProcedureMap(scenario.procedures);
  const totalAllowed = scenario.expectedRemittance.lines.reduce(
    (sum, line) => sum + line.allowed,
    0
  );

  return (
    <TooltipProvider delayDuration={150}>
      <motion.div
        initial={{ y: 30, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.6, ease: "easeOut" }}
      >
        <Card className="rounded-xl border-slate-200 bg-white p-8 shadow-md">
          <div className="mb-6 rounded-xl border border-emerald-100 bg-emerald-50 p-4 text-emerald-700">
            <div className="flex items-center gap-3">
              <CheckCircle className="size-5 shrink-0" aria-hidden="true" />
              <p className="text-sm font-semibold">{getOutcomeText(scenario)}</p>
            </div>
          </div>

          <div className="mb-6">
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-teal-600">
              Payer Response
            </p>
            <h2 className="mt-2 text-xl font-semibold tracking-[0] text-slate-900">
              835 Electronic Remittance Advice
            </h2>
            <p className="mt-2 text-sm text-slate-500">
              Check / Payment ID: {getPaymentId(scenario.id)} - Payment Date:
              Today
            </p>
          </div>

          <div className="overflow-hidden rounded-xl border border-slate-200">
            <div className="overflow-x-auto">
              <table className="w-full min-w-[740px] border-collapse text-left">
                <thead>
                  <tr className="bg-slate-50 text-xs uppercase tracking-wider text-slate-600">
                    <th className="p-4 font-semibold">CPT Code</th>
                    <th className="p-4 text-right font-semibold">Charged</th>
                    <th className="p-4 text-right font-semibold">Allowed</th>
                    <th className="p-4 text-right font-semibold">Paid</th>
                    <th className="p-4 text-right font-semibold">
                      Patient Resp
                    </th>
                    <th className="p-4 font-semibold">Adjustments</th>
                  </tr>
                </thead>
                <tbody>
                  {scenario.expectedRemittance.lines.map((line, index) => {
                    const procedure = getProcedure(line, procedureMap);
                    const charged = procedure.charge * procedure.units;

                    return (
                      <tr
                        key={line.procedureId}
                        className={
                          index % 2 === 0 ? "bg-white" : "bg-slate-50/50"
                        }
                      >
                        <td className="border-t border-slate-100 p-4 font-mono text-sm font-semibold text-slate-900">
                          {procedure.cpt}
                          {procedure.modifiers.length ? (
                            <span className="ml-1 text-slate-500">
                              -{procedure.modifiers.join("-")}
                            </span>
                          ) : null}
                        </td>
                        <td className="border-t border-slate-100 p-4 text-right font-mono text-sm text-slate-700">
                          {formatCurrency(charged)}
                        </td>
                        <td className="border-t border-slate-100 p-4 text-right font-mono text-sm text-slate-700">
                          {formatCurrency(line.allowed)}
                        </td>
                        <td className="border-t border-slate-100 p-4 text-right font-mono text-sm font-semibold text-emerald-600">
                          {formatCurrency(line.paid)}
                        </td>
                        <td className="border-t border-slate-100 p-4 text-right font-mono text-sm font-semibold text-amber-600">
                          {formatCurrency(line.patientResponsibility)}
                        </td>
                        <td className="border-t border-slate-100 p-4">
                          <div className="flex flex-wrap gap-1.5">
                            {line.adjustments.map((adjustment) => (
                              <Tooltip key={`${line.procedureId}-${adjustment.code}`}>
                                <TooltipTrigger asChild>
                                  <span className="inline-flex cursor-help">
                                    <Badge
                                      variant="outline"
                                      className="rounded-lg border-slate-200 bg-slate-50 font-mono text-slate-700"
                                    >
                                      {adjustment.code}:{" "}
                                      {formatCurrency(adjustment.amount)}
                                    </Badge>
                                  </span>
                                </TooltipTrigger>
                                <TooltipContent className="max-w-xs text-sm leading-5">
                                  {adjustment.code}:{" "}
                                  {adjustmentSummaries[adjustment.code] ??
                                    adjustment.description}
                                </TooltipContent>
                              </Tooltip>
                            ))}
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>

          <div className="mt-6 flex justify-end">
            <div className="w-full max-w-sm rounded-xl border border-slate-200 bg-slate-50 p-5">
              <dl className="space-y-3">
                <div className="flex items-center justify-between gap-4">
                  <dt className="text-sm text-slate-600">Total Charges:</dt>
                  <dd className="font-mono text-sm font-semibold text-slate-900">
                    {formatCurrency(scenario.totalCharges)}
                  </dd>
                </div>
                <div className="flex items-center justify-between gap-4">
                  <dt className="text-sm text-slate-600">Total Allowed:</dt>
                  <dd className="font-mono text-sm font-semibold text-slate-900">
                    {formatCurrency(totalAllowed)}
                  </dd>
                </div>
                <div className="flex items-center justify-between gap-4">
                  <dt className="text-sm text-slate-600">Total Paid:</dt>
                  <dd className="font-mono text-xl font-semibold text-emerald-600">
                    {formatCurrency(scenario.expectedRemittance.totalPaid)}
                  </dd>
                </div>
                <div className="flex items-center justify-between gap-4">
                  <dt className="text-sm text-slate-600">
                    Patient Responsibility:
                  </dt>
                  <dd className="font-mono text-sm font-semibold text-amber-600">
                    {formatCurrency(
                      scenario.expectedRemittance.totalPatientResponsibility
                    )}
                  </dd>
                </div>
                <div className="flex items-center justify-between gap-4">
                  <dt className="text-sm text-slate-600">Total Adjustments:</dt>
                  <dd className="font-mono text-sm font-semibold text-slate-500">
                    {formatCurrency(
                      scenario.expectedRemittance.totalAdjustments
                    )}
                  </dd>
                </div>
              </dl>
            </div>
          </div>
        </Card>
      </motion.div>
    </TooltipProvider>
  );
}
