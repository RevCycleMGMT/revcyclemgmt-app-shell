"""Clearinghouse Response Tracker synthetic workspace model and rendering helpers."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from html import escape
import json

from .edi_validation import TRANSACTION_RULES


@dataclass(frozen=True)
class ResponseEvent:
    stage: str
    timestamp: str
    status: str
    note: str


@dataclass(frozen=True)
class ClaimResponsePath:
    claim_id: str
    payer: str
    amount: float
    submitted_at: str
    current_state: str
    days_since_submission: int
    within_sla: bool
    events: tuple[ResponseEvent, ...]


@dataclass(frozen=True)
class StateMetric:
    label: str
    count: int
    color: str


@dataclass(frozen=True)
class ParserExample:
    response_type: str
    raw_segments: tuple[str, ...]
    interpretation: tuple[str, ...]
    frequency: int
    owner: str


@dataclass(frozen=True)
class StuckClaim:
    claim_id: str
    payer: str
    stuck_stage: str
    days_stuck: int
    dollar_exposure: float
    recommended_action: str
    owner: str


@dataclass(frozen=True)
class ClearinghouseActionItem:
    day_range: str
    action: str
    owner: str
    effort: str
    impact: str
    source: str


@dataclass(frozen=True)
class ClearinghouseResponsesWorkspace:
    total_claims: int
    acknowledged_within_sla: int
    timeline: tuple[ClaimResponsePath, ...]
    state_mix: tuple[StateMetric, ...]
    parser_examples: tuple[ParserExample, ...]
    stuck_inventory: tuple[StuckClaim, ...]
    action_plan: tuple[ClearinghouseActionItem, ...]
    transaction_rules: dict[str, tuple[str, ...]]


BASE_TIME = datetime(2026, 5, 11, 8, 0)


def build_clearinghouse_responses_workspace() -> ClearinghouseResponsesWorkspace:
    """Build the four-view Clearinghouse Response Tracker workspace."""

    timeline = _timeline()
    stuck = _stuck_inventory()
    parsers = _parser_examples()
    state_mix = _state_mix(timeline)
    return ClearinghouseResponsesWorkspace(
        total_claims=len(timeline),
        acknowledged_within_sla=sum(1 for claim in timeline if claim.within_sla),
        timeline=timeline,
        state_mix=state_mix,
        parser_examples=parsers,
        stuck_inventory=stuck,
        action_plan=_action_plan(stuck, parsers),
        transaction_rules={key: TRANSACTION_RULES[key] for key in ("999", "277CA", "277")},
    )


def _timeline() -> tuple[ClaimResponsePath, ...]:
    specs = (
        ("SYN-CH-001", "Synthetic Payer A", 240, "277-final-status", True, 2),
        ("SYN-CH-002", "Synthetic Payer B", 360, "clean-and-acknowledged", True, 1),
        ("SYN-CH-003", "Synthetic Payer C", 185, "999-rejected", False, 3),
        ("SYN-CH-004", "Synthetic Payer D", 510, "277CA-rejected", False, 5),
        ("SYN-CH-005", "Synthetic Payer E", 295, "277-pending", False, 12),
        ("SYN-CH-006", "Synthetic Payer A", 415, "277-final-status", True, 4),
        ("SYN-CH-007", "Synthetic Payer B", 225, "clean-and-acknowledged", True, 1),
        ("SYN-CH-008", "Synthetic Payer C", 690, "999-rejected", False, 2),
        ("SYN-CH-009", "Synthetic Payer D", 330, "277CA-rejected", False, 7),
        ("SYN-CH-010", "Synthetic Payer E", 455, "277-pending", False, 15),
        ("SYN-CH-011", "Synthetic Payer A", 175, "clean-and-acknowledged", True, 1),
        ("SYN-CH-012", "Synthetic Payer B", 820, "277-final-status", True, 6),
    )
    return tuple(_claim_path(*spec) for spec in specs)


def _claim_path(claim_id: str, payer: str, amount: float, state: str, within_sla: bool, age_days: int) -> ClaimResponsePath:
    submitted = BASE_TIME - timedelta(days=age_days)
    events = [
        ResponseEvent("Claim submitted", _stamp(submitted), "submitted", "Synthetic claim left the billing queue."),
    ]
    if state == "999-rejected":
        events.append(ResponseEvent("999 received", _stamp(submitted + timedelta(hours=8)), "rejected", "Functional acknowledgment rejected the transaction set."))
    else:
        events.append(ResponseEvent("999 received", _stamp(submitted + timedelta(hours=6)), "accepted", "Envelope and transaction set were accepted."))
    if state in {"277CA-rejected", "277-pending", "277-final-status", "clean-and-acknowledged"}:
        status = "rejected" if state == "277CA-rejected" else "accepted"
        events.append(ResponseEvent("277CA received", _stamp(submitted + timedelta(hours=30)), status, "Claim acknowledgment returned from the clearinghouse route."))
    if state in {"277-final-status", "clean-and-acknowledged"}:
        events.append(ResponseEvent("277 received", _stamp(submitted + timedelta(days=min(age_days, 5))), "final", "Synthetic payer status response is available."))
    return ClaimResponsePath(claim_id, payer, amount, _stamp(submitted), state, age_days, within_sla, tuple(events))


def _state_mix(timeline: tuple[ClaimResponsePath, ...]) -> tuple[StateMetric, ...]:
    colors = {
        "clean-and-acknowledged": "#00B3A4",
        "999-rejected": "#fb7185",
        "277CA-rejected": "#f97316",
        "277-pending": "#facc15",
        "277-final-status": "#7dd3d8",
    }
    return tuple(
        StateMetric(label, sum(1 for claim in timeline if claim.current_state == label), colors[label])
        for label in colors
    )


def _parser_examples() -> tuple[ParserExample, ...]:
    return (
        ParserExample(
            "999",
            ("AK1*HC*000001~", "AK2*837*0001~", "IK5*R*5~", "AK9*R*1*1*0~"),
            ("The functional group was received.", "The 837 transaction set was identified.", "The transaction set was rejected.", "The full functional group needs repair before resubmission."),
            5,
            "Biller",
        ),
        ParserExample(
            "277CA",
            ("STC*A3:21*20260511*U*240~", "TRN*2*SYN-CH-004~", "BHT*0085*08*SYN277CA~"),
            ("The claim reached the acknowledgment layer.", "The status category shows a rejected or unaccepted claim.", "The next action is fixing claim data, not waiting for payment."),
            4,
            "Biller",
        ),
        ParserExample(
            "277",
            ("STC*F1:65*20260511*WQ*455~", "TRN*2*SYN-CH-010~", "NM1*PR*2*SYNTHETIC PAYER*****PI*SYN-PAYER~"),
            ("The payer status response was received.", "The claim is still pending payer action.", "A/R follow-up should track the next response date."),
            6,
            "A/R follow-up",
        ),
    )


def _stuck_inventory() -> tuple[StuckClaim, ...]:
    return (
        StuckClaim("SYN-CH-013", "Synthetic Payer A", "No 999 within 24 hours", 2, 2200, "Confirm batch receipt and rerun 999 polling.", "Biller"),
        StuckClaim("SYN-CH-014", "Synthetic Payer C", "No 999 within 24 hours", 3, 1850, "Check submitter control log and resend if missing.", "Biller"),
        StuckClaim("SYN-CH-015", "Synthetic Payer D", "No 999 within 24 hours", 4, 4120, "Escalate missing acknowledgment before next batch.", "Biller"),
        StuckClaim("SYN-CH-016", "Synthetic Payer B", "No 277CA within 72 hours", 5, 3600, "Separate accepted 999 from missing claim acknowledgment queue.", "Biller"),
        StuckClaim("SYN-CH-017", "Synthetic Payer E", "No 277CA within 72 hours", 6, 2950, "Open clearinghouse status follow-up and owner note.", "A/R follow-up"),
        StuckClaim("SYN-CH-018", "Synthetic Payer A", "No 277CA within 72 hours", 7, 5400, "Reconcile submitted claims against accepted acknowledgment list.", "Biller"),
        StuckClaim("SYN-CH-019", "Synthetic Payer C", "No 277 within 14 days", 16, 6900, "Start payer-status follow-up cadence.", "A/R follow-up"),
        StuckClaim("SYN-CH-020", "Synthetic Payer E", "No 277 within 14 days", 18, 7800, "Move to aged status-response review queue.", "Denials specialist"),
        StuckClaim("SYN-CH-021", "Synthetic Payer D", "No 277 within 14 days", 21, 9100, "Escalate unresolved payer-status response lane.", "Denials specialist"),
    )


def _action_plan(stuck: tuple[StuckClaim, ...], parsers: tuple[ParserExample, ...]) -> tuple[ClearinghouseActionItem, ...]:
    worst = sorted(stuck, key=lambda row: (row.days_stuck, row.dollar_exposure), reverse=True)[:3]
    common = sorted(parsers, key=lambda row: row.frequency, reverse=True)
    return (
        ClearinghouseActionItem("Days 1-3", worst[0].recommended_action, worst[0].owner, "M", "Unblocks 8-12 synthetic claims per week and about $9K weekly exposure.", worst[0].stuck_stage),
        ClearinghouseActionItem("Days 4-7", common[0].interpretation[-1], common[0].owner, "S", "Reduces pending-status ambiguity before A/R follow-up starts.", common[0].response_type),
        ClearinghouseActionItem("Days 8-12", worst[1].recommended_action, worst[1].owner, "M", "Unblocks 6-10 synthetic claims per week.", worst[1].stuck_stage),
        ClearinghouseActionItem("Days 13-18", common[1].interpretation[-1], common[1].owner, "M", "Cuts rejected acknowledgment rework before it ages.", common[1].response_type),
        ClearinghouseActionItem("Days 19-24", worst[2].recommended_action, worst[2].owner, "S", "Protects about $5K of synthetic weekly exposure.", worst[2].stuck_stage),
        ClearinghouseActionItem("Days 25-30", "Review the weekly response tracker and reset SLA thresholds.", "A/R follow-up", "S", "Keeps stale response queues from becoming silent A/R.", "Tracker closeout"),
    )


def clearinghouse_responses_summary(workspace: ClearinghouseResponsesWorkspace | None = None) -> dict[str, object]:
    """Return a JSON-safe summary of the response tracker workspace."""

    ws = workspace or build_clearinghouse_responses_workspace()
    return {
        "boundary": "synthetic-only",
        "total_claims": ws.total_claims,
        "acknowledged_within_sla": ws.acknowledged_within_sla,
        "timeline": [asdict(row) for row in ws.timeline],
        "state_mix": [asdict(row) for row in ws.state_mix],
        "parser_examples": [asdict(row) for row in ws.parser_examples],
        "stuck_inventory": [asdict(row) for row in ws.stuck_inventory],
        "action_plan": [asdict(row) for row in ws.action_plan],
        "transaction_rules": {key: list(value) for key, value in ws.transaction_rules.items()},
    }


def render_clearinghouse_responses_svg(workspace: ClearinghouseResponsesWorkspace | None = None) -> str:
    """Render the README proof SVG from the same data as the route."""

    ws = workspace or build_clearinghouse_responses_workspace()
    headline = f"Synthetic claims tracking: {ws.acknowledged_within_sla} of {ws.total_claims} acknowledged within SLA"
    cards = [
        ("Timeline claims", str(ws.total_claims), "synthetic batch"),
        ("Within SLA", str(ws.acknowledged_within_sla), "acknowledged"),
        ("Parser examples", str(len(ws.parser_examples)), "999 / 277CA / 277"),
        ("Stuck rows", str(len(ws.stuck_inventory)), "owner-ready"),
    ]
    card_markup = []
    for index, (label, value, note) in enumerate(cards):
        x = 58 + index * 292
        card_markup.append(
            f'<rect x="{x}" y="176" width="268" height="106" rx="12" fill="#071316" stroke="#21414a"/>'
            f'<text x="{x + 18}" y="208" class="kicker">{esc(label)}</text>'
            f'<text x="{x + 18}" y="248" class="metric">{esc(value)}</text>'
            f'<text x="{x + 18}" y="272" class="tiny">{esc(note)}</text>'
        )
    total_width = 1080
    start_x = 100
    offset = 0.0
    bars = []
    for item in ws.state_mix:
        width = total_width * (item.count / ws.total_claims)
        bars.append(
            f'<rect x="{start_x + offset:.1f}" y="326" width="{width:.1f}" height="38" fill="{item.color}"/>'
            f'<text x="{start_x + offset + 8:.1f}" y="351" fill="#031719" font-size="11" font-weight="900">{esc(item.label)} {item.count}</text>'
        )
        offset += width
    timeline_rows = []
    y = 430
    for claim in ws.timeline[:12]:
        timeline_rows.append(
            f'<rect x="58" y="{y}" width="1162" height="32" rx="7" fill="#071316" stroke="#1f3941"/>'
            f'<text x="74" y="{y + 21}" class="tiny strong">{esc(claim.claim_id)}</text>'
            f'<text x="202" y="{y + 21}" class="tiny">{esc(claim.payer)}</text>'
            f'<text x="370" y="{y + 21}" class="tiny">{esc(claim.current_state)}</text>'
            f'<text x="570" y="{y + 21}" class="tiny">{claim.days_since_submission}d since submission</text>'
            f'<text x="770" y="{y + 21}" class="tiny">{dollars(claim.amount)} synthetic</text>'
            f'<text x="1188" y="{y + 21}" class="tiny" text-anchor="end">{"SLA" if claim.within_sla else "watch"}</text>'
        )
        y += 38
    parser_panels = []
    x = 58
    for parser in ws.parser_examples:
        raw = " ".join(parser.raw_segments)
        meaning = " ".join(parser.interpretation)
        parser_panels.append(
            f'<rect x="{x}" y="918" width="370" height="176" rx="12" fill="#101b20" stroke="#21414a"/>'
            f'<text x="{x + 18}" y="950" class="kicker">{esc(parser.response_type)} Parser</text>'
            f'<text x="{x + 18}" y="980" class="tiny">{esc(raw[:92])}</text>'
            f'<text x="{x + 18}" y="1010" class="small">{esc(meaning[:96])}</text>'
            f'<text x="{x + 18}" y="1062" class="tiny">Owner: {esc(parser.owner)} | Frequency: {parser.frequency}</text>'
        )
        x += 396
    stuck_rows = []
    y = 1148
    for row in ws.stuck_inventory[:6]:
        stuck_rows.append(
            f'<rect x="58" y="{y}" width="562" height="34" rx="7" fill="#071316" stroke="#21414a"/>'
            f'<text x="74" y="{y + 22}" class="tiny strong">{esc(row.claim_id)}</text>'
            f'<text x="178" y="{y + 22}" class="tiny">{esc(row.stuck_stage)}</text>'
            f'<text x="498" y="{y + 22}" class="tiny" text-anchor="end">{row.days_stuck}d</text>'
        )
        y += 40
    actions = []
    y = 1148
    for item in ws.action_plan[:6]:
        actions.append(
            f'<rect x="650" y="{y}" width="570" height="34" rx="7" fill="#071316" stroke="#21414a"/>'
            f'<text x="666" y="{y + 15}" class="tiny strong">{esc(item.day_range)} | {esc(item.owner)} | {esc(item.effort)}</text>'
            f'<text x="666" y="{y + 29}" class="tiny">{esc((item.action + " " + item.impact)[:92])}</text>'
        )
        y += 40
    evidence = esc(json.dumps(clearinghouse_responses_summary(ws), indent=2))
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="1460" viewBox="0 0 1280 1460" role="img" aria-labelledby="title desc">
  <title id="title">RevCycleMGMT Clearinghouse Response Tracker proof</title>
  <desc id="desc">Synthetic four-view response tracker: submission timeline, parser view, stuck inventory, and 30-day tracking plan.</desc>
  <metadata>{evidence}</metadata>
  <defs>
    <linearGradient id="bg" x1="0" x2="1" y1="0" y2="1"><stop stop-color="#071012" offset="0"/><stop stop-color="#123238" offset="1"/></linearGradient>
    <style>
      .title {{ font: 900 42px Inter, Arial, sans-serif; fill: #f8fafc; }}
      .subtitle {{ font: 600 17px Inter, Arial, sans-serif; fill: #cbd5e1; }}
      .kicker {{ font: 900 12px Inter, Arial, sans-serif; fill: #7dd3d8; letter-spacing: .12em; text-transform: uppercase; }}
      .metric {{ font: 900 38px Inter, Arial, sans-serif; fill: #ffffff; }}
      .small {{ font: 800 14px Inter, Arial, sans-serif; fill: #f8fafc; }}
      .tiny {{ font: 650 12px Inter, Arial, sans-serif; fill: #cbd5e1; }}
      .strong {{ font-weight: 900; fill: #f8fafc; }}
    </style>
  </defs>
  <rect width="1280" height="1460" fill="url(#bg)"/>
  <rect x="28" y="28" width="1224" height="1404" rx="18" fill="#091316" stroke="#21414a"/>
  <text x="58" y="76" class="kicker">Clearinghouse Response Tracker | Synthetic only</text>
  <text x="58" y="124" class="title">Know whether submitted claims are actually moving.</text>
  <text x="58" y="154" class="subtitle">{esc(headline)} across 999, 277CA, and 277 response stages.</text>
  {''.join(card_markup)}
  <rect x="58" y="304" width="1162" height="88" rx="14" fill="#101b20" stroke="#21414a"/>
  <text x="82" y="334" class="kicker">Submission Timeline</text>
  <rect x="{start_x}" y="326" width="{total_width}" height="38" rx="19" fill="#071316" stroke="#21414a"/>
  {''.join(bars)}
  <rect x="58" y="408" width="1162" height="482" rx="14" fill="#101b20" stroke="#21414a"/>
  <text x="82" y="440" class="kicker">Synthetic Claim Lifecycle Rows</text>
  {''.join(timeline_rows)}
  <rect x="58" y="900" width="1162" height="214" rx="14" fill="#101b20" stroke="#21414a"/>
  <text x="82" y="932" class="kicker">Response Parser View</text>
  {''.join(parser_panels)}
  <rect x="58" y="1128" width="562" height="276" rx="14" fill="#101b20" stroke="#21414a"/>
  <text x="82" y="1160" class="kicker">Stuck-in-Clearinghouse Inventory</text>
  {''.join(stuck_rows)}
  <rect x="650" y="1128" width="570" height="276" rx="14" fill="#101b20" stroke="#21414a"/>
  <text x="674" y="1160" class="kicker">30-Day Tracking Plan</text>
  {''.join(actions)}
  <rect x="58" y="1390" width="1162" height="30" rx="15" fill="#00B3A4"/>
  <text x="640" y="1410" text-anchor="middle" fill="#021415" font-size="14" font-weight="900">All claim IDs, payer labels, segment values, dates, dollar figures, response timestamps, and status codes are synthetic demo data.</text>
</svg>"""


def _stamp(value: datetime) -> str:
    return value.strftime("%Y-%m-%d %H:%M")


def dollars(value: float) -> str:
    return f"${value:,.0f}"


def esc(value: object) -> str:
    return escape(str(value), quote=True)
