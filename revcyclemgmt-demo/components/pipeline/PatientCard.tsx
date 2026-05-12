import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import type { Scenario } from "@/lib/scenarios";

interface PatientCardProps {
  scenario: Scenario;
}

function formatDate(isoDate: string) {
  const [year, month, day] = isoDate.split("-");
  return `${month}/${day}/${year}`;
}

export function PatientCard({ scenario }: PatientCardProps) {
  const { patient, encounter } = scenario;

  const rows = [
    {
      label: "DOB / Age",
      value: `${formatDate(patient.dob)} / ${patient.age}`,
    },
    {
      label: "Sex / MRN",
      value: `${patient.sex} / ${patient.mrn}`,
    },
    {
      label: "Insurance / Member ID",
      value: `${patient.insurance.payer} / ${patient.insurance.memberId}`,
    },
    {
      label: "Date of Service",
      value: formatDate(encounter.dateOfService),
    },
  ];

  return (
    <Card className="rounded-xl border-slate-200 bg-white p-6 shadow-sm">
      <CardHeader className="p-0">
        <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">
          Patient
        </p>
        <CardTitle className="mt-2 text-lg font-semibold tracking-[0] text-slate-900">
          {patient.name}
        </CardTitle>
      </CardHeader>

      <CardContent className="p-0 pt-6">
        <dl className="space-y-4">
          {rows.map((row) => (
            <div key={row.label}>
              <dt className="text-xs font-medium uppercase tracking-wider text-slate-500">
                {row.label}
              </dt>
              <dd className="mt-1 text-sm font-medium text-slate-900">
                {row.value}
              </dd>
            </div>
          ))}
        </dl>

        <div className="mt-6 border-t border-slate-200 pt-5 text-sm leading-6 text-slate-600">
          <span className="font-semibold text-slate-900">Provider:</span>{" "}
          {encounter.providerName}, NPI {encounter.providerNpi}
        </div>
      </CardContent>
    </Card>
  );
}
