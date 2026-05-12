import {
  Document,
  Page,
  StyleSheet,
  Text,
  View,
} from "@react-pdf/renderer";
import type { ReactNode } from "react";

import type { ClaimFormData, ServiceLine } from "@/lib/claims/form-data";

interface Cms1500PdfDocumentProps {
  formData: ClaimFormData;
}

interface PdfBoxProps {
  number: string;
  label: string;
  width: string;
  minHeight?: number;
  children?: ReactNode;
}

const styles = StyleSheet.create({
  page: {
    padding: 26,
    backgroundColor: "#ffffff",
    color: "#000000",
    fontSize: 7,
    fontFamily: "Helvetica",
  },
  form: {
    borderLeftWidth: 1,
    borderTopWidth: 1,
    borderColor: "#000000",
  },
  row: {
    flexDirection: "row",
    width: "100%",
  },
  box: {
    borderRightWidth: 1,
    borderBottomWidth: 1,
    borderColor: "#000000",
    padding: 4,
  },
  boxHeader: {
    flexDirection: "row",
    gap: 3,
  },
  boxNumber: {
    fontSize: 6,
    fontWeight: 700,
  },
  boxLabel: {
    fontSize: 5,
    textTransform: "uppercase",
  },
  value: {
    marginTop: 4,
    fontSize: 8,
    fontFamily: "Courier",
    lineHeight: 1.2,
  },
  title: {
    marginBottom: 4,
    textAlign: "center",
    fontSize: 12,
    fontWeight: 700,
  },
  checkboxRow: {
    marginTop: 4,
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 9,
  },
  checkbox: {
    flexDirection: "row",
    gap: 3,
    alignItems: "center",
  },
  checkboxSquare: {
    width: 9,
    height: 9,
    borderWidth: 1,
    borderColor: "#000000",
    textAlign: "center",
    fontSize: 7,
    fontFamily: "Courier",
  },
  serviceHeader: {
    flexDirection: "row",
    borderBottomWidth: 1,
    borderColor: "#000000",
    backgroundColor: "#f1f5f9",
  },
  serviceCell: {
    borderRightWidth: 1,
    borderColor: "#000000",
    padding: 3,
    minHeight: 24,
    fontSize: 6,
  },
  serviceValue: {
    fontFamily: "Courier",
    fontSize: 7,
  },
});

function PdfBox({
  number,
  label,
  width,
  minHeight = 48,
  children,
}: PdfBoxProps) {
  return (
    <View style={[styles.box, { width, minHeight }]}>
      <View style={styles.boxHeader}>
        <Text style={styles.boxNumber}>{number}</Text>
        <Text style={styles.boxLabel}>{label}</Text>
      </View>
      <View style={styles.value}>{children}</View>
    </View>
  );
}

function CheckBox({ label, checked }: { label: string; checked?: boolean }) {
  return (
    <View style={styles.checkbox}>
      <Text style={styles.checkboxSquare}>{checked ? "X" : ""}</Text>
      <Text>{label}</Text>
    </View>
  );
}

function PdfServiceLine({
  line,
  formData,
}: {
  line: ServiceLine;
  formData: ClaimFormData;
}) {
  const cells = [
    { width: "15%", value: formData.encounter.dateDisplay },
    { width: "8%", value: line.placeOfService },
    {
      width: "20%",
      value: `${line.cpt}${line.modifiers.length ? ` ${line.modifiers.join(" ")}` : ""}`,
    },
    { width: "12%", value: line.diagnosisPointerLetters },
    { width: "12%", value: line.charge.toFixed(2) },
    { width: "8%", value: String(line.units) },
    { width: "18%", value: line.renderingProviderNpi },
    { width: "7%", value: "" },
  ];

  return (
    <View style={styles.row}>
      {cells.map((cell, index) => (
        <View key={index} style={[styles.serviceCell, { width: cell.width }]}>
          <Text style={styles.serviceValue}>{cell.value}</Text>
        </View>
      ))}
    </View>
  );
}

export function Cms1500PdfDocument({ formData }: Cms1500PdfDocumentProps) {
  const isMedicare = formData.insuranceType === "medicare";

  return (
    <Document title={`CMS-1500 ${formData.patient.fullName}`}>
      <Page size="LETTER" style={styles.page}>
        <View style={styles.form}>
          <View style={styles.row}>
            <PdfBox
              number="1"
              label="Insurance type"
              width="66.666%"
              minHeight={54}
            >
              <Text style={styles.title}>HEALTH INSURANCE CLAIM FORM</Text>
              <View style={styles.checkboxRow}>
                <CheckBox label="Medicare" checked={isMedicare} />
                <CheckBox label="Medicaid" />
                <CheckBox label="Tricare" />
                <CheckBox label="ChampVA" />
                <CheckBox label="Group Health Plan" checked={!isMedicare} />
                <CheckBox label="Other" />
              </View>
            </PdfBox>
            <PdfBox
              number="1a"
              label="Insured's I.D. Number"
              width="33.334%"
              minHeight={54}
            >
              <Text>{formData.insuredId}</Text>
            </PdfBox>
          </View>

          <View style={styles.row}>
            <PdfBox number="2" label="Patient's Name" width="33.333%">
              <Text>{formData.patient.fullName}</Text>
            </PdfBox>
            <PdfBox number="3" label="Patient Birth Date / Sex" width="25%">
              <Text>
                {formData.patient.dobDisplay}  {formData.patient.sex}
              </Text>
            </PdfBox>
            <PdfBox number="4" label="Insured's Name" width="41.667%">
              <Text>{formData.insured.fullName}</Text>
            </PdfBox>
          </View>

          <View style={styles.row}>
            <PdfBox number="5" label="Patient's Address" width="33.333%">
              <Text>{formData.patient.address.line1}</Text>
              <Text>
                {formData.patient.address.city}, {formData.patient.address.state}{" "}
                {formData.patient.address.zip}
              </Text>
              <Text>{formData.patient.address.phone}</Text>
            </PdfBox>
            <PdfBox
              number="6"
              label="Patient Relationship to Insured"
              width="25%"
            >
              <View style={styles.checkboxRow}>
                <CheckBox label="Self" checked />
                <CheckBox label="Spouse" />
                <CheckBox label="Child" />
                <CheckBox label="Other" />
              </View>
            </PdfBox>
            <PdfBox number="7" label="Insured's Address" width="41.667%">
              <Text>{formData.insured.address.line1}</Text>
              <Text>
                {formData.insured.address.city}, {formData.insured.address.state}{" "}
                {formData.insured.address.zip}
              </Text>
            </PdfBox>
          </View>

          <View style={styles.row}>
            <PdfBox number="11" label="Policy Group Number" width="33.333%">
              <Text>{formData.policyGroupNumber}</Text>
            </PdfBox>
            <PdfBox number="11c" label="Insurance Plan Name" width="66.667%">
              <Text>
                {formData.payerName} / {formData.planType}
              </Text>
            </PdfBox>
          </View>

          <View style={styles.row}>
            <PdfBox number="21" label="Diagnosis Codes" width="100%" minHeight={76}>
              {formData.diagnoses.map((diagnosis) => (
                <Text key={diagnosis.id}>
                  {diagnosis.letter}. {diagnosis.code} - {diagnosis.description}
                </Text>
              ))}
            </PdfBox>
          </View>

          <View style={[styles.box, { padding: 0 }]}>
            <View style={{ padding: 4, borderBottomWidth: 1, borderColor: "#000000" }}>
              <Text style={styles.boxNumber}>24 Service Lines</Text>
            </View>
            <View style={styles.serviceHeader}>
              {[
                ["15%", "24A Date"],
                ["8%", "24B POS"],
                ["20%", "24D CPT/Mod"],
                ["12%", "24E Dx"],
                ["12%", "24F Charges"],
                ["8%", "24G Units"],
                ["18%", "24J NPI"],
                ["7%", ""],
              ].map(([width, label]) => (
                <View key={label} style={[styles.serviceCell, { width }]}>
                  <Text>{label}</Text>
                </View>
              ))}
            </View>
            {formData.serviceLines.map((line) => (
              <PdfServiceLine
                key={line.procedureId}
                line={line}
                formData={formData}
              />
            ))}
          </View>

          <View style={styles.row}>
            <PdfBox number="25" label="Federal Tax I.D." width="25%">
              <Text>{formData.billingProvider.taxId}</Text>
            </PdfBox>
            <PdfBox number="28" label="Total Charge" width="25%">
              <Text>{formData.totalCharges.toFixed(2)}</Text>
            </PdfBox>
            <PdfBox number="33" label="Billing Provider Info" width="50%">
              <Text>{formData.billingProvider.name}</Text>
              <Text>{formData.billingProvider.line1}</Text>
              <Text>
                {formData.billingProvider.city}, {formData.billingProvider.state}{" "}
                {formData.billingProvider.zip}
              </Text>
              <Text>{formData.billingProvider.phone}</Text>
              <Text>NPI {formData.billingProvider.npi}</Text>
            </PdfBox>
          </View>
        </View>
      </Page>
    </Document>
  );
}
