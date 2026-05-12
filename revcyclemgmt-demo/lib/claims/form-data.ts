import type { Diagnosis, Procedure, Scenario } from "@/lib/scenarios";

export interface ClaimAddress {
  line1: string;
  city: string;
  state: string;
  zip: string;
  phone: string;
}

export interface DiagnosisEntry {
  id: string;
  letter: string;
  code: string;
  description: string;
}

export interface ServiceLine {
  procedureId: string;
  lineNumber: number;
  dateOfService: string;
  placeOfService: string;
  cpt: string;
  modifiers: string[];
  diagnosisPointerIds: string[];
  diagnosisPointerLetters: string;
  charge: number;
  units: number;
  renderingProviderNpi: string;
}

export interface ClaimFormData {
  scenarioId: string;
  payerName: string;
  planType: string;
  insuranceType: "medicare" | "group";
  insuredId: string;
  policyGroupNumber: string;
  patient: {
    fullName: string;
    firstName: string;
    lastName: string;
    dob: string;
    dobDisplay: string;
    dobX12: string;
    sex: "M" | "F";
    mrn: string;
    address: ClaimAddress;
  };
  insured: {
    fullName: string;
    address: ClaimAddress;
    relationship: "Self";
  };
  encounter: {
    dateOfService: string;
    dateDisplay: string;
    dateX12: string;
    placeOfServiceCode: string;
    providerName: string;
    providerNpi: string;
  };
  diagnoses: DiagnosisEntry[];
  serviceLines: ServiceLine[];
  billingProvider: {
    name: string;
    line1: string;
    city: string;
    state: string;
    zip: string;
    phone: string;
    taxId: string;
    npi: string;
  };
  totalCharges: number;
  x12: string;
}

export interface AnimatedCmsField {
  id: string;
  value: string;
}

const patientAddresses: Record<string, ClaimAddress> = {
  "Sarah Chen": {
    line1: "4821 Walnut Grove Ave",
    city: "Pasadena",
    state: "CA",
    zip: "91101",
    phone: "(626) 555-0148",
  },
  "James Wilson": {
    line1: "1176 Arroyo Vista Dr",
    city: "Monrovia",
    state: "CA",
    zip: "91016",
    phone: "(626) 555-0182",
  },
};

const billingProvider = {
  name: "RevCycleMGMT Medical Group",
  line1: "100 Training Way, Suite 400",
  city: "Pasadena",
  state: "CA",
  zip: "91101",
  phone: "(626) 555-0100",
  taxId: "95-7654321",
};

function splitPatientName(name: string) {
  const parts = name.trim().split(/\s+/);
  const firstName = parts[0] ?? "";
  const lastName = parts.slice(1).join(" ") || firstName;

  return {
    firstName,
    lastName,
    fullName: `${lastName}, ${firstName}`.trim(),
  };
}

export function formatCurrency(value: number) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: Number.isInteger(value) ? 0 : 2,
  }).format(value);
}

export function formatDateDisplay(isoDate: string) {
  const [year, month, day] = isoDate.split("-");
  return `${month}/${day}/${year}`;
}

function formatDateX12(isoDate: string) {
  return isoDate.replaceAll("-", "");
}

function getPlaceOfServiceCode(placeOfService: string) {
  return placeOfService.split(" ")[0] ?? placeOfService;
}

function compactCode(code: string) {
  return code.replace(".", "");
}

function getInsuranceType(payer: string): ClaimFormData["insuranceType"] {
  return payer.toLowerCase().includes("medicare") ? "medicare" : "group";
}

function getPolicyGroupNumber(scenario: Scenario) {
  if (getInsuranceType(scenario.patient.insurance.payer) === "medicare") {
    return "MEDICARE";
  }

  return "BSC-GRP-4421";
}

function getDiagnosisEntries(diagnoses: Diagnosis[]): DiagnosisEntry[] {
  return diagnoses.map((diagnosis, index) => ({
    id: diagnosis.id,
    letter: String.fromCharCode(65 + index),
    code: diagnosis.code,
    description: diagnosis.description,
  }));
}

function getServiceLines(
  scenario: Scenario,
  diagnoses: DiagnosisEntry[]
): ServiceLine[] {
  const diagnosisLetters = new Map(
    diagnoses.map((diagnosis) => [diagnosis.id, diagnosis.letter])
  );

  return scenario.procedures.map((procedure, index) => ({
    procedureId: procedure.id,
    lineNumber: index + 1,
    dateOfService: scenario.encounter.dateOfService,
    placeOfService: getPlaceOfServiceCode(scenario.encounter.placeOfService),
    cpt: procedure.cpt,
    modifiers: procedure.modifiers,
    diagnosisPointerIds: procedure.diagnosisPointers,
    diagnosisPointerLetters: procedure.diagnosisPointers
      .map((diagnosisId) => diagnosisLetters.get(diagnosisId) ?? "?")
      .join(""),
    charge: procedure.charge,
    units: procedure.units,
    renderingProviderNpi: scenario.encounter.providerNpi,
  }));
}

function payerId(payerName: string) {
  return payerName.toUpperCase().replace(/[^A-Z0-9]/g, "").slice(0, 15);
}

function serviceLineComposite(procedure: Procedure) {
  return ["HC", procedure.cpt, ...procedure.modifiers].join(":");
}

function buildX12EdiContent(
  scenario: Scenario,
  data: Omit<ClaimFormData, "x12">
) {
  const payer = payerId(data.payerName);
  const transactionId = scenario.id === "scenario-01-preventive-htn" ? "0001" : "0002";
  const diagnosisSegment = data.diagnoses
    .map((diagnosis, index) => `${index === 0 ? "ABK" : "ABF"}:${compactCode(diagnosis.code)}`)
    .join("*");
  const serviceSegments = scenario.procedures.flatMap((procedure, index) => {
    const serviceLine = data.serviceLines[index];
    const pointerIndexes = procedure.diagnosisPointers
      .map((diagnosisId) => data.diagnoses.findIndex((diagnosis) => diagnosis.id === diagnosisId) + 1)
      .filter((indexValue) => indexValue > 0)
      .join(":");

    return [
      `// LX: Service line ${index + 1}`,
      `LX*${index + 1}~`,
      `SV1*${serviceLineComposite(procedure)}*${procedure.charge.toFixed(2)}*UN*${procedure.units}***${pointerIndexes || "1"}~`,
      `DTP*472*D8*${data.encounter.dateX12}~`,
    ];
  });

  return [
    "// ISA: Interchange envelope header",
    `ISA*00*          *00*          *ZZ*REVCYCLEMGMT   *ZZ*${payer.padEnd(15, " ")}*260515*1700*^*00501*000000905*1*T*:~`,
    "// GS: Functional group header",
    `GS*HC*REVCYCLEMGMT*${payer}*${data.encounter.dateX12}*1700*1*X*005010X222A1~`,
    "// ST: Transaction set header",
    `ST*837*${transactionId}*005010X222A1~`,
    "// BHT: Beginning of hierarchical transaction",
    `BHT*0019*00*${scenario.id.toUpperCase().replace(/-/g, "")}*${data.encounter.dateX12}*1700*CH~`,
    "// NM1*41: Submitter",
    "NM1*41*2*REVCYCLEMGMT*****46*123456789~",
    "PER*IC*DEMO SUPPORT*TE*6265550100~",
    "// NM1*40: Receiver",
    `NM1*40*2*${data.payerName.toUpperCase()}*****46*${payer}~`,
    "// HL*1: Billing provider hierarchy",
    "HL*1**20*1~",
    "// NM1*85: Billing provider name with NPI",
    `NM1*85*2*${data.billingProvider.name.toUpperCase()}*****XX*${data.billingProvider.npi}~`,
    `N3*${data.billingProvider.line1.toUpperCase()}~`,
    `N4*${data.billingProvider.city.toUpperCase()}*${data.billingProvider.state}*${data.billingProvider.zip}~`,
    "// HL*2: Subscriber hierarchy",
    "HL*2*1*22*0~",
    "// SBR: Subscriber information",
    `SBR*P*18*${data.policyGroupNumber}******${data.insuranceType === "medicare" ? "MB" : "CI"}~`,
    "// NM1*IL: Subscriber name",
    `NM1*IL*1*${data.patient.lastName.toUpperCase()}*${data.patient.firstName.toUpperCase()}****MI*${data.insuredId}~`,
    "// DMG: Demographics",
    `DMG*D8*${data.patient.dobX12}*${data.patient.sex}~`,
    "// NM1*PR: Payer",
    `NM1*PR*2*${data.payerName.toUpperCase()}*****PI*${payer}~`,
    "// CLM: Claim header",
    `CLM*${data.patient.mrn}*${data.totalCharges.toFixed(2)}***${data.encounter.placeOfServiceCode}:B:1*Y*A*Y*Y~`,
    "// HI: Diagnosis codes",
    `HI*${diagnosisSegment}~`,
    ...serviceSegments,
    "// SE: Transaction set trailer",
    `SE*${26 + scenario.procedures.length * 3}*${transactionId}~`,
    "// GE: Functional group trailer",
    "GE*1*1~",
    "// IEA: Interchange envelope trailer",
    "IEA*1*000000905~",
  ].join("\n");
}

export function buildClaimFormData(scenario: Scenario): ClaimFormData {
  const patientName = splitPatientName(scenario.patient.name);
  const address =
    patientAddresses[scenario.patient.name] ?? patientAddresses["Sarah Chen"];
  const diagnoses = getDiagnosisEntries(scenario.diagnoses);
  const serviceLines = getServiceLines(scenario, diagnoses);
  const insuranceType = getInsuranceType(scenario.patient.insurance.payer);
  const claimDataWithoutX12: Omit<ClaimFormData, "x12"> = {
    scenarioId: scenario.id,
    payerName: scenario.patient.insurance.payer,
    planType: scenario.patient.insurance.planType,
    insuranceType,
    insuredId: scenario.patient.insurance.memberId,
    policyGroupNumber: getPolicyGroupNumber(scenario),
    patient: {
      fullName: patientName.fullName,
      firstName: patientName.firstName,
      lastName: patientName.lastName,
      dob: scenario.patient.dob,
      dobDisplay: formatDateDisplay(scenario.patient.dob),
      dobX12: formatDateX12(scenario.patient.dob),
      sex: scenario.patient.sex,
      mrn: scenario.patient.mrn,
      address,
    },
    insured: {
      fullName: patientName.fullName,
      address,
      relationship: "Self",
    },
    encounter: {
      dateOfService: scenario.encounter.dateOfService,
      dateDisplay: formatDateDisplay(scenario.encounter.dateOfService),
      dateX12: formatDateX12(scenario.encounter.dateOfService),
      placeOfServiceCode: getPlaceOfServiceCode(scenario.encounter.placeOfService),
      providerName: scenario.encounter.providerName,
      providerNpi: scenario.encounter.providerNpi,
    },
    diagnoses,
    serviceLines,
    billingProvider: {
      ...billingProvider,
      npi: scenario.encounter.providerNpi,
    },
    totalCharges: scenario.totalCharges,
  };

  return {
    ...claimDataWithoutX12,
    x12: buildX12EdiContent(scenario, claimDataWithoutX12),
  };
}

export function buildCms1500Fields(data: ClaimFormData): AnimatedCmsField[] {
  const selectedInsuranceField =
    data.insuranceType === "medicare" ? "box1-medicare" : "box1-group";

  return [
    { id: selectedInsuranceField, value: "X" },
    { id: "box1a-insured-id", value: data.insuredId },
    { id: "box2-patient-name", value: data.patient.fullName },
    { id: "box3-dob", value: data.patient.dobDisplay },
    { id: "box3-sex", value: data.patient.sex },
    { id: "box4-insured-name", value: data.insured.fullName },
    { id: "box5-address", value: data.patient.address.line1 },
    {
      id: "box5-city-state",
      value: `${data.patient.address.city}, ${data.patient.address.state} ${data.patient.address.zip}`,
    },
    { id: "box5-phone", value: data.patient.address.phone },
    { id: "box6-self", value: "X" },
    { id: "box7-address", value: data.insured.address.line1 },
    {
      id: "box7-city-state",
      value: `${data.insured.address.city}, ${data.insured.address.state} ${data.insured.address.zip}`,
    },
    { id: "box11-group", value: data.policyGroupNumber },
    { id: "box11c-plan", value: `${data.payerName} / ${data.planType}` },
    ...data.diagnoses.map((diagnosis) => ({
      id: `box21-${diagnosis.letter}`,
      value: `${diagnosis.letter}. ${diagnosis.code}`,
    })),
    ...data.serviceLines.flatMap((line) => [
      { id: `box24-${line.lineNumber}-date`, value: data.encounter.dateDisplay },
      { id: `box24-${line.lineNumber}-pos`, value: line.placeOfService },
      { id: `box24-${line.lineNumber}-cpt`, value: line.cpt },
      { id: `box24-${line.lineNumber}-mod`, value: line.modifiers.join(" ") },
      {
        id: `box24-${line.lineNumber}-diag`,
        value: line.diagnosisPointerLetters,
      },
      {
        id: `box24-${line.lineNumber}-charge`,
        value: line.charge.toFixed(2),
      },
      { id: `box24-${line.lineNumber}-units`, value: String(line.units) },
      { id: `box24-${line.lineNumber}-npi`, value: line.renderingProviderNpi },
    ]),
    { id: "box25-tax-id", value: data.billingProvider.taxId },
    { id: "box28-total", value: data.totalCharges.toFixed(2) },
    {
      id: "box33-provider",
      value: `${data.billingProvider.name}\n${data.billingProvider.line1}\n${data.billingProvider.city}, ${data.billingProvider.state} ${data.billingProvider.zip}`,
    },
    { id: "box33-phone", value: data.billingProvider.phone },
    { id: "box33-npi", value: data.billingProvider.npi },
  ].filter((field) => field.value.length > 0);
}
