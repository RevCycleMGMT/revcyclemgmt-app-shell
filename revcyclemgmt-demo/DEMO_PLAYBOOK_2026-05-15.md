# Demo playbook — Dr. Kim, Friday 2026-05-15 5 PM

Format: in-person, single screen. Ask: AAPC chapter endorsement / curriculum use.

This is **not a sales demo**. Frame: "I built training material, would you tell me where it falls short and whether it's ready for chapter use." Dr. Kim is an MD and AAPC chapter president — she's grading pedagogy, not buying software. The minute she senses you're selling, she'll stop coaching and start politely listening. Stay in coach-asks-coach mode.

---

## The single hardest discipline: NARRATE, don't WATCH the screen with her

You're at the same screen. She's watching the demo. **You're watching her face.** If you turn toward the screen alongside her, you become a passive spectator of your own product. Stay turned slightly toward her, talk at her pace, hit Skip on every animation that's longer than 5 seconds — she's already read it by the time the typewriter finishes.

This is the single most common in-person demo failure mode for technical founders. The screen is a prop. She's the audience.

---

## Pre-demo setup

### 90 minutes before

- [ ] `git pull` to latest. Verify the branch contains `653a7ea` or later on `ticket-1-next-demo-scaffold`. Run `npm run build` to confirm clean.
- [ ] `npm run dev` → open `http://localhost:3000/demo` in a fresh **incognito** Chrome window. Incognito to avoid extensions interfering and to look identical to what she'd see if she ever tried it herself.
- [ ] Walk both scenarios end-to-end. Time each. Should land around 8–12 minutes per scenario at narration pace (not full animation pace).
- [ ] **Generate both PDFs.** Open them. Confirm Box 24D shows CPT and modifier as separate sub-columns (Fix #2 from the audit). Print one of each on your home printer so you have a physical artifact in your bag — Dr. Kim is a clinician, paper still works.
- [ ] Open `DEMO_AUDIT_2026-05-12.md` in a tab. If she asks "did you stress-test this?", you have a real answer ready.
- [ ] Pre-warm Inter font: visit `localhost:3000/` and `localhost:3000/demo` in incognito. The font caches after first paint so the demo doesn't flash.

### 15 minutes before

- [ ] Laptop charger plugged in. Brightness max.
- [ ] Display Notifications OFF. Slack/Teams/email silent. iMessage closed.
- [ ] Browser zoom at 100%. Window sized to 1440×900 if possible (or full-screen).
- [ ] Demo URL bookmarked in the active window. URL bar visible (`localhost:3000/demo`) — she's an MD, she's seen enterprise EHRs, the dev URL signals "this is real, not a slide deck."
- [ ] One terminal visible with the dev server running. If she asks "is this connected to anything live?" you can pivot to: "No — and that's deliberate. Every patient is synthetic, every payer response is canned. I'll show you the code."
- [ ] Phone face down, do-not-disturb on.

### 1 minute before

- [ ] Take a breath. You built this. The math reconciles. Codex shipped the fixes. The audit is clean.
- [ ] Have a printed copy of one CMS-1500 PDF and one X12 transcript on the table — physical artifacts make this real.

---

## The opening — 60 seconds, verbatim-able

Say something close to this:

> "Thank you for making time. I want to be upfront about what this is and what I want from you. I built a training demo that walks a new biller through two real-world claims end to end — encounter notes through CMS-1500 through X12 837P through 835 remittance. I built it because there's a gap between the AAPC CPC textbook and the moment a new coder sits down at AdvancedMD and has to actually file a clean claim. The textbook teaches the codes. This demo teaches the workflow.
>
> What I want from you is a pedagogical review. I want you to tell me where this falls short, where the coding logic is wrong, where a new biller would be misled. And if you think it's sound, I want to ask you what it would take to put it in front of your chapter members as supplemental training. I'd like your chapter to be the first one this gets used by.
>
> I'm going to walk two scenarios. Sarah Chen is the canonical modifier-25 case. James Wilson is the injury-with-external-cause case. Both are AAPC exam targets. Stop me anywhere — I'd rather you find an error live than after I put this in front of fifty new coders."

That's ~45 seconds. The key sentences are *"I want a pedagogical review"* and *"I want to ask what it would take to put it in front of your chapter members."* You've now named the ask. The rest of the meeting is her evaluating against that ask.

---

## Scenario 1 — Sarah Chen (10 minutes)

She's the simpler case. Builds rapport. Sets up the workflow vocabulary.

### Step 1 — Scenarios landing page (`/demo`) — 30 seconds

Click into Sarah Chen.

> "Sarah Chen, 45, established patient, annual physical with a hypertension follow-up. Classic two-services-one-visit. This is the most-tested concept on the AAPC CPC exam."

### Step 2 — Encounter page — 60 seconds

She'll read the clinical note. Don't narrate the note itself.

> "Standard SOAP-style documentation. The clue Dr. Kim's chapter teaches: 'separately identifiable from the preventive service' — that phrase in the assessment is what justifies modifier 25 on the problem-focused E&M. If it's not in the note, you can't bill it."

Hit **Continue to Coding**.

### Step 3 — Coding page — 90 seconds

**Important: hit the Skip Animation button immediately.** All seven highlights and four code cards appear at once. Don't make her watch 30 seconds of phrase-pulses.

> "Two diagnoses: Z00.00 for the preventive — note the trailing zero, AAPC trips students on Z00.00 versus Z00.0. And I10 for the hypertension — no decimal, that's the rule.
>
> Two procedures: 99396 for the age-band-specific preventive — 40–64 established — and 99213 with modifier 25. Notice the modifier is its own field. If we appended it to the CPT in the data model, we'd lose the ability to point each diagnosis at the right service line in box 24E. The modifier carries its own meaning."

**Pause here.** Look at her. Ask:

> "Did I get modifier 25 right? Is the 'separately identifiable' phrase the strongest hook to teach modifier 25, or would you teach it differently?"

This is the first of two intentional pauses. You're inviting her into the demo as a co-author. Whatever she says, write it down on a paper notepad in front of her. (Actually write it. The visible writing matters.)

Hit **Continue to Build Claim**.

### Step 4 — Claim builder — 60 seconds

Rows stagger in over 500ms. Let it play; it's short.

> "Both procedures in the claim. Modifier 25 is a separate badge. Diagnosis pointers — Z00.00 points to 99396, I10 points to 99213. Hover the modifier badge — there's a tooltip explaining the rule."

Hover the modifier badge to show the tooltip. Hit **Continue to Forms**.

### Step 5 — Forms (CMS-1500 + X12) — 2 minutes

**Skip the typewriter animation.** Click Skip immediately. The form fills in.

> "Box 1 — Group Health Plan checked because BCBS PPO is commercial. Box 1a member ID. Box 2 patient name in last-comma-first format. Box 6 self-relationship checked. Box 11 group number. Box 11c plan name.
>
> Box 21 — both diagnoses with letter prefixes A and B. Box 24E pointer A for the preventive line, B for the E&M line. That's how the claim tells the payer 'this E&M was for the hypertension, not the preventive.'
>
> Box 24D — CPT and modifier in their own visual sub-columns. That's the AAPC standard for the 02-12 form."

Click the **X12 837P EDI** tab.

> "Same claim, electronic format. ISA envelope, GS functional group, ST transaction set 837. HI segment with ABK qualifier for the primary diagnosis, ABF for the secondary. SV1 segments with HC qualifier prefix on each CPT. SE segment count at the bottom is 23 — counted by hand against the segments above. I had a bug here last week that gave wrong counts; we caught it in audit and fixed it before today."

The "I had a bug, we caught it" framing is gold with Dr. Kim. It signals you have an audit discipline. Don't dwell on it — half-sentence, move on.

Click **Generate PDF**. The PDF downloads.

> "Take-home artifact. If a new biller wants to study this offline, this is the printable form."

Hit **Continue to Submit**.

### Step 6 — Submit page — 2 minutes

Timeline plays. Let it run — 7 seconds, manageable. Narrate over the top:

> "Submitted to clearinghouse… 999 acknowledgment, file is well-formed… 277CA, payer accepted it for adjudication… adjudicating… 835 remittance ready."

The remittance card appears at 8s.

> "Sarah's outcome. BCBS allowed $220 on the preventive — full pay, $0 patient responsibility because the ACA mandates preventive at 100% in-network. $30 contractual adjustment, that's CO-45 charge exceeds fee schedule.
>
> On the E&M, allowed $98, BCBS paid $68 after a $30 copay applied to the patient. Total billed $375, payer paid $288, patient owes $30, contractual adjustments $57. Everything reconciles to the penny."

Hit **Demo Complete**.

### Step 7 — Complete page — 30 seconds

> "That's Sarah. Let me show you the harder case."

Click back to `/demo`, click James Wilson.

---

## Scenario 2 — James Wilson (10 minutes)

This is the AAPC discrimination case. Injury, external cause, A-suffix, comorbidity context for the E&M. This is where Dr. Kim's expertise actually matters.

### Step 1 — Encounter page — 90 seconds

> "James Wilson, 62, Medicare Part B, comes in an hour after a kitchen accident. Four-centimeter laceration on the right forearm, kitchen knife, last tetanus 2019. He's also a Type 2 diabetic, well controlled.
>
> Three things every new coder gets wrong on this case: the A suffix for initial encounter, the external cause code with placeholder X's, and the diagnosis pointers on the E&M when there's a comorbidity in play."

Continue to Coding.

### Step 2 — Coding page — 2 minutes

Hit **Skip Animation**.

> "Three diagnoses. S51.811A — note the A suffix, AAPC fails students who drop it. W26.0XXA — note the placeholder X's and the A suffix; external cause sequencing is its own rule chapter. E11.9 — type 2 diabetes without complications, not E11.0. The 0-versus-9 distinction trips up new coders.
>
> Four procedures. 99213 with modifier 25. 12002 for the repair — four-centimeter simple repair falls in the 2.6-to-7.5-cm range. 90471 for the immunization administration. 90714 for the Td vaccine product. Admin and product are reported separately for tetanus."

**Second intentional pause.** Look at her. Ask:

> "I'm going to ask you a coding-judgment call before we get to the claim. On the E&M, I pointed only at E11.9 — only the diabetes. My reasoning: modifier 25 requires the E&M to be separately identifiable from the procedure. The 12002 repair is supported by S51.811A. If the E&M also points to S51.811A, I lose the 'separately identifiable' signal. By pointing only at the comorbidity that justified the wound-healing review, I'm making the modifier-25 case explicit.
>
> Is that the right teach? Or would you point the E&M at both A and C — 'A for the injury context, C for the diabetes consideration'?"

This is the question that earns you her respect. You're not asking permission — you're showing her you understand the trade-off and have a defensible position. Whatever she says, write it down.

Continue to Build Claim.

### Step 3 — Claim builder — 60 seconds

> "Four service lines. Note Box 24E pointers: 99213-25 points to C only — that's my call. 12002 points to A and B — laceration plus external cause. 90471 and 90714 both point to A — without a Z23 'encounter for immunization' in the scenario, the laceration is the documented reason."

Continue to Forms.

### Step 4 — Forms — 2 minutes

Skip the typewriter.

> "Box 1 Medicare checked — Medicare Part B is the payer. Box 1a is his Medicare beneficiary identifier — synthetic, but in the new MBI format Medicare moved to in 2018: alphanumeric, no Social.
>
> Box 21 lists all three diagnoses, letters A through C. Box 24E shows the pointer differentiation across the four service lines — A, AB, A, A. Box 24D — modifier 25 in its own sub-column on the E&M line, no modifier on the repair, admin, or product."

Click X12 tab.

> "SBR segment uses MB qualifier for Medicare instead of CI for commercial. CLM02 carries the $390 total. HI segment has all three diagnoses with the ABK/ABF qualifier discipline. SE count is 29 — four procedures means 12 service-line segments plus the 17 fixed."

Generate PDF.

> "Second take-home."

Continue to Submit.

### Step 5 — Submit + remittance — 2 minutes

> "James is Medicare. Watch the adjustments — Medicare reimbursement is roughly 60–70% of charges, and that surprises new billers every time.
>
> 99213 allowed $73.50 against a $125 charge — that's a $51.50 CO-45 contractual writedown. $58.80 paid after Medicare's 20% coinsurance of $14.70 lands on the patient.
>
> 12002 allowed $138.20 against $190 — $51.80 writedown. Repair lands the patient another $27.64 coinsurance.
>
> Admin and vaccine: full pay, no patient responsibility, small adjustments.
>
> Total billed $390, Medicare paid $229.78, patient owes $42.34, adjustments $117.88. Medicare took 30% off the top in contractual reductions. That's the lived reality of Medicare RCM, and it's something most CPC graduates haven't felt until they get to their first job."

That last line is your strongest pedagogical claim. Dr. Kim teaches; she knows the gap between exam-room coding and real-world reimbursement reality. Naming it explicitly invites her to validate.

Hit Demo Complete.

---

## The close — 5 minutes

This is the actual point of the meeting. Don't rush it.

> "That's the demo. Two scenarios, six steps each, end to end. Both based on real-world coding patterns AAPC tests on. Everything is synthetic — no PHI ever touched this, every patient is invented, the payer responses are canned. The CMS-1500 form is the 02-12 layout. The X12 is real 837P-style syntax; the segment counts validate and the copied EDI excludes the teaching comments shown on screen.
>
> Three questions for you, in order of how much it matters to me:
>
> One — is the coding sound? Tell me where you'd correct it.
>
> Two — is the workflow accurate? Would a biller leaving your chapter's CPC prep program recognize this as the real day-one work?
>
> Three — and this is the actual ask — if it's sound, what would it take for your chapter to use this as supplemental training? Could I build a 30-minute session around it for one of your monthly meetings? Would AAPC nationally be interested in seeing it? What's the path?"

Then **shut up**. Let her think. Don't fill silence. She's an MD; she's used to thinking through clinical decisions before speaking. The next 30–90 seconds of silence is the most valuable part of the meeting.

When she speaks, write down what she says verbatim on the notepad. Don't paraphrase. Don't argue. Don't defend. If she flags an error, say "you're right, I'll fix that this weekend." If she has a suggestion, say "what would the AAPC-correct version look like?" — invite her to be the teacher.

If she says yes to the chapter use, follow up with: "What would you need from me to make that easy? A facilitator guide? A pre-built quiz? Access to a private fork of the demo?"

---

## Anticipated questions + pre-baked answers

### "How did you build this?"
"Next.js front-end, TypeScript, no backend — all data is synthetic and static. Roughly two weeks of focused work with an AI coding assistant. The data integrity logic is hand-coded; the visual presentation is mostly framework defaults. I'll send you the GitHub link after the meeting if you want to look at it."

### "Where does the data come from?"
"Every patient is invented. Every code is from the current AAPC code books. Every payer response is canned — I wrote them by hand to make the math reconcile. There's no real practice and no real claim file in this codebase. That's deliberate — this is training material, and the line between training material and a real claim is a line I won't blur."

### "Is this HIPAA compliant?"
"It doesn't need to be — there's no PHI. That's by design. If your chapter wanted to adapt it for actual practice training with real claims, that's a different conversation and we'd need a BAA-protected hosting arrangement. For training-room use with these synthetic cases, it's just a static web app."

### "Could AAPC use this nationally?"
"That's exactly what I'd want to explore. The two scenarios cover the highest-frequency CPC exam topics — modifier 25, S/W code sequencing, A-suffix discipline, external cause codes, comorbidity diagnosis pointing. I could add more scenarios — institutional billing for 837I, dental, telehealth, behavioral health. If there's interest from AAPC nationally, I'd build the curriculum around their exam blueprint."

### "What's the business model?"
Be honest, but lead with the pedagogy:
"For chapter use — free. The demo is the demo. For my actual business, RevCycleMGMT, this is part of the credibility layer. I build revenue infrastructure for independent practices, and showing that I understand the work this thoroughly is how I earn the right to be in those conversations. The demo doesn't sell my services directly — but the people who graduate from it might recognize me later when they're at a practice that needs help."

### "What if I find an error?"
"Then I owe you a fix. Tell me what you'd correct and I'll have it shipped by Monday."

### "I want to show this to my chapter board / education committee."
"Yes please. What format helps you the most — should I send a recording, an offline build, a facilitator guide, or all three? What's their timeline?"

### "Will this still be here in six months?"
"Yes. It's a static site, no backend, no recurring cost beyond a few cents in hosting per month. I'll keep it live indefinitely."

### "Why did you pick Sarah Chen / James Wilson specifically?"
"Modifier 25 and external-cause-coding are the two AAPC exam concepts new coders most consistently fail. I built the two scenarios that test exactly those concepts. If your chapter has other top-frequency failure points, I'd build scenarios around them next."

---

## Failure modes — what to do if something breaks live

### Dev server crashes mid-demo
Open a second terminal, `npm run dev` in it. Refresh the browser. Recover with: "Forgive me — this is running off my laptop, not a deployed environment. Production won't have that issue." Keep going.

### PDF doesn't download
Two-tab fallback: the on-screen CMS-1500 form is identical to the PDF except for a few extra reference boxes. Pull out the **printed PDF you brought in your bag**: "Here — I printed one earlier in case the download misbehaved on this laptop."

### Animation hangs
Refresh the page. The state is URL-based; you land back on the same step. The Skip button exists for exactly this — don't try to fix it live, just skip past.

### She catches a real error in your math
She won't — the audit was clean — but if she does: "You're right. I'll fix that tonight and email you the corrected version Monday." Do not try to defend the error live. Write it down. Move on.

### She catches a coding judgment call that's defensibly different from what AAPC teaches
This is the interesting case — see Scenario 2 Step 2's intentional pause. Engage genuinely: "Tell me how AAPC frames it — I want to make sure the demo aligns with your chapter's curriculum, not just my interpretation." This is the moment you turn her from "judge" to "co-author".

### She's bored / checks her phone
Skip to the close earlier than planned. She's already made her decision. Don't drag through the rest of James Wilson — ask for her feedback now.

### She loves it and wants to commit live
Don't over-commit on the spot. "I'd love that — let me follow up Monday with a specific proposal for what curriculum integration looks like, so we're not deciding the shape of this on a handshake." Then deliver Monday.

---

## After the meeting

### Within 24 hours

Send a follow-up email. Verbatim-able:

> "Dr. Kim — thank you for the time today. Below is what I heard you ask for; please correct anything I got wrong.
>
> [list what she said, exactly — the notes you wrote on the notepad in front of her]
>
> Next steps from my side, by [day next week]:
> 1. [if she flagged an error]: corrected version live with a note about what changed
> 2. [if she asked for a facilitator guide]: a 4-page facilitator guide for the demo
> 3. [if she wanted to show the chapter]: a screen-recorded walkthrough at her preferred length
>
> Next steps from your side, if you're willing:
> 1. [whatever you actually asked her to do — review by date X, intro to her chapter board, etc.]
>
> The demo will stay live at [URL] — I'll send you a stable link after I deploy it to a permanent host on Monday. The GitHub repo is at [URL] — both files attached are the CMS-1500 PDFs from the demo. The README and audit file document how I tested this for accuracy and how I caught and fixed errors before showing it to you.
>
> I'm at [phone] for anything. Thank you again."

### Within one week

Whatever you promised, deliver it. If she asked for a facilitator guide, ship the facilitator guide. If she asked for an intro deck for the AAPC education committee, ship that. The follow-through is what converts a polite meeting into a partnership.

### Add Dr. Kim to the people memory

After the meeting, drop a profile at `Z:\BUSINESSES\memory\people\dr-kim-[lastname].md` capturing:
- Her exact title (AAPC chapter name, role, MD specialty)
- What she committed to
- What you committed to
- Her communication preferences (you'll have observed them by then)
- Any nicknames or specific phrases she used

Update `Z:\BUSINESSES\memory\glossary.md` Nicknames table.

---

## One last thing

The biggest version of the win here isn't "AAPC chapter uses the demo." It's: **Dr. Kim becomes a clinical/coding advisor to RevCycleMGMT.** If the demo lands well enough that she sees you as someone who understands coding the way she does, the natural next move is advisor — formal or informal — to your future H-002 hire, to your billing curriculum, to your customer-facing copy. That's a much bigger win than a curriculum endorsement, and it's downstream of doing this demo well.

Don't ask for advisor at this meeting. Ask for curriculum. The advisor relationship comes later, organically, once you've earned the right.

Good luck Friday.
