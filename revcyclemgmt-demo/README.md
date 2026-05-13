# RevCycleMGMT Training Demo

Static Next.js RCM training demo for the Dr. Kim / AAPC chapter review on Friday 2026-05-15.

Canonical path:

```text
/mnt/z/BUSINESSES/RevCycleMGMT/06_PORTFOLIO_PROJECTS/revcyclemgmt-app-shell/revcyclemgmt-demo
```

## Stack

- Next.js 14 App Router
- TypeScript
- Tailwind CSS
- shadcn/ui
- Framer Motion
- `lucide-react`
- `@react-pdf/renderer`
- Inter and JetBrains Mono via `next/font/google`

## Commands

```bash
npm run dev
npm run build
npm run lint
```

Development URL:

```text
http://localhost:3000
```

## Current Screen

The app renders the full synthetic revenue-cycle training flow:

| Route | Purpose |
|---|---|
| `/` | Landing page |
| `/demo` | Scenario selector |
| `/demo/[scenarioId]/encounter` | EHR-style encounter review |
| `/demo/[scenarioId]/coding` | Animated coding sequence with skip control |
| `/demo/[scenarioId]/claim` | Claim-line table with diagnosis pointers |
| `/demo/[scenarioId]/forms` | CMS-1500 form and X12 837P display |
| `/demo/[scenarioId]/submit` | Simulated clearinghouse timeline and 835 remit |
| `/demo/[scenarioId]/complete` | Summary close screen |

Current scenarios:

- Sarah Chen: annual physical plus hypertension follow-up, preventive + E&M modifier 25.
- James Wilson: laceration repair plus brief E&M, external cause coding, tetanus update, Medicare remittance.

## Current Verification

Demo code baseline:

```text
653a7ea fix: respect reduced motion and polish spacing
```

`npm run build` passed from a temp copy. Bundle snapshot:

```text
/                                    6.97 kB   157 kB
/demo                                2.4 kB    152 kB
/demo/[scenarioId]/claim             4.1 kB    173 kB
/demo/[scenarioId]/coding            5 kB      157 kB
/demo/[scenarioId]/complete          5.88 kB   155 kB
/demo/[scenarioId]/encounter         3.76 kB   156 kB
/demo/[scenarioId]/forms             8.66 kB   168 kB
/demo/[scenarioId]/submit            4.25 kB   177 kB
Shared first-load JS                 87.5 kB
```

Parser/PDF checks completed:

- Sarah X12 SE count: `23`.
- James X12 SE count: `29`.
- Copy EDI strips pedagogical `//` comments before clipboard write.
- CMS-1500 PDF Box 24D separates CPT and modifier sub-columns.
- Sarah and James CMS-1500 PDFs generated as valid one-page PDF documents.
- Reduced-motion users skip the long coding, forms, submission, and claim animations.

Remaining manual pre-demo QA: run a fresh incognito walkthrough at 1440x900, download/open both PDFs, time both scenarios, and pre-warm `/` plus `/demo`.

## Deployment

No Vercel deployment is configured as the default. Use NAS/local execution unless a later ticket explicitly chooses a deployment target.
