import { scenario01PreventiveHtn } from "./scenario-01-preventive-htn";
import { scenario02Laceration } from "./scenario-02-laceration";
import type { Scenario } from "./types";

export type {
  ClinicalNoteSection,
  Diagnosis,
  HighlightedPhrase,
  Patient,
  Procedure,
  RemittanceLine,
  Scenario,
  TeachingNote,
} from "./types";

export const scenarios: Scenario[] = [
  scenario01PreventiveHtn,
  scenario02Laceration,
];

export function getScenarioById(id: string): Scenario | undefined {
  return scenarios.find((scenario) => scenario.id === id);
}

export { scenario01PreventiveHtn, scenario02Laceration };
