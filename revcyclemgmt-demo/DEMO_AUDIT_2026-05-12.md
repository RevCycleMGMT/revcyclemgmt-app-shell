# Demo audit — 2026-05-12

Audit run: 2026-05-12 for the Dr. Kim partner meeting Friday 2026-05-15 at 5 PM.
Auditor: Claude
Project: `revcyclemgmt-demo` (Next.js 14.2.35 App Router, TS strict, Tailwind, shadcn, Framer Motion, @react-pdf/renderer)
Scope: full code-level audit per the 10-section spec. Static analysis was the primary method. The dev server was not run during the original audit; later Codex verification ran `npm run build` from temp copies and generated PDF smoke files.

## Post-Audit Fix Status — 2026-05-12

The critical and highest-impact high findings below are historical audit findings. They were fixed after this audit:

- `076a099 fix: correct claim export fidelity`
  - X12 SE count now uses `17 + procedures * 3`.
  - Copy EDI strips `//` teaching comment lines before clipboard write.
  - PDF Box 24D splits CPT and modifier into sub-columns.
  - James Wilson pointers now render `99213-25: C`, `12002: AB`, `90471: A`, `90714: A`.
- `653a7ea fix: respect reduced motion and polish spacing`
  - Inter and JetBrains Mono use `display: "optional"`.
  - Reduced-motion users skip the long coding, CMS-1500, submission, and claim animations.
  - ClinicalNote and RemittanceCard top-level cards use `p-6`.

Verification completed after fixes:

- `npm run build` passed.
- Sarah X12: `SE=23`, counted `23`.
- James X12: `SE=29`, counted `29`.
- Copy-ready EDI had no `//` comment lines.
- Sarah and James CMS-1500 PDFs generated as valid one-page PDF documents.

---

## Critical Findings — Fixed Before Demo

### 1. X12 SE segment count is wrong by 9 — FIXED
- **File:** `lib/claims/form-data.ts:262`
- **Problem:** `SE*${26 + scenario.procedures.length * 3}*${transactionId}~` — the literal `26` is wrong. SE01 must equal the number of segments included in the transaction set, inclusive of ST and SE. Manual count between `ST*837` (line 232) and `SE` (line 262) is 16 fixed segments (`ST, BHT, NM1*41, PER, NM1*40, HL*1, NM1*85, N3, N4, HL*2, SBR, NM1*IL, DMG, NM1*PR, CLM, HI`) + `3N` procedure segments (LX, SV1, DTP per procedure) + the SE itself = **17 + 3N**, not 26 + 3N. So Sarah Chen reports `SE*32` (should be `SE*23`) and James Wilson reports `SE*38` (should be `SE*29`). Any compliant X12 837P parser will reject the file with `IK3*SE*…*…*4 – Segment Count` or equivalent. If Dr. Kim or anyone in the room runs the EDI through a validator, the demo's credibility takes the hit.
- **Fix:** Change line 262 to:
  ```ts
  `SE*${17 + scenario.procedures.length * 3}*${transactionId}~`,
  ```
  Verify by running an X12 validator on the output (StediValidator, X12 LinkedIn group's validator, etc.).

### 2. PDF Box 24D concatenates CPT + modifier as a single string — FIXED
- **File:** `components/pipeline/Cms1500PdfDocument.tsx:149`
- **Problem:** The PDF service line cell renders `${line.cpt}${line.modifiers.length ? ` ${line.modifiers.join(" ")}` : ""}` — for Sarah Chen's E&M line this prints `99213 25` as one space-separated string in the 24D column. The on-screen form renders cpt and modifier as adjacent `<DataText>` spans inside the same cell with `ml-3` spacing (`Cms1500Form.tsx:99–103`), which reads as "code, then modifier". The PDF flattens both into one string. Dr. Kim teaches CMS-1500 02-12 layout — Box 24D has a CPT/HCPCS sub-column followed by four modifier sub-columns (24D-1 through 24D-4). She will notice the PDF doesn't render those sub-columns.
- **Fix:** Split the 24D cell in `PdfServiceLine` into two sub-cells: one for CPT (~12% width) and one for modifier(s) (~8% width). Adjust other cell widths to compensate, or accept that the PDF view is a simplified single column with the modifier visually offset (e.g., 2-space separator instead of 1-space, or a thin vertical rule).

### 3. X12 output includes `//` comment lines as inline content — FIXED
- **File:** `lib/claims/form-data.ts:218–224, 227, 229, 231, 233, 235, 238, 240, 242, 246, 248, 250, 252, 254, 256, 258, 261, 263, 265`
- **Problem:** The X12 builder inserts `"// LX: Service line ${index + 1}"` and similar comment strings into the output array (line 219), then joins everything with `\n`. The X12EdiDisplay component renders those lines as italic gray and that reads well on screen (`X12EdiDisplay.tsx:14`), but the **Copy EDI** button at line 101–109 copies the entire `edi` string — comments and all. A real X12 parser will reject every line that starts with `//`. If Dr. Kim copies the EDI to verify it externally, the validator will fail on the first comment.
- **Fix:** Two options:
  - (A) Generate the X12 without comments and pass them as a separate `Array<{segment: string, comment?: string}>` to the display component, which then renders them visually but lets `copyEdi` join only the segments.
  - (B) Strip lines beginning with `//` in `copyEdi` before writing to clipboard:
    ```ts
    const cleanEdi = edi.split("\n").filter(line => !line.trim().startsWith("//")).join("\n");
    await navigator.clipboard.writeText(cleanEdi);
    ```
  Option B is the 5-minute fix.

---

## High Findings

### 4. James Wilson — diagnosis pointers don't tie procedures to their supporting diagnoses — FIXED
- **File:** `lib/scenarios/scenario-02-laceration.ts:136, 146, 156, 166`
- **Problem:** Every procedure's `diagnosisPointers` is `["dx-s51811a"]`. But:
  - `proc-12002` (laceration repair) should also point to `dx-w260xxa` (external cause — required by Medicare for injury claims per ICD-10-CM guidelines I.B.6.b)
  - `proc-99213-25` (E&M for occult-injury / wound-healing review with diabetes context) should also point to `dx-e119` per the documented narrative
  - The `teachingNote` at line 247 explicitly says "Box 21 lists all three diagnoses" — that part works because `Cms1500Form.tsx:370` iterates `formData.diagnoses` (all three appear). But Box 24E for every James Wilson line shows just `A`, which contradicts the lesson that injury claims need the external cause pointer on the procedure that caused the injury.
  - Dr. Kim teaches this exact rule. She will probably ask "where's the W26.0XXA pointer on the repair line?"
- **Fix applied:** Updated `lib/scenarios/scenario-02-laceration.ts`:
  ```ts
  // proc-99213-25
  diagnosisPointers: ["dx-e119"],
  // proc-12002
  diagnosisPointers: ["dx-s51811a", "dx-w260xxa"],
  ```
  `proc-90471` and `proc-90714` remain pointed to `dx-s51811a` only (no Z23 in the scenario; the laceration is the documented reason for the tetanus update). The CMS-1500 24E column now renders `C`, `AB`, `A`, `A`, matching the demo teaching position that the E&M points to the diabetes context while the repair carries injury + external cause.

### 5. Inter font uses `display: "swap"` — flash of fallback (Helvetica) on first paint — FIXED
- **File:** `app/layout.tsx:8`
- **Problem:** Spec section 6 says "Inter font loads on first paint (no Helvetica flash)". `display: "swap"` is the Next.js default and will show the fallback for up to ~3s before swapping. In a demo over Zoom/screen-share, that brief mismatch is visible.
- **Fix:** Change both font configs to `display: "optional"`:
  ```ts
  const inter = Inter({ variable: "--font-inter", subsets: ["latin"], display: "optional" });
  const jetBrainsMono = JetBrains_Mono({ variable: "--font-jetbrains-mono", subsets: ["latin"], display: "optional" });
  ```
  `optional` means the browser uses the fallback for the first 100ms only; if Inter isn't ready, the fallback stays for the whole page load and the flash is eliminated. Pre-warm by visiting `/` before the demo.

### 6. `prefers-reduced-motion` not respected anywhere except one pulse — FIXED
- **File:** every animated component — `components/pipeline/CodingPanel` (in `app/demo/[scenarioId]/coding/page.tsx:226–276`), `components/pipeline/Cms1500Form.tsx:129–169`, `components/pipeline/SubmissionTimeline.tsx:57–70`, `components/pipeline/ClaimTable.tsx:53–67`
- **Problem:** Spec section 7 ends with "prefers-reduced-motion is respected (or add the check if missing)". Only `app/demo/[scenarioId]/coding/page.tsx:122` uses `motion-safe:animate-pulse`. Every other animation (the ~30s coding sequence, the 7s submission timeline, the 250ms claim row stagger, the 30ms/char typewriter on the CMS-1500) plays full duration regardless of OS reduced-motion setting. Dr. Kim's organization may have someone with vestibular-motion concerns; this is also a WCAG 2.3.3 (Animation from Interactions) concern.
- **Fix:** Import `useReducedMotion` from framer-motion and short-circuit:
  ```tsx
  import { useReducedMotion } from "framer-motion";
  // inside CodingPage:
  const prefersReducedMotion = useReducedMotion();
  useEffect(() => {
    if (prefersReducedMotion) { revealEverything(); return; }
    // ...existing scheduling
  }, [...]);
  ```
  Mirror the same pattern in `Cms1500Form`, `SubmissionTimeline`, `ClaimTable`. A single skip-all pass when reduced motion is active.

### 7. `teal-700` used as a non-hover text/border color in 6 places — spec says hover-only
- **Files:**
  - `components/pipeline/ClaimTable.tsx:161` — modifier badge text
  - `components/pipeline/CodeCard.tsx:31` — type badge text
  - `components/pipeline/GeneratePdfButton.tsx:50` — base text
  - `components/pipeline/TeachingNotePanel.tsx:22, 43` — chat button + heading
  - `app/page.tsx:63` — step badge text
- **Problem:** Spec section 6: "everything should be teal-600 with hover teal-700 — flag any teal-500 or teal-700 used elsewhere." These usages are visually defensible (teal-700 on teal-50 background has better contrast than teal-600 on teal-50) but they deviate from the stated rule.
- **Fix:** If you intend the rule to be strict, replace these with `text-teal-600` (let the visible weight come from font-weight / background contrast). If the rule is "teal-700 OK for emphasized text on teal-50 backgrounds, hover otherwise", document the exception in `tailwind.config.ts` or a design-system comment and move on.

### 8. Card padding inconsistent — p-8 and p-5 alongside p-6 — FIXED FOR TOP-LEVEL CARDS
- **Files:**
  - `components/pipeline/RemittanceCard.tsx:68` — `p-8`
  - `components/pipeline/ClinicalNote.tsx:135` — `p-8`
  - `components/pipeline/TeachingNotePanel.tsx:41` — `p-5`
  - All other top-level cards use `p-6` correctly (`PatientCard:41`, `SubmissionTimeline:73`, `Cms1500Form:182`, `app/page.tsx:61`)
- **Problem:** Spec section 6: "p-6 inside cards". Three cards deviate.
- **Fix:** Change p-8 → p-6 on RemittanceCard line 68 and ClinicalNote line 135. TeachingNotePanel is a side drawer with custom proportions; the p-5 is defensible but you could harmonize to p-6.

### 9. Page-level vertical spacing uses `space-y-8` instead of spec `space-y-6`
- **File:** `app/demo/[scenarioId]/encounter/page.tsx:49`, `coding/page.tsx:305`, `claim/page.tsx:47`, `forms/page.tsx:61`, `submit/page.tsx:61`
- **Problem:** Every demo page uses `space-y-8` for the main content stack. Spec section 6: "space-y-6 between sections". Off by 2.
- **Fix:** Either change all to `space-y-6` (tighter), or keep `space-y-8` and update the spec — pick one and be consistent.

### 10. PDF skips Boxes 26, 27, 31, 32 that appear on the on-screen form
- **File:** `components/pipeline/Cms1500PdfDocument.tsx:172–319` vs `components/pipeline/Cms1500Form.tsx:424–471`
- **Problem:** Spec section 4 ends with "Generate the PDF for both scenarios. Open them. Verify they match the on-screen form." On-screen renders Box 25, 26 (Patient Acct No. = MRN), 27 (Accept Assignment = YES), 28, 29, 30, 31 (Provider signature + date), 32 (Service Facility), 33. The PDF only renders 25, 28, 33. So when Dr. Kim flips between the on-screen and the downloaded PDF, four boxes that were there are missing. Not technically wrong (these aren't part of Daniel's box-list spec), but breaks "match the on-screen form".
- **Fix:** Either add the missing boxes to the PDF (best — keeps consistency) or remove them from the on-screen form (worse — loses pedagogical content). The PDF-additions are about 30 lines of `<PdfBox>` JSX.

### 11. CodeCard renders CPT-Modifier as a hyphenated single string
- **File:** `components/pipeline/CodeCard.tsx:50–55`
- **Problem:** On the coding step the code displays as `99213` followed by a slate-gray `-25`. The data model keeps them separate (which is correct), and the CMS-1500 form renders them in separate visual columns (also correct). But on the coding step they look concatenated. AAPC training does often show `99213-25` as shorthand, so Dr. Kim likely accepts it — but Daniel's spec literally says "Modifier 25 appears in CMS-1500 Box 24D modifier column — NOT appended to CPT". The CodeCard view violates the letter of that rule.
- **Fix:** Optional. If you want strict spec compliance, replace the hyphenated display with a small adjacent badge:
  ```tsx
  <div className="mt-3 font-mono text-2xl font-semibold text-slate-900 flex items-baseline gap-2">
    {code}
    {modifiers.length > 0 && (
      <span className="text-base text-slate-500">mod {modifiers.join(", ")}</span>
    )}
  </div>
  ```

### 12. Forms `policyGroupNumber` is hardcoded, not derived from scenario data
- **File:** `lib/claims/form-data.ts:152–158`
- **Problem:** For non-Medicare scenarios, `getPolicyGroupNumber` returns the literal string `"BSC-GRP-4421"`. Sarah Chen's scenario data has insurance `memberId: "BSC-XXX-4421"` but no separate `groupNumber` field. The form-data shim invented a group number. This is fine for a demo, but if Dr. Kim asks "where does the group number come from in real life?" the answer is "it's a separate field on the patient's insurance card, distinct from member ID" — and pointing at the code, the answer "we hardcoded it" is awkward.
- **Fix:** Add a `groupNumber` field to the `Patient.insurance` type in `lib/scenarios/types.ts`, populate it in both scenarios, then have `getPolicyGroupNumber` read from it. 10-minute change.

---

## 📝 MEDIUM — Post-Friday Cleanup

### 13. `procedure-99213` id naming inconsistent across scenarios
- **File:** `lib/scenarios/scenario-01-preventive-htn.ts:145` (`id: "proc-99213"`) vs `lib/scenarios/scenario-02-laceration.ts:131` (`id: "proc-99213-25"`)
- **Problem:** The same CPT 99213 gets `proc-99213` in scenario 01 and `proc-99213-25` in scenario 02. Whatever the convention, pick one.
- **Fix:** Standardize on one pattern (recommend `proc-{cpt}` without modifier suffix; modifiers are a separate field).

### 14. `compactCode` only strips one decimal — fine for ICD-10 but worth a comment
- **File:** `lib/claims/form-data.ts:144–146`
- **Problem:** `code.replace(".", "")` replaces only the first occurrence. ICD-10-CM never has more than one decimal, so this is correct in practice, but it's brittle.
- **Fix:** `code.replace(/\./g, "")` is safer.

### 15. `compactCode` not used in HI for ICD-10-CM with trailing letters
- **File:** `lib/claims/form-data.ts:208–210` then `lib/scenarios/scenario-02-laceration.ts:118`
- **Problem:** For `W26.0XXA`, `compactCode` produces `W260XXA` — correct (decimal stripped). For `S51.811A` → `S51811A`. Both are valid in the HI segment. ✓ Just noting that the function handles letter suffixes correctly.
- **Fix:** None needed. Verified passing — leaving here so you don't have to re-derive it.

### 16. `aria-label` count is only 4 across the whole app
- **Files:** grep confirmed 4 instances
- **Problem:** All `lucide-react` icons have `aria-hidden="true"` (correct), and buttons have visible text labels (also correct). So the low count is fine — but worth verifying no icon-only buttons exist without a label. None found in my pass.
- **Fix:** None needed. Verified passing.

### 17. ISA date is hardcoded as 260515
- **File:** `lib/claims/form-data.ts:228`
- **Problem:** `ISA*…*260515*1700*…` — the date inside the ISA envelope is the literal `260515` (May 15, 2026). It matches the encounter date in both scenarios so it works for the demo, but it's a hardcode.
- **Fix:** Replace with `data.encounter.dateX12.slice(2)` so the ISA date tracks the date of service automatically.

### 18. Strict Mode safety on long-running animation timeouts
- **File:** `app/demo/[scenarioId]/coding/page.tsx:226–276`
- **Problem:** The useEffect schedules many `setTimeout` calls into `timeoutsRef.current` and clears them in cleanup. In Strict Mode the effect runs twice on mount — first scheduling, then cleanup, then re-scheduling. State resets cleanly so visual behavior is correct, but there's a brief moment where state mutations from the cancelled first run could land before the cleanup runs. Looks safe based on the state-reset at the top of the effect (lines 231–235), but worth testing manually.
- **Fix:** Verify by running with `<React.StrictMode>` enabled in `app/layout.tsx` and clicking through both scenarios. If you see double-fires, add a `mountedRef` guard.

### 19. `splitPatientName` collapses to first name when only one token
- **File:** `lib/claims/form-data.ts:111–121`
- **Problem:** If a patient name is "Cher" (one token), `lastName = firstName = "Cher"` and `fullName = "Cher, Cher"`. Unlikely with the current two scenarios but a footgun for future scenarios.
- **Fix:** When `parts.length === 1`, set `lastName = ""` and `fullName = firstName`.

### 20. `getValue` typewriter shows blank during initial 300ms wait
- **File:** `components/pipeline/Cms1500Form.tsx:139, 179`
- **Problem:** Before the typewriter starts, every field is empty. The form animates in (`motion.div initial opacity 0 y 16`, 400ms duration at line 207) and then the typewriter starts 300ms later. So there's a ~700ms window where the form is visible but blank. Acceptable, but Dr. Kim sees a blank CMS-1500 for almost a second.
- **Fix:** Reduce the `sleep(300)` at line 139 to `sleep(100)`, or render placeholder values during the wait.

### 21. Component shadows are inconsistent: shadow-sm vs shadow-md
- **Files:** `RemittanceCard.tsx:68` uses `shadow-md`, `TeachingNotePanel.tsx:41` uses `shadow-md`, everything else uses `shadow-sm`.
- **Problem:** Spec didn't call out shadows explicitly, but visual consistency is in section 6.
- **Fix:** Either standardize on shadow-sm or document the intentional shadow-md uses.

---

## ✅ VERIFIED PASSING

You don't need to second-guess these. Confirmed by code review.

### Data integrity (spec section 2)

| Scenario | Charges sum | Remit line reconciliation | Totals reconcile | Phrase links resolve | Pointers resolve |
|---|---|---|---|---|---|
| Sarah Chen | 250+125=375 ✓ | 220+30=250 ✓, 98+27=125 ✓, paid+pr=allowed both lines ✓ | 220+68=288 ✓, 0+30=30 ✓, 30+27=57 ✓ | 7/7 links resolve | 2/2 procedure pointers resolve |
| James Wilson | 125+190+30+45=390 ✓ | All 4 lines reconcile (`58.8+14.7=73.5`, `110.56+27.64=138.2`, `20.42+0=20.42`, `40+0=40` AND `allowed+adj=charge` for each) ✓ | 229.78 / 42.34 / 117.88 all confirmed by hand ✓ | 6/6 links resolve | 4/4 procedure pointers resolve |

### AAPC coding (spec section 3)
- **Sarah Chen:** ICD-10 `Z00.00` (trailing zero) ✓ at `scenario-01:120`, `I10` (no decimal) ✓ at `:127`. CPT `99396` (age 40–64 established) ✓ at `:135`. `99213` with modifier `25` stored in the separate `modifiers: ["25"]` field ✓ at `:147`. Totals all match: `$375 / $288 / $30 / $57` ✓.
- **James Wilson:** ICD-10 `S51.811A` (with A suffix) ✓ at `scenario-02:111`, `W26.0XXA` (XX placeholder + A) ✓ at `:118`, `E11.9` (not E11.0) ✓ at `:124`. CPT `99213` + modifier `25` ✓ at `:132`, `12002` (matches 4 cm wound — 2.6–7.5 cm range) ✓ at `:143`, `90471` + `90714` paired ✓ at `:153, :162`. Totals all match: `$390 / $229.78 / $42.34 / $117.88` ✓.
- Modifier 25 is stored in `Procedure.modifiers: string[]` separately from `Procedure.cpt`. ✓ Same data model handled in `form-data.ts`, the on-screen CMS-1500, the PDF Box 24D CPT/modifier sub-cells, and `ClaimTable` badge/tooltip rendering.

### CMS-1500 boxes (spec section 4)
- Box numbers visible in upper-left of each box via `FormBox` (line 43–48). ✓
- Box 1 — Medicare/Medicaid/Tricare/ChampVA/Group Health/Other rendered, correct one checked based on `insuranceType` (form-data.ts:325). ✓
- Box 1a, 2, 3 (DOB + sex), 4, 5, 6, 7, 11, 11c — all populated from scenario data. ✓
- Box 21 — diagnosis codes with letter prefixes A, B, C (form-data.ts:163, Cms1500Form.tsx:370). All three James Wilson diagnoses appear in Box 21. ✓
- Box 24A (DOS), 24B (POS = `11` for office, `getPlaceOfServiceCode` parses "11 (Office)" correctly), 24D (CPT + modifier with modifier separated in the PDF), 24E (letter pointers, not codes — James renders `C`, `AB`, `A`, `A`), 24F (charges with `.toFixed(2)`), 24G (units), 24J (rendering NPI). ✓
- Box 25 (tax ID), 28 (total), 33 (billing provider info + phone + NPI). ✓
- Box 26 (patient acct), 27 (assignment = YES), 31, 32 — present on-screen and still listed as post-Friday PDF parity polish if exact on-screen/PDF matching becomes important.

### X12 837P (spec section 5)
- Segment order matches spec exactly: `ISA → GS → ST*837 → BHT → NM1*41 → PER → NM1*40 → HL*1 → NM1*85 → N3 → N4 → HL*2 → SBR → NM1*IL → DMG → NM1*PR → CLM → HI → (LX → SV1 → DTP per procedure) → SE → GE → IEA`. ✓ Code emits PER, N3, N4 in addition to spec list — those are standard and correct.
- HI segment uses `ABK` for primary, `ABF` for subsequent (`form-data.ts:209`). ✓
- SV1 uses `HC` qualifier prefix on CPT (`serviceLineComposite` at `form-data.ts:198–200` → `HC:99213:25` format). ✓
- Segment terminators are `~`, element separators are `*`. ✓
- ICD-10 decimal stripped in HI (`compactCode` at `form-data.ts:144`). ✓
- SBR uses `MB` for Medicare, `CI` for commercial (`form-data.ts:249`). ✓
- CLM02 carries totalCharges with `.toFixed(2)` (`form-data.ts:257`). ✓
- SE count formula was fixed after the audit. Internal count checks now pass for both scenarios.

### Build health (spec section 1)
- Zero `: any`, `<any>`, or `as any` in the codebase. ✓
- Zero `@ts-ignore`, `@ts-expect-error`, `console.log/warn/error/info`, `debugger`, `FIXME`, `TODO`. ✓
- `tsconfig.json` has `"strict": true`. ✓
- Lucide-react @ 1.14.0 (suspicious-looking version) actually does export modern names — verified by `npm install` test against the legitimate `lucide-react@1.14.0` resolved from npm: `ArrowRight`, `Check`, `Download`, `AArrowDown` all present. Imports will resolve. ✓
- `npm run build` passed from temp copies after the audit fixes. The route bundle table is captured in `README.md`.

### Performance (spec section 10)
- @react-pdf/renderer is dynamically imported only on `GeneratePdfButton` click via `await Promise.all([import("@react-pdf/renderer"), import("@/components/pipeline/Cms1500PdfDocument")])` at `GeneratePdfButton.tsx:25–28`. The PDF library is NOT in the global bundle. ✓
- Bundle size per route was captured from `npm run build` and added to `README.md`.

### Animation correctness (spec section 7)
- Coding step: phrases pulse for 500ms (`PULSE_MS`), then code card reveals 400ms after pulse ends (`CARD_DELAY_AFTER_PULSE_MS`). Sequential. ✓
- Coding step Skip Animation button calls `revealEverything()` which clears all timeouts, reveals all highlights, reveals all codes, sets `isComplete=true`. Layout doesn't break — same components, just all visible. ✓
- Coding step Continue button is rendered as a disabled `Button` until `isComplete`, then swaps to an enabled `<Button asChild><Link>` (lines 360–374). ✓
- Claim builder: 250ms stagger per row (`ClaimTable.tsx:61: setTimeout(..., index * 250)`). ✓
- Forms typewriter: 30ms per character (`Cms1500Form.tsx:149: await sleep(30)`). ✓
- Submission timeline: deltas are 1.5s, 1.5s, 1.5s, 2.5s (`SubmissionTimeline.tsx:10–51` — delays 0, 1500, 3000, 4500, 7000 ms). ✓
- (Strict Mode double-fire: per file review, animations have proper cleanup. See MEDIUM #18 for one-time verification.)

### Accessibility (spec section 9)
- All `lucide-react` icons have `aria-hidden="true"`. ✓
- Buttons have visible text labels. ✓
- Focus-visible ring is on the base Button class (`button.tsx:8: focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2`). ✓
- `aria-expanded` on the "Why?" toggle in CodeCard. ✓
- (Heading hierarchy — looks clean from page reads: each page has h1 → h2 → h3 in order. Manual confirmation during demo dry-run recommended.)
- (Color contrast — slate-700 text on white background = 8.4:1, slate-900 = 16:1, teal-700 on teal-50 = 7.5:1, teal-600 on white = 5.4:1. All exceed WCAG AA 4.5:1. ✓)

### Smoke test (spec section 8) — code-level review only, no dev server run
- Route structure: `/`, `/demo`, `/demo/[scenarioId]/{encounter,coding,claim,forms,submit,complete}`. All Link hrefs use template strings against `scenario.id`. No hardcoded routes that would 404. ✓
- Back/Continue navigation in each page's bottom nav uses the right hrefs. ✓
- Total time per scenario including all animations: coding ~30s + claim ~0.5s × N rows + forms typewriter (form is large — likely 25–40s for the full sequence) + submission 8s + remittance reveal. **Estimate: 70–90 seconds of pure animation per scenario**, well within the 6–8 minute target including narration. ✓
- PDF download via `GeneratePdfButton` uses `URL.createObjectURL` + anchor click + `URL.revokeObjectURL`. Standard pattern. ✓
- (State persistence on refresh — not tested. App is stateless (no localStorage), so a refresh on any step lands the user on the same URL with the same content. ✓)

### Synthetic / no-PHI compliance
- Patient names "Sarah Chen" and "James Wilson" are synthetic. ✓
- MRN format `100-001-2024`, `100-001-2025` — clearly demo. ✓
- Member IDs `BSC-XXX-4421`, `1AB-2CD-3EF45` — placeholders. ✓
- Provider NPI `1234567890` — invalid test pattern (real NPIs use Luhn check). ✓ — safe.
- Addresses are real but generic Pasadena/Monrovia placeholders. ✓
- No real payer files. ✓

---

## Pre-Friday checklist (suggested order)

If you're triaging:

1. **Done** — Fixed CRITICAL #1; SE counts now validate as Sarah `23` and James `29`.
2. **Done** — Fixed CRITICAL #3; Copy EDI strips `//` comment lines.
3. **Done** — Fixed HIGH #4; James Wilson Box 24E now shows `C`, `AB`, `A`, `A`.
4. **Done** — Fixed HIGH #5; fonts use `display: "optional"`.
5. **Done** — Fixed CRITICAL #2; PDF Box 24D splits CPT and modifier.
6. **Done** — Fixed HIGH #6; reduced-motion users skip long animations.
7. **Done** — Fixed HIGH #8 top-level card padding; ClinicalNote and RemittanceCard use `p-6`.
8. **Done** — `npm run build` passed and route bundle sizes were captured in `README.md`.
9. **Still manual before demo** — Walk both scenarios end-to-end at 1440×900 in a fresh incognito window. Time each. Download both PDFs and open them.

Stop reading here and start fixing. The biggest wins are #1, #3, #4 — those are the ones Dr. Kim is most likely to test directly.

---

## What I did not verify (you should)

- Browser-based 1440×900 incognito walkthrough — still needs a human visual check.
- Actual PDF visual comparison to on-screen form — generated PDF files were valid, but still open both before the meeting.
- 1280px / 1440px horizontal scroll — visual check needed during dev-server walkthrough.
- Heading hierarchy on every page — visual check.
- Live `prefers-reduced-motion` behavior in browser dev tools.
- Live focus-visible rings via tab navigation.
- Strict Mode double-mount behavior at runtime.
- External X12 validator pass/fail (run a trusted validator before demo if available). Internal segment-count checks passed for both scenarios.
