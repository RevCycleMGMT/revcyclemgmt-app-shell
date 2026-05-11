"""Synthetic app-shell data.

All values in this module are invented for public proof use.
"""

from __future__ import annotations

ROADMAP_MODULES = [
    {
        "slug": "launch-workspace",
        "label": "Launch Workspace",
        "status": "Live intake",
        "description": "No-PHI startup-clinic intake, readiness checklist, and launch preview.",
    },
    {
        "slug": "claims-pipeline",
        "label": "Claims Pipeline Mapper",
        "status": "Live workspace",
        "description": "Claim journey, ownership map, stuck-point inventory, and first action plan.",
    },
    {
        "slug": "dashboard",
        "label": "KPI Dashboard",
        "status": "Live workspace",
        "description": "Headline scorecard, 13-week trends, breakdowns, and owner-ready action plan.",
    },
    {
        "slug": "edi-validation",
        "label": "EDI Validation",
        "status": "Coming next",
        "description": "837P readiness, acknowledgments, status mapping, and validation report.",
    },
    {
        "slug": "coding-readiness",
        "label": "Coding Readiness",
        "status": "Coming next",
        "description": "Documentation completeness, diagnosis/procedure readiness, and modifier prompts.",
    },
    {
        "slug": "clearinghouse-responses",
        "label": "Clearinghouse Response Tracker",
        "status": "Requires agreement",
        "description": "Submission movement, acknowledgments, payer status, and follow-up controls.",
    },
    {
        "slug": "835-matchback",
        "label": "835 Matchback",
        "status": "Coming next",
        "description": "Claim-to-remit matching, adjustment grouping, and variance queues.",
    },
    {
        "slug": "denial-workqueues",
        "label": "Denial Workqueues",
        "status": "Coming next",
        "description": "Root-cause routing, owner queues, appeal/rework paths, and recovery value.",
    },
    {
        "slug": "evidence",
        "label": "Evidence/Compliance",
        "status": "Requires agreement",
        "description": "Production boundary checklist, audit events, evidence exports, and runbooks.",
    },
    {
        "slug": "site-qa",
        "label": "MCP Site QA Console",
        "status": "Internal QA",
        "description": "Public-page QA, metadata checks, mixed-content scans, and visual regression.",
    },
]

DEFAULT_INTAKE = {
    "organization_name": "Synthetic Harbor Clinic",
    "specialty": "Behavioral health",
    "ehr": "Independent EHR/PM system",
    "clearinghouse_intent": "Evaluate partner-routed launch workflow",
    "payer_mix": "Commercial 60%, Medicaid managed care 25%, self-pay 15%",
    "monthly_claim_volume": "650",
    "launch_timing": "60-90 days",
    "denial_focus": "Eligibility, authorization, missing information",
}

DASHBOARD_METRICS = {
    "claims_submitted": 772,
    "clean_claim_rate": 0.9158,
    "clearinghouse_rejection_rate": 0.0427,
    "denial_rate": 0.0427,
    "remit_match_rate": 0.8044,
    "remits_matched": 621,
    "average_payment_lag_days": 5.6,
    "current_ar_exposure": 14100.0,
    "total_billed": 308850.0,
    "total_paid": 217200.0,
}

DASHBOARD_READOUT = [
    "772 synthetic claims were monitored across the launch window.",
    "Clean-claim rate is 91.6% with denial rate at 4.3%.",
    "Current A/R exposure is $14,100 with average payment lag of 5.6 days.",
]

CLAIMS_JOURNEY = [
    {
        "claim_id": "CLM-LAUNCH-001",
        "stage": "Paid / posted",
        "ack": "Accepted",
        "status": "Accepted",
        "remit": "Seen",
        "issue": "None",
        "owner": "Posting",
    },
    {
        "claim_id": "CLM-LAUNCH-002",
        "stage": "Front-end rejection",
        "ack": "Accepted",
        "status": "Rejected",
        "remit": "Not due",
        "issue": "Subscriber detail mismatch",
        "owner": "Billing ops",
    },
    {
        "claim_id": "CLM-LAUNCH-003",
        "stage": "Denial follow-up",
        "ack": "Accepted",
        "status": "Accepted",
        "remit": "Seen",
        "issue": "Missing information",
        "owner": "Denials",
    },
]

PLACEHOLDER_COPY = {
    "edi-validation": "This module will expose synthetic 837P, 999, 277CA, and 835 validation reports. Public mode will not accept real files.",
    "coding-readiness": "This module will show documentation and coding-readiness prompts without claiming final coding authority.",
    "clearinghouse-responses": "This module requires production agreements before any live status feed or credentials are used.",
    "835-matchback": "This module will connect synthetic claim rows to synthetic remittance outcomes and variance queues.",
    "denial-workqueues": "This module will convert denial reasons into owner-ready workqueues and recovery actions.",
    "evidence": "This module will track production readiness, access boundaries, audit events, and evidence exports.",
    "site-qa": "This internal module will stay scoped to public-site QA and operations checks.",
}
