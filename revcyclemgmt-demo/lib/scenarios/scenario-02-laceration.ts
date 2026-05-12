import type { Scenario } from "./types";

export const scenario02Laceration: Scenario = {
  id: "scenario-02-laceration",
  title: "James Wilson - Laceration Repair + Brief E&M",
  shortDescription:
    "Established patient laceration repair with E&M, modifier 25, and tetanus update.",
  complexity: "Intermediate",
  estimatedMinutes: 12,
  patient: {
    name: "James Wilson",
    dob: "1963-07-22",
    age: 62,
    sex: "M",
    mrn: "100-001-2025",
    insurance: {
      payer: "Medicare Part B",
      memberId: "1AB-2CD-3EF45",
      planType: "Medicare Part B",
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
        content: "Cut on right forearm from kitchen knife. ~1 hour ago.",
      },
      {
        id: "hpi",
        label: "HPI",
        content:
          "62 y/o established male presents with a 4 cm laceration on the volar aspect of the right forearm, sustained ~1 hour ago while cutting vegetables. No foreign body sensation, no numbness or tingling. Last tetanus 2019.",
      },
      {
        id: "pmhx",
        label: "Past Medical History",
        content: "Type 2 diabetes (well-controlled, A1c 6.8), hyperlipidemia.",
      },
      {
        id: "pe",
        label: "Physical Exam",
        content:
          "VS stable. Right forearm: 4 cm linear laceration, volar aspect, mid-forearm. Edges clean, minimal bleeding. No tendon involvement, intact neurovascular exam distal to wound. No foreign body visualized.",
      },
      {
        id: "ap",
        label: "Assessment & Plan",
        content:
          "1. Laceration of right forearm, 4 cm, no foreign body. Wound cleaned with saline irrigation, inspected. Closed with 5 interrupted sutures using 4-0 nylon. Sterile dressing applied. Tetanus updated. Return in 10 days for suture removal. Wound care instructions reviewed. 2. Brief E&M to assess for occult injury, neurovascular status, and review of medical history relevant to wound healing (diabetes).",
      },
    ],
    highlightedPhrases: [
      {
        text: "4 cm laceration on the volar aspect of the right forearm",
        noteSectionId: "hpi",
        startOffset: 40,
        endOffset: 96,
        reveals: "diagnosis",
        linksToCodeId: "dx-s51811a",
      },
      {
        text: "while cutting vegetables",
        noteSectionId: "hpi",
        startOffset: 120,
        endOffset: 144,
        reveals: "diagnosis",
        linksToCodeId: "dx-w260xxa",
      },
      {
        text: "Closed with 5 interrupted sutures",
        noteSectionId: "ap",
        startOffset: 104,
        endOffset: 137,
        reveals: "procedure",
        linksToCodeId: "proc-12002",
      },
      {
        text: "Brief E&M to assess",
        noteSectionId: "ap",
        startOffset: 273,
        endOffset: 292,
        reveals: "modifier",
        linksToCodeId: "proc-99213-25",
      },
      {
        text: "Tetanus updated",
        noteSectionId: "ap",
        startOffset: 181,
        endOffset: 196,
        reveals: "procedure",
        linksToCodeId: "proc-90471",
      },
      {
        text: "review of medical history relevant to wound healing (diabetes)",
        noteSectionId: "ap",
        startOffset: 338,
        endOffset: 400,
        reveals: "diagnosis",
        linksToCodeId: "dx-e119",
      },
    ],
  },
  diagnoses: [
    {
      id: "dx-s51811a",
      code: "S51.811A",
      description:
        "Laceration without foreign body of right forearm, initial encounter",
      why: "Documents wound type, anatomic site, laterality, absence of foreign body, and initial encounter status.",
    },
    {
      id: "dx-w260xxa",
      code: "W26.0XXA",
      description: "Contact with knife, initial encounter",
      why: "External cause code explains the mechanism of injury and reinforces complete injury-code sequencing.",
    },
    {
      id: "dx-e119",
      code: "E11.9",
      description: "Type 2 diabetes mellitus without complications",
      why: "Documents the comorbidity reviewed because diabetes can affect wound healing and supports the separate E&M context.",
    },
  ],
  procedures: [
    {
      id: "proc-99213-25",
      cpt: "99213",
      modifiers: ["25"],
      description:
        "Office or other outpatient visit, established patient, low complexity",
      diagnosisPointers: ["dx-s51811a"],
      charge: 125,
      units: 1,
      why: "Modifier 25 separates the E&M from the laceration repair when the provider documents separately identifiable assessment work.",
    },
    {
      id: "proc-12002",
      cpt: "12002",
      modifiers: [],
      description: "Simple repair of superficial wounds, 2.6-7.5 cm",
      diagnosisPointers: ["dx-s51811a"],
      charge: 190,
      units: 1,
      why: "A 4 cm simple forearm repair falls in the 2.6-7.5 cm simple repair range.",
    },
    {
      id: "proc-90471",
      cpt: "90471",
      modifiers: [],
      description: "Immunization administration, one vaccine",
      diagnosisPointers: ["dx-s51811a"],
      charge: 30,
      units: 1,
      why: "Administration is separately reported from the vaccine product when the tetanus update is given.",
    },
    {
      id: "proc-90714",
      cpt: "90714",
      modifiers: [],
      description: "Td vaccine",
      diagnosisPointers: ["dx-s51811a"],
      charge: 45,
      units: 1,
      why: "Reports the tetanus and diphtheria vaccine product supplied during the encounter.",
    },
  ],
  totalCharges: 390,
  expectedRemittance: {
    lines: [
      {
        procedureId: "proc-99213-25",
        allowed: 73.5,
        paid: 58.8,
        patientResponsibility: 14.7,
        adjustments: [
          {
            code: "CO-45",
            description: "Charge exceeds fee schedule/maximum allowable.",
            amount: 51.5,
          },
        ],
      },
      {
        procedureId: "proc-12002",
        allowed: 138.2,
        paid: 110.56,
        patientResponsibility: 27.64,
        adjustments: [
          {
            code: "CO-45",
            description: "Charge exceeds fee schedule/maximum allowable.",
            amount: 51.8,
          },
        ],
      },
      {
        procedureId: "proc-90471",
        allowed: 20.42,
        paid: 20.42,
        patientResponsibility: 0,
        adjustments: [
          {
            code: "CO-45",
            description: "Charge exceeds fee schedule/maximum allowable.",
            amount: 9.58,
          },
        ],
      },
      {
        procedureId: "proc-90714",
        allowed: 40,
        paid: 40,
        patientResponsibility: 0,
        adjustments: [
          {
            code: "CO-45",
            description: "Charge exceeds fee schedule/maximum allowable.",
            amount: 5,
          },
        ],
      },
    ],
    totalPaid: 229.78,
    totalPatientResponsibility: 42.34,
    totalAdjustments: 117.88,
  },
  teachingNotes: [
    {
      step: "encounter",
      text: "Procedure + E&M visits trip up new coders constantly. The decision: is the E&M a separate, identifiable service or just pre-procedure assessment?",
    },
    {
      step: "coding",
      text: "S codes require external cause (W26.0) and encounter type ('A' for initial). Many students drop the 'A' and lose specificity.",
    },
    {
      step: "claim",
      text: "Modifier 25 on 99213 is what separates this from a procedure-bundled visit. Without it, you lose the $73.50 E&M reimbursement.",
    },
    {
      step: "forms",
      text: "Medicare requires the external cause code in the diagnosis pointers. Box 21 lists all three diagnoses.",
    },
    {
      step: "submit",
      text: "Medicare contractual adjustments are over 30% of charges. This is the reality of Medicare reimbursement new practices need to understand.",
    },
  ],
};
