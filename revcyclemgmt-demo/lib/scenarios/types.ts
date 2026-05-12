export interface Patient {
  name: string;
  dob: string; // ISO date
  age: number;
  sex: "M" | "F";
  mrn: string;
  insurance: {
    payer: string;
    memberId: string;
    planType: string;
  };
}

export interface HighlightedPhrase {
  text: string;
  noteSectionId: string; // 'cc' | 'hpi' | 'pe' | 'ap' etc.
  startOffset: number; // character offset within section
  endOffset: number;
  reveals: "diagnosis" | "procedure" | "modifier" | "context";
  linksToCodeId: string; // code identifier this phrase reveals
}

export interface ClinicalNoteSection {
  id: string;
  label: string; // 'Chief Complaint', 'HPI', etc.
  content: string; // markdown
}

export interface Diagnosis {
  id: string;
  code: string; // 'I10', 'Z00.00'
  description: string;
  why: string; // pedagogical explanation
}

export interface Procedure {
  id: string;
  cpt: string; // '99396'
  modifiers: string[]; // ['25']
  description: string;
  diagnosisPointers: string[]; // diagnosis ids
  charge: number;
  units: number;
  why: string;
}

export interface RemittanceLine {
  procedureId: string;
  allowed: number;
  paid: number;
  patientResponsibility: number;
  adjustments: { code: string; description: string; amount: number }[];
}

export interface TeachingNote {
  step: "encounter" | "coding" | "claim" | "forms" | "submit";
  text: string;
}

export interface Scenario {
  id: string;
  title: string;
  shortDescription: string;
  complexity: "Beginner" | "Intermediate" | "Advanced";
  estimatedMinutes: number;
  patient: Patient;
  encounter: {
    dateOfService: string;
    placeOfService: string;
    providerName: string;
    providerNpi: string;
    note: ClinicalNoteSection[];
    highlightedPhrases: HighlightedPhrase[];
  };
  diagnoses: Diagnosis[];
  procedures: Procedure[];
  totalCharges: number;
  expectedRemittance: {
    lines: RemittanceLine[];
    totalPaid: number;
    totalPatientResponsibility: number;
    totalAdjustments: number;
  };
  teachingNotes: TeachingNote[];
}
