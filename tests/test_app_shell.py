from __future__ import annotations

import json
from pathlib import Path

import pytest

from revcyclemgmt_app_shell.claims_pipeline import CLAIM_PATHS, build_claims_pipeline_workspace
from revcyclemgmt_app_shell.artifacts import write_artifacts
from revcyclemgmt_app_shell.privacy import PrivacyBoundaryError, validate_synthetic_payload
from revcyclemgmt_app_shell.views import ROUTES, render_route
from revcyclemgmt_app_shell.workspace import build_workspace


def test_all_app_routes_return_200() -> None:
    for route in ROUTES:
        status, content_type, body = render_route(route)
        assert status == 200, route
        assert "text/html" in content_type
        assert "RevCycleMGMT" in body


@pytest.mark.parametrize(
    "payload",
    [
        {"organization_name": "Patient ID AB123456"},
        {"organization_name": "DOB: 01/02/1975"},
        {"organization_name": "555-222-1111"},
        {"organization_name": "person@example.com"},
        {"denial_focus": "member id ZXCVB12345"},
    ],
)
def test_intake_rejects_phi_shaped_inputs(payload: dict[str, str]) -> None:
    with pytest.raises(PrivacyBoundaryError):
        build_workspace(payload)


def test_render_route_returns_422_for_phi_shaped_query() -> None:
    status, _content_type, body = render_route("/app/intake", "organization_name=Patient%20ID%20ABC12345")
    assert status == 422
    assert "Input rejected" in body


def test_synthetic_boundary_holds_in_workspace() -> None:
    workspace = build_workspace()
    blob = json.dumps(workspace.__dict__, default=str)
    blocked = ["patient id", "date of birth", "member id", "QMT" + "RY", "HED" + "IS", "NC" + "QA", "Tap" + "estry"]
    for term in blocked:
        assert term.lower() not in blob.lower()
    validate_synthetic_payload(workspace.intake)


def test_artifacts_generate_svg_and_summary(tmp_path: Path) -> None:
    summary = write_artifacts(tmp_path)
    svg = tmp_path / "app_shell_proof.svg"
    claims_svg = tmp_path / "claims_pipeline_mapper_proof.svg"
    claims_summary = tmp_path / "claims_pipeline_mapper_summary.json"
    data = tmp_path / "app_shell_summary.json"
    assert svg.exists()
    assert claims_svg.exists()
    assert claims_summary.exists()
    assert data.exists()
    assert "No-PHI" in svg.read_text(encoding="utf-8")
    assert claims_svg.stat().st_size > 8_000
    assert "Claims Pipeline Mapper" in claims_svg.read_text(encoding="utf-8")
    assert summary["boundary"] == "synthetic-only"
    assert summary["claims_pipeline_mapper"]["boundary"] == "synthetic-only"


@pytest.mark.parametrize("claim_path", [path.slug for path in CLAIM_PATHS])
def test_claims_pipeline_workspace_views_render_for_each_sample_path(claim_path: str) -> None:
    workspace = build_claims_pipeline_workspace(claim_path)
    assert workspace.selected_path.slug == claim_path
    assert len(workspace.selected_path.nodes) == 8
    assert workspace.ownership
    assert workspace.stuck_points
    assert workspace.action_plan

    status, content_type, body = render_route("/app/claims-pipeline", f"path={claim_path}")
    assert status == 200
    assert "text/html" in content_type
    assert "Claim Path Timeline" in body
    assert "Ownership Map" in body
    assert "Stuck-Point Inventory" in body
    assert "First 30-Day Action Plan" in body
    assert workspace.selected_path.claim_id in body


def test_claims_pipeline_generated_artifacts_have_no_phi_shapes(tmp_path: Path) -> None:
    write_artifacts(tmp_path)
    root = Path(__file__).resolve().parents[1]
    generated = [
        tmp_path / "claims_pipeline_mapper_proof.svg",
        tmp_path / "claims_pipeline_mapper_summary.json",
        root / "docs" / "assets" / "claims-pipeline-mapper-proof.svg",
    ]
    blob = "\n".join(path.read_text(encoding="utf-8") for path in generated)
    blocked_patterns = {
        "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
        "mrn": r"\bMRN[A-Z0-9-]{3,}\b",
        "npi": r"\b[12]\d{9}\b",
        "email": r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b",
        "phone": r"\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]\d{3}[-.\s]\d{4}\b",
        "date_of_birth": r"\b(?:dob|date of birth)\b",
        "member_id": r"\b(?:member|subscriber|patient)\s*(?:id|#)\b",
    }
    import re

    for label, pattern in blocked_patterns.items():
        assert not re.search(pattern, blob, re.I), label
    assert "Synthetic" in blob


def test_no_real_client_or_vendor_partnership_copy_in_repo_docs() -> None:
    root = Path(__file__).resolve().parents[1]
    banned = [
        "QMT" + "RY",
        "federal " + "teaming",
        "HED" + "IS",
        "St" + "ars",
        "NC" + "QA",
        "Co" + "zeva",
        "Tap" + "estry",
        "Ep" + "ic",
        "Cer" + "ner",
        "Op" + "tum",
        "Advanced" + "MD",
        "Val" + "ant",
    ]
    scanned_paths = []
    for path in root.rglob("*"):
        if not path.is_file() or ".git" in path.parts or ".venv" in path.parts:
            continue
        if path.name in {"test_app_shell.py", "privacy.py"}:
            continue
        if path.suffix in {".md", ".py", ".json", ".svg", ".txt", ".yml", ".toml"}:
            scanned_paths.append(path)
    text = "\n".join(path.read_text(encoding="utf-8", errors="ignore") for path in scanned_paths)
    for term in banned:
        assert term.lower() not in text.lower(), term
