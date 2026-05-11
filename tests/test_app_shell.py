from __future__ import annotations

import json
from pathlib import Path

import pytest

from revcyclemgmt_app_shell.claims_pipeline import CLAIM_PATHS, build_claims_pipeline_workspace
from revcyclemgmt_app_shell.artifacts import write_artifacts
from revcyclemgmt_app_shell.clearinghouse_responses import (
    build_clearinghouse_responses_workspace,
    render_clearinghouse_responses_svg,
)
from revcyclemgmt_app_shell.dashboard import build_dashboard_workspace, render_dashboard_svg, worst_three
from revcyclemgmt_app_shell.edi_validation import build_edi_validation_workspace, render_edi_validation_svg
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
    dashboard_svg = tmp_path / "rcm_dashboard_proof.svg"
    dashboard_summary = tmp_path / "rcm_dashboard_summary.json"
    edi_svg = tmp_path / "edi_validation_harness_proof.svg"
    edi_summary = tmp_path / "edi_validation_summary.json"
    clearinghouse_svg = tmp_path / "clearinghouse_responses_proof.svg"
    clearinghouse_summary = tmp_path / "clearinghouse_responses_summary.json"
    data = tmp_path / "app_shell_summary.json"
    assert svg.exists()
    assert claims_svg.exists()
    assert claims_summary.exists()
    assert dashboard_svg.exists()
    assert dashboard_summary.exists()
    assert edi_svg.exists()
    assert edi_summary.exists()
    assert clearinghouse_svg.exists()
    assert clearinghouse_summary.exists()
    assert data.exists()
    assert "No-PHI" in svg.read_text(encoding="utf-8")
    assert claims_svg.stat().st_size > 8_000
    assert "Claims Pipeline Mapper" in claims_svg.read_text(encoding="utf-8")
    assert dashboard_svg.stat().st_size > 30_000
    assert "RCM Dashboard KPI" in dashboard_svg.read_text(encoding="utf-8")
    assert edi_svg.stat().st_size > 30_000
    assert "EDI Validation Harness" in edi_svg.read_text(encoding="utf-8")
    assert clearinghouse_svg.stat().st_size > 30_000
    assert "Clearinghouse Response Tracker" in clearinghouse_svg.read_text(encoding="utf-8")
    assert summary["boundary"] == "synthetic-only"
    assert summary["claims_pipeline_mapper"]["boundary"] == "synthetic-only"
    assert summary["rcm_dashboard_kpi_workspace"]["boundary"] == "synthetic-only"
    assert summary["edi_validation_harness"]["boundary"] == "synthetic-only"
    assert summary["clearinghouse_responses"]["boundary"] == "synthetic-only"


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


def test_dashboard_workspace_views_render_with_expected_kpis() -> None:
    workspace = build_dashboard_workspace()
    assert len(workspace.kpis) == 5
    assert len(workspace.trends) == 13
    assert set(workspace.breakdowns) == {"Payer", "CARC code", "Specialty", "Claim type"}
    assert workspace.action_plan
    for rows in workspace.breakdowns.values():
        assert len(worst_three(rows)) == 3

    status, content_type, body = render_route("/app/dashboard")
    assert status == 200
    assert "text/html" in content_type
    expected = [
        "Headline Scorecard",
        "13-Week Trend",
        "Breakdowns",
        "30-Day Action Plan",
        "Clean claim rate",
        "First-pass yield",
        "Denial rate",
        "Days in A/R",
        "Net collection rate",
        "Worst three",
    ]
    for label in expected:
        assert label in body


def test_dashboard_generated_artifacts_have_no_phi_shapes(tmp_path: Path) -> None:
    write_artifacts(tmp_path)
    root = Path(__file__).resolve().parents[1]
    generated = [
        tmp_path / "rcm_dashboard_proof.svg",
        tmp_path / "rcm_dashboard_summary.json",
        root / "docs" / "assets" / "rcm-dashboard-proof.svg",
    ]
    blob = "\n".join(path.read_text(encoding="utf-8") for path in generated)
    blocked_patterns = {
        "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
        "mrn": r"\bMRN[A-Z0-9-]{3,}\b",
        "email": r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b",
        "phone": r"\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]\d{3}[-.\s]\d{4}\b",
        "date_of_birth": r"\b(?:dob|date of birth)\b",
        "member_id": r"\b(?:member|subscriber|patient)\s*(?:id|#)\b",
    }
    import re

    for label, pattern in blocked_patterns.items():
        assert not re.search(pattern, blob, re.I), label
    assert not any(_is_luhn_valid(match) for match in re.findall(r"\b\d{13,19}\b", blob))
    assert not any(_is_valid_npi(match) for match in re.findall(r"\b[12]\d{9}\b", blob))
    assert "Synthetic" in blob


def test_dashboard_svg_is_non_trivial() -> None:
    svg = render_dashboard_svg(build_dashboard_workspace())
    assert len(svg.encode("utf-8")) > 30_000
    assert "Headline" in svg or "RCM Dashboard KPI" in svg


def test_edi_validation_workspace_views_render_with_expected_sections() -> None:
    workspace = build_edi_validation_workspace()
    assert len(workspace.failure_catalog) >= 8
    assert [row.payer for row in workspace.payer_variance] == [
        "Synthetic Payer A",
        "Synthetic Payer B",
        "Synthetic Payer C",
        "Synthetic Payer D",
        "Synthetic Payer E",
    ]
    assert workspace.action_plan

    status, content_type, body = render_route("/app/edi-validation")
    assert status == 200
    assert "text/html" in content_type
    expected = [
        "Submission Readiness Check",
        "Failure Catalog",
        "Payer Variance Map",
        "30-Day Readiness Plan",
        "Ready to submit",
        "Synthetic Payer A",
        "Synthetic Payer B",
        "Synthetic Payer C",
        "Synthetic Payer D",
        "Synthetic Payer E",
    ]
    for label in expected:
        assert label in body


def test_edi_validation_generated_artifacts_have_no_phi_shapes(tmp_path: Path) -> None:
    write_artifacts(tmp_path)
    root = Path(__file__).resolve().parents[1]
    generated = [
        tmp_path / "edi_validation_harness_proof.svg",
        tmp_path / "edi_validation_summary.json",
        root / "docs" / "assets" / "edi-validation-harness-proof.svg",
    ]
    blob = "\n".join(path.read_text(encoding="utf-8") for path in generated)
    blocked_patterns = {
        "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
        "mrn": r"\bMRN[A-Z0-9-]{3,}\b",
        "email": r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b",
        "phone": r"\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]\d{3}[-.\s]\d{4}\b",
        "date_of_birth": r"\b(?:dob|date of birth)\b",
        "member_id": r"\b(?:member|subscriber|patient)\s*(?:id|#)\b",
        "payer_member_id": r"\b(?!SYN)[A-Z]{3}\d{6,12}\b",
    }
    import re

    for label, pattern in blocked_patterns.items():
        assert not re.search(pattern, blob, re.I), label
    assert not any(_is_luhn_valid(match) for match in re.findall(r"\b\d{13,19}\b", blob))
    assert not any(_is_valid_npi(match) for match in re.findall(r"\b[12]\d{9}\b", blob))
    assert "Synthetic" in blob


def test_edi_validation_svg_is_non_trivial() -> None:
    svg = render_edi_validation_svg(build_edi_validation_workspace())
    assert len(svg.encode("utf-8")) > 30_000
    assert "EDI Validation Harness" in svg


def test_clearinghouse_responses_workspace_views_render_with_expected_sections() -> None:
    workspace = build_clearinghouse_responses_workspace()
    assert len(workspace.timeline) >= 12
    assert len(workspace.stuck_inventory) >= 8
    assert {parser.response_type for parser in workspace.parser_examples} == {"999", "277CA", "277"}

    status, content_type, body = render_route("/app/clearinghouse-responses")
    assert status == 200
    assert "text/html" in content_type
    expected = [
        "Submission Timeline",
        "Response Parser View",
        "Stuck-in-Clearinghouse Inventory",
        "30-Day Tracking Plan",
        "999",
        "277CA",
        "277",
    ]
    for label in expected:
        assert label in body


def test_clearinghouse_responses_generated_artifacts_have_no_phi_shapes(tmp_path: Path) -> None:
    write_artifacts(tmp_path)
    root = Path(__file__).resolve().parents[1]
    generated = [
        tmp_path / "clearinghouse_responses_proof.svg",
        tmp_path / "clearinghouse_responses_summary.json",
        root / "docs" / "assets" / "clearinghouse-responses-proof.svg",
    ]
    blob = "\n".join(path.read_text(encoding="utf-8") for path in generated)
    blocked_patterns = {
        "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
        "mrn": r"\bMRN[A-Z0-9-]{3,}\b",
        "email": r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b",
        "phone": r"\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]\d{3}[-.\s]\d{4}\b",
        "date_of_birth": r"\b(?:dob|date of birth)\b",
        "member_id": r"\b(?:member|subscriber|patient)\s*(?:id|#)\b",
        "payer_member_id": r"\b(?!Synthetic Payer [A-E]\b)[A-Z]{3}\d{6,12}\b",
    }
    import re

    for label, pattern in blocked_patterns.items():
        assert not re.search(pattern, blob, re.I), label
    assert not any(_is_luhn_valid(match) for match in re.findall(r"\b\d{13,19}\b", blob))
    assert not any(_is_valid_npi(match) for match in re.findall(r"\b[12]\d{9}\b", blob))
    assert "Synthetic" in blob


def test_clearinghouse_responses_svg_is_non_trivial() -> None:
    svg = render_clearinghouse_responses_svg(build_clearinghouse_responses_workspace())
    assert len(svg.encode("utf-8")) > 30_000
    assert "Clearinghouse Response Tracker" in svg


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


def _is_luhn_valid(value: str) -> bool:
    digits = [int(char) for char in value if char.isdigit()]
    total = 0
    parity = len(digits) % 2
    for index, digit in enumerate(digits):
        if index % 2 == parity:
            digit *= 2
            if digit > 9:
                digit -= 9
        total += digit
    return total % 10 == 0


def _is_valid_npi(value: str) -> bool:
    return _is_luhn_valid(f"80840{value}")
