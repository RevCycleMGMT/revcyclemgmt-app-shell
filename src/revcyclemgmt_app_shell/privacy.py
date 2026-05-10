"""Synthetic-only validation helpers."""

from __future__ import annotations

import re

PHI_PATTERNS = {
    "ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "date_of_birth": re.compile(r"\b(?:dob|date of birth)\s*[:#-]?\s*\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b", re.I),
    "member_id": re.compile(r"\b(?:member|subscriber|patient|claim)\s*(?:id|#)\s*[:#-]?\s*[A-Z0-9-]{6,}\b", re.I),
    "medical_record": re.compile(r"\b(?:mrn|medical record)\s*[:#-]?\s*[A-Z0-9-]{5,}\b", re.I),
    "phone": re.compile(r"\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]\d{3}[-.\s]\d{4}\b"),
    "email": re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I),
}

FORBIDDEN_PUBLIC_TERMS = [
    "QMT" + "RY",
    "PM" + "O",
    "federal " + "teaming",
    "HED" + "IS",
    "St" + "ars",
    "NC" + "QA",
    "Co" + "zeva",
    "Tap" + "estry",
]


class PrivacyBoundaryError(ValueError):
    """Raised when input appears to contain PHI or forbidden public framing."""


def scan_text(value: str) -> list[str]:
    """Return boundary findings for a text value."""

    findings: list[str] = []
    for label, pattern in PHI_PATTERNS.items():
        if pattern.search(value):
            findings.append(label)
    for term in FORBIDDEN_PUBLIC_TERMS:
        if term.lower() in value.lower():
            findings.append(f"forbidden_term:{term}")
    return findings


def validate_synthetic_payload(payload: dict[str, str]) -> None:
    """Reject PHI-shaped or forbidden public-positioning input."""

    findings: list[str] = []
    for field, value in payload.items():
        if not isinstance(value, str):
            continue
        for finding in scan_text(value):
            findings.append(f"{field}:{finding}")
    if findings:
        raise PrivacyBoundaryError("Synthetic-only boundary violation: " + ", ".join(findings))
