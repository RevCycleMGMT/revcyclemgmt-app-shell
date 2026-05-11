"""Generate README-facing proof artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .claims_pipeline import build_claims_pipeline_workspace, claims_pipeline_summary, render_claims_pipeline_svg
from .clearinghouse_responses import (
    build_clearinghouse_responses_workspace,
    clearinghouse_responses_summary,
    render_clearinghouse_responses_svg,
)
from .data import DASHBOARD_METRICS, ROADMAP_MODULES
from .dashboard import build_dashboard_workspace, dashboard_summary, render_dashboard_svg
from .edi_validation import build_edi_validation_workspace, edi_validation_summary, render_edi_validation_svg
from .workspace import build_workspace

ROOT = Path(__file__).resolve().parents[2]


def generate_summary() -> dict[str, object]:
    workspace = build_workspace()
    return {
        "headline": "No-PHI app shell with Launch Workspace and Dashboard Proof anchor.",
        "boundary": "synthetic-only",
        "readiness_score": workspace.readiness_score,
        "first_build": workspace.first_build,
        "recommended_module": workspace.recommended_module,
        "functional_routes": ["/app/intake", "/app/claims-pipeline", "/app/dashboard", "/app/edi-validation", "/app/clearinghouse-responses"],
        "reserved_modules": [
            module["label"]
            for module in ROADMAP_MODULES
            if module["status"] not in {"Live intake", "Live workspace", "Synthetic proof"}
        ],
        "dashboard_metrics": DASHBOARD_METRICS,
        "checklist": workspace.checklist,
        "claims_journey": workspace.claims_journey,
    }


def generate_svg(summary: dict[str, object]) -> str:
    modules = ROADMAP_MODULES
    rows = []
    y = 236
    for module in modules:
        color = "#00B3A4" if module["status"] in {"Live intake", "Live workspace", "Synthetic proof"} else "#31545c"
        rows.append(
            f'<rect x="54" y="{y}" width="292" height="42" rx="8" fill="#0d1a1f" stroke="{color}" />'
            f'<text x="72" y="{y + 25}" fill="#f4fbfa" font-size="15" font-weight="700">{esc(module["label"])}</text>'
            f'<text x="257" y="{y + 25}" fill="#9ab5b5" font-size="11" text-anchor="end">{esc(module["status"])}</text>'
        )
        y += 50

    checklist = summary["checklist"]
    checklist_rows = []
    y = 336
    for item in checklist[:5]:
        checklist_rows.append(
            f'<circle cx="418" cy="{y - 5}" r="5" fill="#00B3A4" />'
            f'<text x="434" y="{y}" fill="#d8e7e5" font-size="15">{esc(str(item))}</text>'
        )
        y += 34

    metric_cards = [
        ("Claims", f"{DASHBOARD_METRICS['claims_submitted']:,}"),
        ("Clean claim", f"{DASHBOARD_METRICS['clean_claim_rate'] * 100:.1f}%"),
        ("Rejection", f"{DASHBOARD_METRICS['clearinghouse_rejection_rate'] * 100:.1f}%"),
        ("835 match", f"{DASHBOARD_METRICS['remit_match_rate'] * 100:.1f}%"),
    ]
    metric_svg = []
    x = 400
    for label, value in metric_cards:
        metric_svg.append(
            f'<rect x="{x}" y="586" width="154" height="82" rx="10" fill="#071316" stroke="#21414a" />'
            f'<text x="{x + 16}" y="616" fill="#9ab5b5" font-size="13">{label}</text>'
            f'<text x="{x + 16}" y="648" fill="#7dd3d8" font-size="26" font-weight="800">{value}</text>'
        )
        x += 170

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="760" viewBox="0 0 1280 760" role="img" aria-labelledby="title desc">
  <title id="title">RevCycleMGMT app shell proof</title>
  <desc id="desc">Generated SVG showing the No-PHI Launch Workspace, roadmap navigation, dashboard metrics, and synthetic-only boundary.</desc>
  <defs>
    <linearGradient id="bg" x1="0" x2="1" y1="0" y2="1">
      <stop stop-color="#071012" offset="0" />
      <stop stop-color="#123238" offset="1" />
    </linearGradient>
  </defs>
  <rect width="1280" height="760" fill="url(#bg)" />
  <rect x="26" y="26" width="1228" height="708" rx="18" fill="#0a1418" stroke="#21414a" />
  <rect x="34" y="34" width="332" height="692" rx="14" fill="#091316" stroke="#1f3941" />
  <text x="54" y="82" fill="#7dd3d8" font-size="28" font-weight="900">RevCycleMGMT</text>
  <text x="54" y="112" fill="#9ab5b5" font-size="13" letter-spacing="2">NO-PHI APP SHELL</text>
  {''.join(rows)}
  <text x="400" y="82" fill="#00B3A4" font-size="13" font-weight="800" letter-spacing="2">REVENUE INFRASTRUCTURE FOR INDEPENDENT HEALTHCARE PRACTICES</text>
  <text x="400" y="126" fill="#f4fbfa" font-size="40" font-weight="900">Launch Workspace + Dashboard Proof</text>
  <rect x="1010" y="74" width="184" height="42" rx="21" fill="#00B3A4" />
  <text x="1102" y="101" fill="#021415" font-size="15" font-weight="900" text-anchor="middle">Synthetic only</text>
  <rect x="400" y="166" width="330" height="132" rx="14" fill="#101b20" stroke="#21414a" />
  <text x="424" y="204" fill="#9ab5b5" font-size="14">Launch readiness</text>
  <text x="424" y="266" fill="#7dd3d8" font-size="64" font-weight="900">{summary["readiness_score"]}</text>
  <rect x="762" y="166" width="430" height="132" rx="14" fill="#101b20" stroke="#21414a" />
  <text x="786" y="204" fill="#9ab5b5" font-size="14">First recommended build</text>
  <text x="786" y="244" fill="#f4fbfa" font-size="25" font-weight="800">{esc(str(summary["first_build"]))}</text>
  <text x="786" y="276" fill="#00B3A4" font-size="16">Dashboard Proof remains the visual anchor.</text>
  <rect x="400" y="318" width="792" height="224" rx="14" fill="#101b20" stroke="#21414a" />
  <text x="424" y="354" fill="#f4fbfa" font-size="24" font-weight="900">Generated readiness checklist</text>
  {''.join(checklist_rows)}
  {''.join(metric_svg)}
  <text x="400" y="710" fill="#9ab5b5" font-size="15">Functional now: Launch Workspace, Claims Pipeline Mapper, KPI Dashboard, EDI Validation, and Response Tracker. Roadmap modules remain no-PHI.</text>
</svg>"""


def esc(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def write_artifacts(out_dir: Path) -> dict[str, object]:
    out_dir.mkdir(parents=True, exist_ok=True)
    assets_dir = ROOT / "docs" / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)
    summary = generate_summary()
    svg = generate_svg(summary)
    claims_workspace = build_claims_pipeline_workspace("denied-carc-16")
    claims_summary = claims_pipeline_summary(claims_workspace)
    claims_svg = render_claims_pipeline_svg(claims_workspace)
    dashboard_workspace = build_dashboard_workspace()
    dashboard_data = dashboard_summary(dashboard_workspace)
    dashboard_svg = render_dashboard_svg(dashboard_workspace)
    edi_workspace = build_edi_validation_workspace()
    edi_data = edi_validation_summary(edi_workspace)
    edi_svg = render_edi_validation_svg(edi_workspace)
    clearinghouse_workspace = build_clearinghouse_responses_workspace()
    clearinghouse_data = clearinghouse_responses_summary(clearinghouse_workspace)
    clearinghouse_svg = render_clearinghouse_responses_svg(clearinghouse_workspace)
    summary["claims_pipeline_mapper"] = claims_summary
    summary["rcm_dashboard_kpi_workspace"] = dashboard_data
    summary["edi_validation_harness"] = edi_data
    summary["clearinghouse_responses"] = clearinghouse_data
    (out_dir / "app_shell_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    (out_dir / "app_shell_proof.svg").write_text(svg, encoding="utf-8")
    (out_dir / "claims_pipeline_mapper_summary.json").write_text(json.dumps(claims_summary, indent=2) + "\n", encoding="utf-8")
    (out_dir / "claims_pipeline_mapper_proof.svg").write_text(claims_svg, encoding="utf-8")
    (out_dir / "rcm_dashboard_summary.json").write_text(json.dumps(dashboard_data, indent=2) + "\n", encoding="utf-8")
    (out_dir / "rcm_dashboard_proof.svg").write_text(dashboard_svg, encoding="utf-8")
    (out_dir / "edi_validation_summary.json").write_text(json.dumps(edi_data, indent=2) + "\n", encoding="utf-8")
    (out_dir / "edi_validation_harness_proof.svg").write_text(edi_svg, encoding="utf-8")
    (out_dir / "clearinghouse_responses_summary.json").write_text(json.dumps(clearinghouse_data, indent=2) + "\n", encoding="utf-8")
    (out_dir / "clearinghouse_responses_proof.svg").write_text(clearinghouse_svg, encoding="utf-8")
    (assets_dir / "app-shell-proof.svg").write_text(svg, encoding="utf-8")
    (assets_dir / "claims-pipeline-mapper-proof.svg").write_text(claims_svg, encoding="utf-8")
    (assets_dir / "rcm-dashboard-proof.svg").write_text(dashboard_svg, encoding="utf-8")
    (assets_dir / "edi-validation-harness-proof.svg").write_text(edi_svg, encoding="utf-8")
    (assets_dir / "clearinghouse-responses-proof.svg").write_text(clearinghouse_svg, encoding="utf-8")
    return summary


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Generate RevCycleMGMT app shell proof artifacts.")
    parser.add_argument("--out", default="output_demo")
    args = parser.parse_args(argv)
    summary = write_artifacts(Path(args.out))
    print(json.dumps({"artifact_count": 13, "readiness_score": summary["readiness_score"]}, indent=2))


if __name__ == "__main__":
    main()
