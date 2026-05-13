# Dr. Kim Training Demo Source Of Truth

Date: 2026-05-12

The active Next.js demo lives inside this repository at:

```text
revcyclemgmt-demo/
```

Canonical NAS path:

```text
/mnt/z/BUSINESSES/RevCycleMGMT/06_PORTFOLIO_PROJECTS/revcyclemgmt-app-shell/revcyclemgmt-demo
```

Active branch:

```text
ticket-1-next-demo-scaffold
```

Demo code baseline:

```text
653a7ea fix: respect reduced motion and polish spacing
```

Tickets 1-10 are implemented. The demo routes are:

```text
/
/demo
/demo/[scenarioId]/encounter
/demo/[scenarioId]/coding
/demo/[scenarioId]/claim
/demo/[scenarioId]/forms
/demo/[scenarioId]/submit
/demo/[scenarioId]/complete
```

Latest build verification: `npm run build` passed from a temp copy. X12 SE counts were verified as Sarah `23` and James `29`; copy-ready EDI strips teaching comments; CMS-1500 PDFs generated as valid one-page PDFs.

Do not continue development from `/mnt/agent_8/RevCycleMGMT/revcyclemgmt-demo` or another scratch copy. Those paths were temporary staging only.

Deployment is not Vercel by default. Run the app locally or from NAS until a deployment target is explicitly chosen.
