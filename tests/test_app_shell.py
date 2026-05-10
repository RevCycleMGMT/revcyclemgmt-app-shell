from __future__ import annotations

import json
from pathlib import Path

import pytest

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
    blocked = ["patient id", "date of birth", "member id", "QMTRY", "HEDIS", "NCQA", "Tapestry"]
    for term in blocked:
        assert term.lower() not in blob.lower()
    validate_synthetic_payload(workspace.intake)


def test_artifacts_generate_svg_and_summary(tmp_path: Path) -> None:
    summary = write_artifacts(tmp_path)
    svg = tmp_path / "app_shell_proof.svg"
    data = tmp_path / "app_shell_summary.json"
    assert svg.exists()
    assert data.exists()
    assert "No-PHI" in svg.read_text(encoding="utf-8")
    assert summary["boundary"] == "synthetic-only"


def test_no_real_client_or_vendor_partnership_copy_in_repo_docs() -> None:
    root = Path(__file__).resolve().parents[1]
    banned = [
        "QMTRY",
        "federal teaming",
        "HEDIS",
        "Stars",
        "NCQA",
        "Cozeva",
        "Tapestry",
        "Epic",
        "Cerner",
        "Optum",
        "AdvancedMD",
        "Valant",
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
