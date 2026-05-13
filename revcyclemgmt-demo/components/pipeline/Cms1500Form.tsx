"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import type { ReactNode } from "react";
import { motion, useReducedMotion } from "framer-motion";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import {
  buildCms1500Fields,
  type ClaimFormData,
  type ServiceLine,
} from "@/lib/claims/form-data";
import { cn } from "@/lib/utils";

interface Cms1500FormProps {
  formData: ClaimFormData;
}

interface FormBoxProps {
  number: string;
  label: string;
  className?: string;
  children?: ReactNode;
}

const lineGridColumns =
  "96px 50px 118px 72px 90px 58px 128px 1fr";

function sleep(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function FormBox({ number, label, className, children }: FormBoxProps) {
  return (
    <div
      className={cn(
        "relative overflow-hidden border-b border-r border-black p-1 text-black",
        className
      )}
    >
      <div className="flex items-start gap-1">
        <span className="min-w-4 text-[8px] font-semibold leading-none">
          {number}
        </span>
        <span className="text-[7px] font-medium uppercase leading-none tracking-[0]">
          {label}
        </span>
      </div>
      <div className="mt-1 whitespace-pre-line font-mono text-[10px] leading-tight">
        {children}
      </div>
    </div>
  );
}

function CheckField({
  label,
  value,
}: {
  label: string;
  value: string;
}) {
  return (
    <span className="inline-flex items-center gap-1">
      <span className="flex size-3 items-center justify-center border border-black font-mono text-[9px] leading-none">
        {value}
      </span>
      <span>{label}</span>
    </span>
  );
}

function DataText({ value, className }: { value: string; className?: string }) {
  return (
    <span className={cn("inline-block min-h-[12px]", className)}>{value}</span>
  );
}

function ServiceLineRow({
  line,
  getValue,
}: {
  line: ServiceLine;
  getValue: (fieldId: string) => string;
}) {
  return (
    <div
      className="grid min-h-10 border-b border-black font-mono text-[10px] leading-tight"
      style={{ gridTemplateColumns: lineGridColumns }}
    >
      <div className="border-r border-black p-1">
        <DataText value={getValue(`box24-${line.lineNumber}-date`)} />
      </div>
      <div className="border-r border-black p-1">
        <DataText value={getValue(`box24-${line.lineNumber}-pos`)} />
      </div>
      <div className="border-r border-black p-1">
        <DataText value={getValue(`box24-${line.lineNumber}-cpt`)} />
        <span className="ml-3">
          <DataText value={getValue(`box24-${line.lineNumber}-mod`)} />
        </span>
      </div>
      <div className="border-r border-black p-1">
        <DataText value={getValue(`box24-${line.lineNumber}-diag`)} />
      </div>
      <div className="border-r border-black p-1 text-right">
        <DataText value={getValue(`box24-${line.lineNumber}-charge`)} />
      </div>
      <div className="border-r border-black p-1 text-center">
        <DataText value={getValue(`box24-${line.lineNumber}-units`)} />
      </div>
      <div className="border-r border-black p-1">
        <DataText value={getValue(`box24-${line.lineNumber}-npi`)} />
      </div>
      <div className="p-1" />
    </div>
  );
}

export function Cms1500Form({ formData }: Cms1500FormProps) {
  const prefersReducedMotion = Boolean(useReducedMotion());
  const fields = useMemo(() => buildCms1500Fields(formData), [formData]);
  const completeValues = useMemo(
    () => Object.fromEntries(fields.map((field) => [field.id, field.value])),
    [fields]
  );
  const [animatedValues, setAnimatedValues] = useState<Record<string, string>>(
    {}
  );
  const [isComplete, setIsComplete] = useState(false);
  const skipRequestedRef = useRef(false);

  useEffect(() => {
    let cancelled = false;

    skipRequestedRef.current = false;

    if (prefersReducedMotion) {
      setAnimatedValues(completeValues);
      setIsComplete(true);
      return () => {
        cancelled = true;
      };
    }

    async function runTypewriter() {
      const nextValues: Record<string, string> = {};

      setIsComplete(false);
      setAnimatedValues({});

      await sleep(300);

      for (const field of fields) {
        for (let index = 1; index <= field.value.length; index += 1) {
          if (cancelled || skipRequestedRef.current) {
            return;
          }

          nextValues[field.id] = field.value.slice(0, index);
          setAnimatedValues({ ...nextValues });
          await sleep(30);
        }

        if (cancelled || skipRequestedRef.current) {
          return;
        }

        await sleep(200);
      }

      if (!cancelled) {
        setIsComplete(true);
      }
    }

    runTypewriter();

    return () => {
      cancelled = true;
    };
  }, [completeValues, fields, prefersReducedMotion]);

  const skipAnimation = () => {
    skipRequestedRef.current = true;
    setAnimatedValues(completeValues);
    setIsComplete(true);
  };

  const getValue = (fieldId: string) => animatedValues[fieldId] ?? "";

  return (
    <Card className="rounded-xl border-slate-200 bg-white p-6 shadow-sm">
      <div className="mb-4 flex items-center justify-between gap-4">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-teal-600">
            CMS-1500
          </p>
          <h2 className="mt-2 text-lg font-semibold tracking-[0] text-slate-900">
            Professional Claim Form
          </h2>
        </div>
        <Button
          type="button"
          variant="outline"
          className="rounded-lg border-slate-200"
          onClick={skipAnimation}
          disabled={isComplete}
        >
          Skip animation
        </Button>
      </div>

      <div className="overflow-x-auto pb-2">
        <motion.div
          initial={prefersReducedMotion ? false : { opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: prefersReducedMotion ? 0 : 0.4, ease: "easeOut" }}
          className="mx-auto aspect-[8.5/11] w-[920px] bg-white font-sans text-black shadow-sm ring-1 ring-black"
        >
          <div className="flex h-full flex-col border-l border-t border-black">
            <div className="grid h-16 grid-cols-12">
              <FormBox
                number="1"
                label="Medicare Medicaid Tricare Champva Group Health Plan Other"
                className="col-span-8"
              >
                <div className="mb-1 text-center text-[13px] font-semibold tracking-[0]">
                  HEALTH INSURANCE CLAIM FORM
                </div>
                <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-[8px]">
                  <CheckField
                    label="Medicare"
                    value={getValue("box1-medicare")}
                  />
                  <CheckField label="Medicaid" value="" />
                  <CheckField label="Tricare" value="" />
                  <CheckField label="ChampVA" value="" />
                  <CheckField
                    label="Group Health Plan"
                    value={getValue("box1-group")}
                  />
                  <CheckField label="Other" value="" />
                </div>
              </FormBox>
              <FormBox
                number="1a"
                label="Insured's I.D. Number"
                className="col-span-4"
              >
                <DataText value={getValue("box1a-insured-id")} />
              </FormBox>
            </div>

            <div className="grid h-[72px] grid-cols-12">
              <FormBox number="2" label="Patient's Name" className="col-span-4">
                <DataText value={getValue("box2-patient-name")} />
              </FormBox>
              <FormBox
                number="3"
                label="Patient's Birth Date / Sex"
                className="col-span-3"
              >
                <div className="flex items-center gap-5">
                  <DataText value={getValue("box3-dob")} />
                  <DataText value={getValue("box3-sex")} />
                </div>
              </FormBox>
              <FormBox number="4" label="Insured's Name" className="col-span-5">
                <DataText value={getValue("box4-insured-name")} />
              </FormBox>
            </div>

            <div className="grid h-[84px] grid-cols-12">
              <FormBox
                number="5"
                label="Patient's Address"
                className="col-span-4"
              >
                <DataText value={getValue("box5-address")} />
                <br />
                <DataText value={getValue("box5-city-state")} />
                <br />
                <DataText value={getValue("box5-phone")} />
              </FormBox>
              <FormBox
                number="6"
                label="Patient Relationship to Insured"
                className="col-span-3"
              >
                <div className="mt-2 flex flex-wrap gap-3 text-[8px]">
                  <CheckField label="Self" value={getValue("box6-self")} />
                  <CheckField label="Spouse" value="" />
                  <CheckField label="Child" value="" />
                  <CheckField label="Other" value="" />
                </div>
              </FormBox>
              <FormBox
                number="7"
                label="Insured's Address"
                className="col-span-5"
              >
                <DataText value={getValue("box7-address")} />
                <br />
                <DataText value={getValue("box7-city-state")} />
              </FormBox>
            </div>

            <div className="grid h-16 grid-cols-12">
              <FormBox number="8" label="Reserved for NUCC Use" className="col-span-4" />
              <FormBox number="9" label="Other Insured's Name" className="col-span-4" />
              <FormBox
                number="10"
                label="Patient's Condition Related To"
                className="col-span-4"
              >
                <div className="flex gap-4 text-[8px]">
                  <CheckField label="Employment" value="" />
                  <CheckField label="Auto Accident" value="" />
                  <CheckField label="Other Accident" value="" />
                </div>
              </FormBox>
            </div>

            <div className="grid h-16 grid-cols-12">
              <FormBox
                number="11"
                label="Insured's Policy Group or FECA Number"
                className="col-span-4"
              >
                <DataText value={getValue("box11-group")} />
              </FormBox>
              <FormBox
                number="11a"
                label="Insured's Date of Birth"
                className="col-span-2"
              />
              <FormBox number="11b" label="Other Claim ID" className="col-span-2" />
              <FormBox
                number="11c"
                label="Insurance Plan Name or Program Name"
                className="col-span-4"
              >
                <DataText value={getValue("box11c-plan")} />
              </FormBox>
            </div>

            <div className="grid h-[58px] grid-cols-12">
              <FormBox
                number="12"
                label="Patient's or Authorized Person's Signature"
                className="col-span-8"
              >
                SIGNATURE ON FILE
              </FormBox>
              <FormBox
                number="13"
                label="Insured's or Authorized Person's Signature"
                className="col-span-4"
              >
                SIGNATURE ON FILE
              </FormBox>
            </div>

            <div className="grid h-[150px] grid-cols-12">
              <FormBox number="14" label="Date of Current Illness" className="col-span-2" />
              <FormBox number="15" label="Other Date" className="col-span-2" />
              <FormBox number="16" label="Dates Patient Unable to Work" className="col-span-2" />
              <FormBox
                number="17"
                label="Name of Referring Provider"
                className="col-span-3"
              />
              <FormBox number="17b" label="NPI" className="col-span-3" />
              <FormBox
                number="21"
                label="Diagnosis or Nature of Illness or Injury"
                className="col-span-9"
              >
                <div className="grid grid-cols-2 gap-x-5 gap-y-1">
                  {formData.diagnoses.map((diagnosis) => (
                    <DataText
                      key={diagnosis.id}
                      value={getValue(`box21-${diagnosis.letter}`)}
                    />
                  ))}
                </div>
              </FormBox>
              <FormBox number="23" label="Prior Authorization Number" className="col-span-3" />
            </div>

            <div className="h-[360px] border-b border-r border-black">
              <div className="flex h-7 items-center border-b border-black px-1 text-[8px] font-semibold uppercase">
                <span className="mr-2 text-[8px]">24</span>
                Supplemental claim information and service lines
              </div>
              <div
                className="grid border-b border-black bg-slate-100 text-[7px] font-semibold uppercase leading-tight"
                style={{ gridTemplateColumns: lineGridColumns }}
              >
                <div className="border-r border-black p-1">24A Date(s) of Service</div>
                <div className="border-r border-black p-1">24B POS</div>
                <div className="border-r border-black p-1">24D CPT/HCPCS Mod</div>
                <div className="border-r border-black p-1">24E Diagnosis Pointer</div>
                <div className="border-r border-black p-1 text-right">24F Charges</div>
                <div className="border-r border-black p-1 text-center">24G Units</div>
                <div className="border-r border-black p-1">24J Rendering NPI</div>
                <div className="p-1">Reserved</div>
              </div>
              {formData.serviceLines.map((line) => (
                <ServiceLineRow
                  key={line.procedureId}
                  line={line}
                  getValue={getValue}
                />
              ))}
              {Array.from({ length: Math.max(0, 6 - formData.serviceLines.length) }).map(
                (_, index) => (
                  <div
                    key={index}
                    className="grid min-h-10 border-b border-black"
                    style={{ gridTemplateColumns: lineGridColumns }}
                  >
                    {Array.from({ length: 8 }).map((__, cellIndex) => (
                      <div
                        key={cellIndex}
                        className={cn(cellIndex < 7 && "border-r border-black")}
                      />
                    ))}
                  </div>
                )
              )}
            </div>

            <div className="grid h-[70px] grid-cols-12">
              <FormBox number="25" label="Federal Tax I.D. Number" className="col-span-3">
                <DataText value={getValue("box25-tax-id")} />
              </FormBox>
              <FormBox number="26" label="Patient Account No." className="col-span-2">
                {formData.patient.mrn}
              </FormBox>
              <FormBox number="27" label="Accept Assignment?" className="col-span-2">
                YES
              </FormBox>
              <FormBox number="28" label="Total Charge" className="col-span-2">
                <DataText value={getValue("box28-total")} />
              </FormBox>
              <FormBox number="29" label="Amount Paid" className="col-span-1" />
              <FormBox number="30" label="Reserved" className="col-span-2" />
            </div>

            <div className="grid flex-1 grid-cols-12">
              <FormBox
                number="31"
                label="Signature of Physician or Supplier"
                className="col-span-4"
              >
                {formData.encounter.providerName}
                <br />
                {formData.encounter.dateDisplay}
              </FormBox>
              <FormBox
                number="32"
                label="Service Facility Location Information"
                className="col-span-4"
              >
                {formData.billingProvider.name}
                <br />
                {formData.billingProvider.city}, {formData.billingProvider.state}
              </FormBox>
              <FormBox
                number="33"
                label="Billing Provider Info and Phone Number"
                className="col-span-4"
              >
                <DataText value={getValue("box33-provider")} />
                <br />
                <DataText value={getValue("box33-phone")} />
                <br />
                NPI <DataText value={getValue("box33-npi")} />
              </FormBox>
            </div>
          </div>
        </motion.div>
      </div>
    </Card>
  );
}
