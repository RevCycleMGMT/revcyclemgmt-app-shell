import type { Scenario } from "./types";

export const scenario01PreventiveHtn: Scenario = {
  id: "scenario-01-preventive-htn",
  title: "Sarah Chen - Annual Physical + Hypertension Follow-Up",
  shortDescription:
    "Established adult preventive visit with a separately identifiable hypertension follow-up.",
  complexity: "Beginner",
  estimatedMinutes: 10,
  patient: {
    name: "Sarah Chen",
    dob: "1981-03-14",
    age: 45,
    sex: "F",
    mrn: "100-001-2024",
    insurance: {
      payer: "BCBS PPO",
      memberId: "BSC-XXX-4421",
      planType: "PPO",
    },
  },
  encounter: {
    dateOfService: "2026-05-15",
    placeOfService: "11 (Office)",
    providerName: "Dr. James Park",
    providerNpi: "1234567890",
    note: [
      {
        id: "cc",
        label: "Chief Complaint",
        content: "Annual physical. Follow-up on hypertension.",
      },
      {
        id: "hpi",
        label: "HPI",
        content:
          "45 y/o established female presents for routine annual physical examination and hypertension follow-up. Patient reports good adherence to lisinopril 10 mg daily. Denies headaches, chest pain, vision changes, or peripheral edema. Diet and exercise unchanged since last visit.",
      },
      {
        id: "pmhx",
        label: "Past Medical History",
        content:
          "Essential hypertension, diagnosed 2021. No other chronic conditions.",
      },
      {
        id: "pe",
        label: "Physical Exam",
        content:
          "VS: BP 128/82 (improved from prior 142/90), HR 72, BMI 24. General: well-appearing. Cardiac: RRR, no murmurs. Resp: clear. Abdomen: benign. Extremities: no edema. Full preventive exam performed including age-appropriate screenings reviewed.",
      },
      {
        id: "ap",
        label: "Assessment & Plan",
        content:
          "1. Routine adult medical examination - no abnormal findings. Counseled on diet, exercise, cancer screening, immunizations updated. 2. Essential hypertension - well-controlled on current regimen. Continue lisinopril 10 mg daily. Recheck in 6 months. Labs ordered (BMP, lipid panel). The hypertension follow-up is documented as separately identifiable from the preventive service.",
      },
    ],
    highlightedPhrases: [
      {
        text: "annual physical examination",
        noteSectionId: "hpi",
        startOffset: 47,
        endOffset: 74,
        reveals: "procedure",
        linksToCodeId: "proc-99396",
      },
      {
        text: "hypertension follow-up",
        noteSectionId: "hpi",
        startOffset: 79,
        endOffset: 101,
        reveals: "diagnosis",
        linksToCodeId: "dx-i10",
      },
      {
        text: "lisinopril 10 mg daily",
        noteSectionId: "hpi",
        startOffset: 137,
        endOffset: 159,
        reveals: "context",
        linksToCodeId: "dx-i10",
      },
      {
        text: "BP 128/82",
        noteSectionId: "pe",
        startOffset: 4,
        endOffset: 13,
        reveals: "context",
        linksToCodeId: "dx-i10",
      },
      {
        text: "no abnormal findings",
        noteSectionId: "ap",
        startOffset: 39,
        endOffset: 59,
        reveals: "diagnosis",
        linksToCodeId: "dx-z0000",
      },
      {
        text: "Essential hypertension",
        noteSectionId: "ap",
        startOffset: 134,
        endOffset: 156,
        reveals: "diagnosis",
        linksToCodeId: "dx-i10",
      },
      {
        text: "separately identifiable",
        noteSectionId: "ap",
        startOffset: 326,
        endOffset: 349,
        reveals: "modifier",
        linksToCodeId: "proc-99213",
      },
    ],
  },
  diagnoses: [
    {
      id: "dx-z0000",
      code: "Z00.00",
      description:
        "Encounter for general adult medical examination without abnormal findings",
      why: "Documents the preventive intent of the visit. Required as the primary diagnosis when billing 99396.",
    },
    {
      id: "dx-i10",
      code: "I10",
      description: "Essential (primary) hypertension",
      why: "Documents the chronic condition addressed during the same visit. Pointed to the problem-focused E&M.",
    },
  ],
  procedures: [
    {
      id: "proc-99396",
      cpt: "99396",
      modifiers: [],
      description:
        "Periodic comprehensive preventive medicine, established patient, 40-64 years",
      diagnosisPointers: ["dx-z0000"],
      charge: 250,
      units: 1,
      why: "Age-appropriate preventive visit code for established patients 40-64.",
    },
    {
      id: "proc-99213",
      cpt: "99213",
      modifiers: ["25"],
      description:
        "Office or other outpatient visit, established patient, low complexity",
      diagnosisPointers: ["dx-i10"],
      charge: 125,
      units: 1,
      why: "Modifier 25 signals a significant, separately identifiable service from the preventive visit. Without it, payers bundle this E&M into 99396 and you lose the reimbursement.",
    },
  ],
  totalCharges: 375,
  expectedRemittance: {
    lines: [
      {
        procedureId: "proc-99396",
        allowed: 220,
        paid: 220,
        patientResponsibility: 0,
        adjustments: [
          {
            code: "CO-45",
            description: "Charge exceeds fee schedule/maximum allowable.",
            amount: 30,
          },
        ],
      },
      {
        procedureId: "proc-99213",
        allowed: 98,
        paid: 68,
        patientResponsibility: 30,
        adjustments: [
          {
            code: "CO-45",
            description: "Charge exceeds fee schedule/maximum allowable.",
            amount: 27,
          },
        ],
      },
    ],
    totalPaid: 288,
    totalPatientResponsibility: 30,
    totalAdjustments: 57,
  },
  teachingNotes: [
    {
      step: "encounter",
      text: "Two distinct services in one visit - this is the most common AAPC exam topic for E&M coding.",
    },
    {
      step: "coding",
      text: "Z00.00 captures the preventive intent. I10 captures the chronic condition addressed during the same visit. Both are billable when properly documented as separate work.",
    },
    {
      step: "claim",
      text: "Modifier 25 is essential here - without it, payers will bundle 99213 into 99396 and you'll lose the $98 reimbursement.",
    },
    {
      step: "forms",
      text: "Notice how the modifier appears in Box 24D of the CMS-1500. Box 21 lists both ICD-10 codes; Box 24E points each procedure to its diagnosis.",
    },
    {
      step: "submit",
      text: "BCBS reimbursed the preventive at 100% (ACA mandate) but applied a $30 copay to the problem-focused E&M. This is the most common patient confusion.",
    },
  ],
};
