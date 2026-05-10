"""Launch Workspace calculations for synthetic intake."""

from __future__ import annotations

from dataclasses import dataclass

from .data import CLAIMS_JOURNEY, DEFAULT_INTAKE
from .privacy import validate_synthetic_payload


@dataclass(frozen=True)
class LaunchWorkspace:
    intake: dict[str, str]
    readiness_score: int
    first_build: str
    recommended_module: str
    checklist: list[str]
    claims_journey: list[dict[str, str]]


def normalize_intake(payload: dict[str, str] | None = None) -> dict[str, str]:
    """Merge submitted values over the safe synthetic default."""

    merged = dict(DEFAULT_INTAKE)
    if payload:
        merged.update({key: str(value).strip() for key, value in payload.items() if str(value).strip()})
    validate_synthetic_payload(merged)
    return merged


def readiness_score(intake: dict[str, str]) -> int:
    """Score launch readiness from non-sensitive workflow facts."""

    score = 48
    volume = int("".join(ch for ch in intake.get("monthly_claim_volume", "") if ch.isdigit()) or "0")
    if volume >= 500:
        score += 12
    if "eligibility" in intake.get("denial_focus", "").lower():
        score += 10
    if "authorization" in intake.get("denial_focus", "").lower():
        score += 8
    if "partner-routed" in intake.get("clearinghouse_intent", "").lower():
        score += 8
    if "60" in intake.get("launch_timing", "") or "90" in intake.get("launch_timing", ""):
        score += 7
    return min(score, 94)


def build_checklist(score: int) -> list[str]:
    """Create a no-PHI launch readiness checklist."""

    base = [
        "Confirm no-PHI discovery scope before any file intake.",
        "Map current EHR/PM, billing, payer-response, remit, and dashboard handoffs.",
        "Select the first synthetic claim journey to mirror during launch planning.",
        "Document denial categories and owner queues before automation work starts.",
        "Define the production-agreement checklist before credentials or files are requested.",
    ]
    if score >= 80:
        base.insert(1, "Prepare a paid design-partner scope for the first 30-day workflow build.")
    else:
        base.insert(1, "Run a short workflow-discovery sprint before estimating production launch scope.")
    return base


def build_workspace(payload: dict[str, str] | None = None) -> LaunchWorkspace:
    """Build the synthetic Launch Workspace output."""

    intake = normalize_intake(payload)
    score = readiness_score(intake)
    first_build = "Dashboard Proof + Claims Pipeline Mapper"
    recommended_module = "Launch Workspace"
    if "denial" in intake.get("denial_focus", "").lower():
        first_build = "Denial Workqueues + Dashboard Proof"
        recommended_module = "Denial Workqueues"
    if "eligibility" in intake.get("denial_focus", "").lower():
        first_build = "Claims Pipeline Mapper + Dashboard Proof"
        recommended_module = "Claims Pipeline Mapper"
    return LaunchWorkspace(
        intake=intake,
        readiness_score=score,
        first_build=first_build,
        recommended_module=recommended_module,
        checklist=build_checklist(score),
        claims_journey=list(CLAIMS_JOURNEY),
    )
