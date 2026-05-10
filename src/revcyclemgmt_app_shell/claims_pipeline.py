"""Claims Pipeline Mapper synthetic workspace model and rendering helpers."""

from __future__ import annotations

from dataclasses import dataclass
from html import escape
from typing import Iterable


@dataclass(frozen=True)
class TimelineNode:
    stage: str
    status: str
    elapsed_days: int
    owner: str


@dataclass(frozen=True)
class ClaimPath:
    slug: str
    label: str
    summary: str
    claim_id: str
    billed_amount: float
    dollars_at_risk: float
    current_status: str
    nodes: tuple[TimelineNode, ...]


@dataclass(frozen=True)
class OwnershipRow:
    stage: str
    owner: str
    role: str
    queue_load: int
    unassigned: int
    note: str


@dataclass(frozen=True)
class StuckPoint:
    group: str
    stuck_at: str
    count: int
    aged_days: int
    dollars_at_risk: float
    action: str


@dataclass(frozen=True)
class ActionPlanItem:
    day_range: str
    action: str
    owner: str
    effort: str
    impact: str


@dataclass(frozen=True)
class ClaimsPipelineWorkspace:
    selected_path: ClaimPath
    paths: tuple[ClaimPath, ...]
    ownership: tuple[OwnershipRow, ...]
    stuck_points: tuple[StuckPoint, ...]
    action_plan: tuple[ActionPlanItem, ...]


STAGES = (
    "Eligibility check",
    "Charge capture",
    "Coding",
    "837P submission",
    "999 acknowledgment",
    "277CA acceptance",
    "835 remit",
    "Payment posting",
)


def _nodes(statuses: Iterable[tuple[str, int, str]]) -> tuple[TimelineNode, ...]:
    owners = (
        "Front desk",
        "Clinical ops",
        "Coder",
        "Biller",
        "Biller",
        "AR follow-up",
        "Posting",
        "Posting",
    )
    return tuple(
        TimelineNode(stage=stage, status=status, elapsed_days=days, owner=owner)
        for stage, (status, days, owner) in zip(STAGES, statuses, strict=True)
    )


CLAIM_PATHS: tuple[ClaimPath, ...] = (
    ClaimPath(
        slug="clean",
        label="Clean claim",
        summary="Synthetic claim moves from eligibility through remit and posting without rework.",
        claim_id="SYN-CLM-CLEAN-001",
        billed_amount=185.0,
        dollars_at_risk=0.0,
        current_status="paid",
        nodes=_nodes(
            (
                ("paid", 0, "Front desk"),
                ("paid", 0, "Clinical ops"),
                ("paid", 1, "Coder"),
                ("paid", 1, "Biller"),
                ("paid", 1, "Biller"),
                ("paid", 2, "AR follow-up"),
                ("paid", 5, "Posting"),
                ("paid", 5, "Posting"),
            )
        ),
    ),
    ClaimPath(
        slug="rejected-at-999",
        label="Rejected at 999",
        summary="Synthetic implementation acknowledgment catches a missing service-line control before payer acceptance.",
        claim_id="SYN-CLM-999-002",
        billed_amount=220.0,
        dollars_at_risk=220.0,
        current_status="stuck",
        nodes=_nodes(
            (
                ("paid", 0, "Front desk"),
                ("paid", 0, "Clinical ops"),
                ("paid", 1, "Coder"),
                ("paid", 1, "Biller"),
                ("stuck", 3, "Biller"),
                ("in-flight", 0, "AR follow-up"),
                ("in-flight", 0, "Posting"),
                ("in-flight", 0, "Posting"),
            )
        ),
    ),
    ClaimPath(
        slug="denied-carc-16",
        label="Denied CARC 16",
        summary="Synthetic payer denial routes missing-information cleanup to an owner-ready appeal queue.",
        claim_id="SYN-CLM-DENIAL-003",
        billed_amount=300.0,
        dollars_at_risk=300.0,
        current_status="denied",
        nodes=_nodes(
            (
                ("paid", 0, "Front desk"),
                ("paid", 0, "Clinical ops"),
                ("paid", 1, "Coder"),
                ("paid", 1, "Biller"),
                ("paid", 1, "Biller"),
                ("paid", 2, "AR follow-up"),
                ("denied", 9, "Denials specialist"),
                ("stuck", 9, "Denials specialist"),
            )
        ),
    ),
    ClaimPath(
        slug="partial-pay-co-45",
        label="Partial pay CO-45",
        summary="Synthetic remit variance shows allowed-amount pressure before it becomes unresolved A/R.",
        claim_id="SYN-CLM-PARTIAL-004",
        billed_amount=640.0,
        dollars_at_risk=165.0,
        current_status="stuck",
        nodes=_nodes(
            (
                ("paid", 0, "Front desk"),
                ("paid", 0, "Clinical ops"),
                ("paid", 1, "Coder"),
                ("paid", 1, "Biller"),
                ("paid", 1, "Biller"),
                ("paid", 2, "AR follow-up"),
                ("stuck", 11, "Posting"),
                ("stuck", 12, "Posting"),
            )
        ),
    ),
    ClaimPath(
        slug="patient-responsibility-balance",
        label="Patient responsibility balance",
        summary="Synthetic responsibility balance separates posting work from follow-up communication.",
        claim_id="SYN-CLM-PR-005",
        billed_amount=410.0,
        dollars_at_risk=97.0,
        current_status="in-flight",
        nodes=_nodes(
            (
                ("paid", 0, "Front desk"),
                ("paid", 0, "Clinical ops"),
                ("paid", 1, "Coder"),
                ("paid", 1, "Biller"),
                ("paid", 1, "Biller"),
                ("paid", 2, "AR follow-up"),
                ("in-flight", 7, "Posting"),
                ("stuck", 8, "Unassigned"),
            )
        ),
    ),
)


OWNERSHIP_ROWS: tuple[OwnershipRow, ...] = (
    OwnershipRow("Eligibility check", "Front desk", "Front-end intake", 36, 0, "Verify coverage category before service."),
    OwnershipRow("Charge capture", "Clinical ops", "Visit closeout", 18, 2, "Close same-day charge gaps."),
    OwnershipRow("Coding", "Coder", "Coding readiness", 27, 0, "Review documentation and modifier prompts."),
    OwnershipRow("837P submission", "Biller", "Claim build", 42, 0, "Submit clean synthetic batches."),
    OwnershipRow("999 acknowledgment", "Biller", "Implementation response", 11, 3, "Assign reject repair ownership."),
    OwnershipRow("277CA acceptance", "AR follow-up", "Payer acceptance", 14, 1, "Separate payer rejects from waiting claims."),
    OwnershipRow("835 remit", "Posting", "ERA review", 24, 0, "Match remit and variance rows."),
    OwnershipRow("Payment posting", "Unassigned", "Balance follow-up", 9, 5, "Name owner before launch volume grows."),
)


STUCK_POINTS: tuple[StuckPoint, ...] = (
    StuckPoint("Eligibility mismatch", "Eligibility check", 18, 6, 4860.0, "Run front-desk coverage script and retry before claim build."),
    StuckPoint("Missing documentation", "Coding", 11, 8, 3375.0, "Create coder-owned note completion queue."),
    StuckPoint("999 reject", "999 acknowledgment", 7, 3, 1540.0, "Repair implementation errors and resubmit same week."),
    StuckPoint("277CA reject", "277CA acceptance", 9, 5, 2610.0, "Separate payer-accepted claims from payer-rejected claims."),
    StuckPoint("Denial pending appeal", "835 remit", 13, 14, 6820.0, "Build denial packet queue with due dates."),
    StuckPoint("No-response payer", "277CA acceptance", 16, 12, 5520.0, "Start payer follow-up cadence and owner log."),
    StuckPoint("Posting backlog", "Payment posting", 21, 9, 4185.0, "Clear remit posting backlog before new batch submission."),
)


ACTION_PLAN: tuple[ActionPlanItem, ...] = (
    ActionPlanItem("Days 1-3", "Name one accountable owner for every unassigned stage.", "Operations lead", "Low", "Stops claims from aging without a queue owner."),
    ActionPlanItem("Days 4-7", "Stand up daily 999 and 277CA review for rejected synthetic cohorts.", "Biller", "Medium", "Cuts front-end rework before payer follow-up starts."),
    ActionPlanItem("Days 8-12", "Create coding-readiness checklist for missing documentation cohorts.", "Coder", "Medium", "Reduces CARC 16-style denial exposure."),
    ActionPlanItem("Days 13-18", "Build denial and remit variance workqueues by owner, age, and dollars at risk.", "Denials specialist", "Medium", "Turns backlog into recoverable work."),
    ActionPlanItem("Days 19-24", "Install posting cadence for 835 matchback and responsibility balance separation.", "Posting", "Medium", "Prevents cash and patient-balance confusion."),
    ActionPlanItem("Days 25-30", "Review the first synthetic operating dashboard and update weekly controls.", "AR follow-up", "Low", "Makes week-two operations measurable."),
)


def get_claim_path(slug: str | None = None) -> ClaimPath:
    """Return the selected synthetic claim path."""

    if slug:
        for path in CLAIM_PATHS:
            if path.slug == slug:
                return path
    return CLAIM_PATHS[0]


def build_claims_pipeline_workspace(slug: str | None = None) -> ClaimsPipelineWorkspace:
    """Build the four-view Claims Pipeline Mapper workspace."""

    return ClaimsPipelineWorkspace(
        selected_path=get_claim_path(slug),
        paths=CLAIM_PATHS,
        ownership=OWNERSHIP_ROWS,
        stuck_points=STUCK_POINTS,
        action_plan=ACTION_PLAN,
    )


def claims_pipeline_summary(workspace: ClaimsPipelineWorkspace | None = None) -> dict[str, object]:
    """Return a JSON-safe summary of the mapper data."""

    ws = workspace or build_claims_pipeline_workspace()
    return {
        "boundary": "synthetic-only",
        "selected_path": ws.selected_path.slug,
        "sample_paths": [path.slug for path in ws.paths],
        "timeline_nodes": [node.__dict__ for node in ws.selected_path.nodes],
        "ownership_rows": [row.__dict__ for row in ws.ownership],
        "stuck_points": [row.__dict__ for row in ws.stuck_points],
        "action_plan": [row.__dict__ for row in ws.action_plan],
        "synthetic_dollars_at_risk": sum(row.dollars_at_risk for row in ws.stuck_points),
    }


def esc(value: object) -> str:
    return escape(str(value), quote=True)


def dollars(value: float) -> str:
    return f"${value:,.0f}"


def render_claims_pipeline_svg(workspace: ClaimsPipelineWorkspace | None = None) -> str:
    """Render the README proof SVG from the same data as the workspace route."""

    ws = workspace or build_claims_pipeline_workspace("denied-carc-16")
    status_colors = {
        "paid": "#00B3A4",
        "in-flight": "#7dd3d8",
        "stuck": "#facc15",
        "denied": "#fb7185",
    }
    timeline = []
    x = 80
    for index, node in enumerate(ws.selected_path.nodes, start=1):
        color = status_colors.get(node.status, "#94a3b8")
        if index > 1:
            timeline.append(f'<path d="M{x - 98} 238 L{x - 28} 238" stroke="#31545c" stroke-width="5" stroke-linecap="round"/>')
        timeline.append(
            f'<circle cx="{x}" cy="238" r="24" fill="{color}"/>'
            f'<text x="{x}" y="244" class="node" text-anchor="middle">{index}</text>'
            f'<text x="{x - 42}" y="286" class="tiny strong">{esc(node.stage)}</text>'
            f'<text x="{x - 42}" y="305" class="tiny">{esc(node.status)} | {node.elapsed_days}d</text>'
            f'<text x="{x - 42}" y="324" class="tiny">{esc(node.owner)}</text>'
        )
        x += 148

    owners = []
    y = 386
    for row in ws.ownership[:5]:
        loud = row.unassigned > 0 or row.owner == "Unassigned"
        stroke = "#fb7185" if loud else "#21414a"
        fill = "#1b1014" if loud else "#071316"
        owners.append(
            f'<rect x="58" y="{y}" width="330" height="42" rx="8" fill="{fill}" stroke="{stroke}"/>'
            f'<text x="74" y="{y + 25}" class="small">{esc(row.stage)}</text>'
            f'<text x="246" y="{y + 25}" class="small strong">{esc(row.owner)}</text>'
            f'<text x="354" y="{y + 25}" class="small">{row.queue_load}</text>'
        )
        y += 52

    stuck_rows = []
    y = 386
    for row in ws.stuck_points[:5]:
        stuck_rows.append(
            f'<rect x="420" y="{y}" width="390" height="42" rx="8" fill="#071316" stroke="#21414a"/>'
            f'<text x="436" y="{y + 25}" class="small strong">{esc(row.group)}</text>'
            f'<text x="620" y="{y + 25}" class="small">{row.count} | {row.aged_days}d</text>'
            f'<text x="724" y="{y + 25}" class="small">{dollars(row.dollars_at_risk)}</text>'
        )
        y += 52

    actions = []
    y = 386
    for item in ws.action_plan[:5]:
        actions.append(
            f'<rect x="842" y="{y}" width="372" height="42" rx="8" fill="#071316" stroke="#21414a"/>'
            f'<text x="858" y="{y + 18}" class="tiny strong">{esc(item.day_range)} | {esc(item.owner)} | {esc(item.effort)}</text>'
            f'<text x="858" y="{y + 34}" class="tiny">{esc(item.action[:72])}</text>'
        )
        y += 52

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="780" viewBox="0 0 1280 780" role="img" aria-labelledby="title desc">
  <title id="title">RevCycleMGMT Claims Pipeline Mapper proof</title>
  <desc id="desc">Synthetic four-view claims pipeline workspace: timeline, ownership map, stuck-point inventory, and first 30-day action plan.</desc>
  <defs>
    <linearGradient id="bg" x1="0" x2="1" y1="0" y2="1">
      <stop stop-color="#071012" offset="0"/>
      <stop stop-color="#13343a" offset="1"/>
    </linearGradient>
    <style>
      .title {{ font: 900 42px Inter, Arial, sans-serif; fill: #f8fafc; }}
      .subtitle {{ font: 600 17px Inter, Arial, sans-serif; fill: #cbd5e1; }}
      .kicker {{ font: 900 12px Inter, Arial, sans-serif; fill: #7dd3d8; letter-spacing: .12em; text-transform: uppercase; }}
      .metric {{ font: 900 30px Inter, Arial, sans-serif; fill: #ffffff; }}
      .small {{ font: 700 14px Inter, Arial, sans-serif; fill: #d9fffd; }}
      .tiny {{ font: 600 12px Inter, Arial, sans-serif; fill: #cbd5e1; }}
      .strong {{ font-weight: 900; fill: #f8fafc; }}
      .node {{ font: 900 17px Inter, Arial, sans-serif; fill: #031719; }}
    </style>
  </defs>
  <rect width="1280" height="780" fill="url(#bg)"/>
  <rect x="28" y="28" width="1224" height="724" rx="18" fill="#091316" stroke="#21414a"/>
  <text x="58" y="76" class="kicker">Claims Pipeline Mapper | Synthetic only</text>
  <text x="58" y="124" class="title">See where claims move, stall, and need owners.</text>
  <text x="58" y="154" class="subtitle">Four production-style views generated from synthetic claim paths: timeline, ownership, stuck points, and first 30-day operating plan.</text>
  <rect x="58" y="178" width="1162" height="172" rx="14" fill="#101b20" stroke="#21414a"/>
  <text x="80" y="210" class="kicker">Claim Path Timeline: {esc(ws.selected_path.label)}</text>
  {''.join(timeline)}
  <rect x="58" y="366" width="330" height="318" rx="14" fill="#101b20" stroke="#21414a"/>
  <text x="74" y="396" class="kicker">Ownership Map</text>
  {''.join(owners)}
  <rect x="420" y="366" width="390" height="318" rx="14" fill="#101b20" stroke="#21414a"/>
  <text x="436" y="396" class="kicker">Stuck-Point Inventory</text>
  {''.join(stuck_rows)}
  <rect x="842" y="366" width="372" height="318" rx="14" fill="#101b20" stroke="#21414a"/>
  <text x="858" y="396" class="kicker">First 30-Day Action Plan</text>
  {''.join(actions)}
  <rect x="58" y="704" width="1162" height="30" rx="15" fill="#00B3A4"/>
  <text x="640" y="724" text-anchor="middle" fill="#021415" font-size="14" font-weight="900">All IDs, payer labels, dollar figures, and claim events are synthetic demo data.</text>
</svg>"""
