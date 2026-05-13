<!-- BEGIN:nextjs-agent-rules -->
# This is NOT the Next.js you know

This version has breaking changes — APIs, conventions, and file structure may all differ from your training data. Read the relevant guide in `node_modules/next/dist/docs/` before writing any code. Heed deprecation notices.
<!-- END:nextjs-agent-rules -->

# RevCycleMGMT Training Demo Agent Notes

Canonical NAS path:

```text
/mnt/z/BUSINESSES/RevCycleMGMT/06_PORTFOLIO_PROJECTS/revcyclemgmt-app-shell/revcyclemgmt-demo
```

Remote branch:

```text
git@github.com:RevCycleMGMT/revcyclemgmt-app-shell.git
ticket-1-next-demo-scaffold
653a7ea fix: respect reduced motion and polish spacing
```

Do not use `/mnt/agent_8` as the source of truth. Use `/tmp` only for dependency installs, build copies, and browser/PDF smoke tests.

Current demo state:

- Tickets 1-10 are implemented.
- Static data only: no backend, no database, no auth, no real API calls.
- Routes: `/`, `/demo`, and `/demo/[scenarioId]/{encounter,coding,claim,forms,submit,complete}`.
- Scenarios: Sarah Chen preventive + hypertension follow-up; James Wilson laceration repair + brief E&M.
- Known fixed audit items: X12 SE count, Copy EDI comment filtering, PDF Box 24D CPT/modifier split, James diagnosis pointers, font-display optional, reduced-motion guards, card padding.
- Remaining pre-demo manual QA: fresh incognito walkthrough at 1440x900, download/open both PDFs, time both scenarios, pre-warm `/` and `/demo`.

Build verification should be run from a temp copy if avoiding NAS `node_modules` churn:

```bash
rsync -a --exclude node_modules --exclude .next ./ /tmp/revcyclemgmt-demo-build/
cd /tmp/revcyclemgmt-demo-build
npm ci
npm run build
```
