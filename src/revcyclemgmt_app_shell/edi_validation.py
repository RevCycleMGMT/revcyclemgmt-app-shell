"""EDI Validation Harness synthetic workspace model and rendering helpers."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from html import escape
import json


ENVELOPE_SEGMENTS = ("ISA", "GS", "ST", "SE", "GE", "IEA")

TRANSACTION_RULES: dict[str, tuple[str, ...]] = {
    "837P": ("BHT", "NM1", "CLM", "LX", "SV1"),
    "837I": ("BHT", "NM1", "CLM", "LX", "SV2"),
    "835": ("BPR", "TRN", "CLP"),
    "999": ("AK1", "AK2", "IK5", "AK9"),
    "277CA": ("BHT", "HL", "TRN", "STC"),
    "270": ("BHT", "HL", "NM1", "EQ"),
    "271": ("BHT", "HL", "NM1", "EB"),
    "276": ("BHT", "HL", "NM1", "TRN"),
    "277": ("BHT", "HL", "NM1", "TRN", "STC"),
    "275": ("BGN", "NM1"),
}


@dataclass(frozen=True)
class Segment:
    tag: str
    elements: tuple[str, ...]
    ordinal: int

    def value(self, index: int, default: str = "") -> str:
        return self.elements[index] if len(self.elements) > index else default


@dataclass
class ValidationReport:
    valid: bool
    transaction_type: str | None
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    segment_count: int = 0
    control_numbers: dict[str, str] = field(default_factory=dict)
    required_segments: list[str] = field(default_factory=list)
    present_segments: dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class ClaimValidationRun:
    claim_id: str
    payer: str
    x12_text: str
    billed_amount: float
    business_rule_errors: tuple[str, ...] = ()
    category: str = "Ready"


@dataclass(frozen=True)
class ReadinessMetric:
    label: str
    count: int
    color: str


@dataclass(frozen=True)
class FailureCatalogEntry:
    name: str
    trigger: str
    fix: str
    frequency: int
    dollars_at_risk: float
    category: str
    owner: str
    evidence: str


@dataclass(frozen=True)
class PayerVarianceRow:
    payer: str
    auth_ref_g1: str
    dx_pointer_order: str
    cob_single_coverage: str
    rendering_taxonomy: str
    service_location: str
    note: str
    owner: str
    weekly_claims_at_risk: int
    weekly_dollars_at_risk: float


@dataclass(frozen=True)
class EdiActionItem:
    day_range: str
    action: str
    owner: str
    effort: str
    impact: str
    source: str


@dataclass(frozen=True)
class EdiValidationWorkspace:
    total_claims: int
    envelope_pass: int
    structure_pass: int
    business_rule_pass: int
    ready_to_submit: int
    failure_mix: tuple[ReadinessMetric, ...]
    validation_runs: tuple[ClaimValidationRun, ...]
    failure_catalog: tuple[FailureCatalogEntry, ...]
    payer_variance: tuple[PayerVarianceRow, ...]
    action_plan: tuple[EdiActionItem, ...]


def parse_x12_segments(x12_text: str) -> list[Segment]:
    """Parse X12 text into segments using the demo delimiters from the proof harness."""

    cleaned = x12_text.replace("\n", "").replace("\r", "").strip()
    raw_segments = [part.strip() for part in cleaned.split("~") if part.strip()]
    segments: list[Segment] = []
    for ordinal, raw in enumerate(raw_segments, start=1):
        parts = raw.split("*")
        tag = parts[0].strip().upper()
        elements = tuple(part.strip() for part in parts[1:])
        segments.append(Segment(tag=tag, elements=elements, ordinal=ordinal))
    return segments


def first_segment(segments: list[Segment], tag: str) -> Segment | None:
    tag = tag.upper()
    return next((segment for segment in segments if segment.tag == tag), None)


def all_segments(segments: list[Segment], tag: str) -> list[Segment]:
    tag = tag.upper()
    return [segment for segment in segments if segment.tag == tag]


def classify_transaction(st_code: str, segments_by_tag: dict[str, int]) -> str:
    """Return the transaction label using the proof-harness transaction rules."""

    if st_code == "837":
        return "837I" if segments_by_tag.get("SV2", 0) else "837P"
    if st_code == "277":
        return "277CA" if segments_by_tag.get("STC", 0) and not segments_by_tag.get("NM1", 0) else "277"
    return st_code


def validate_x12_text(x12_text: str) -> ValidationReport:
    segments = parse_x12_segments(x12_text)
    counts = _segment_counts(segments)
    controls = _control_numbers(segments)
    st = first_segment(segments, "ST")
    transaction_type = classify_transaction(st.value(0), counts) if st else None
    required_segments = list(ENVELOPE_SEGMENTS) + list(TRANSACTION_RULES.get(transaction_type or "", ()))
    report = ValidationReport(
        valid=False,
        transaction_type=transaction_type,
        segment_count=len(segments),
        control_numbers=controls,
        required_segments=required_segments,
        present_segments=counts,
    )
    if not segments:
        report.errors.append("No X12 segments found.")
        return report
    if not st:
        report.errors.append("Missing ST transaction set header.")
    for tag in ENVELOPE_SEGMENTS:
        if counts.get(tag, 0) == 0:
            report.errors.append(f"Missing required envelope segment {tag}.")
    if transaction_type not in TRANSACTION_RULES:
        report.errors.append(f"Unsupported or unrecognized transaction type: {transaction_type or 'unknown'}.")
    else:
        for tag in TRANSACTION_RULES[transaction_type]:
            if counts.get(tag, 0) == 0:
                report.errors.append(f"Missing required {transaction_type} segment {tag}.")
    if all_segments(segments, "CLM") and not (counts.get("SV1", 0) or counts.get("SV2", 0)):
        report.errors.append("Claim segment exists but no professional or institutional service line was found.")
    _validate_control_numbers(segments, report)
    report.valid = not report.errors
    return report


def build_edi_validation_workspace() -> EdiValidationWorkspace:
    """Build the four-view EDI Validation Harness workspace."""

    runs = _synthetic_validation_runs()
    catalog = _failure_catalog()
    payer_map = _payer_variance()
    total_claims = 487
    envelope_failures = 24
    structure_failures = 31
    business_failures = 20
    ready_to_submit = total_claims - envelope_failures - structure_failures - business_failures
    failure_mix = (
        ReadinessMetric("Ready to submit", ready_to_submit, "#00B3A4"),
        ReadinessMetric("Envelope repair", envelope_failures, "#facc15"),
        ReadinessMetric("Structure repair", structure_failures, "#fb7185"),
        ReadinessMetric("Business-rule repair", business_failures, "#7dd3d8"),
    )
    return EdiValidationWorkspace(
        total_claims=total_claims,
        envelope_pass=total_claims - envelope_failures,
        structure_pass=total_claims - envelope_failures - structure_failures,
        business_rule_pass=ready_to_submit,
        ready_to_submit=ready_to_submit,
        failure_mix=failure_mix,
        validation_runs=runs,
        failure_catalog=catalog,
        payer_variance=payer_map,
        action_plan=_build_action_plan(catalog, payer_map),
    )


def _synthetic_validation_runs() -> tuple[ClaimValidationRun, ...]:
    return (
        ClaimValidationRun("SYN-EDI-READY-001", "Synthetic Payer A", _x12_claim("0001"), 240.0),
        ClaimValidationRun("SYN-EDI-MISS-NM1-002", "Synthetic Payer B", _x12_claim("0002", include_rendering=False), 360.0, category="Structure repair"),
        ClaimValidationRun("SYN-EDI-MISS-SV1-003", "Synthetic Payer C", _x12_claim("0003", include_service=False), 185.0, category="Structure repair"),
        ClaimValidationRun("SYN-EDI-CTRL-004", "Synthetic Payer D", _x12_claim("0004", bad_control=True), 510.0, category="Envelope repair"),
        ClaimValidationRun("SYN-EDI-BIZ-005", "Synthetic Payer E", _x12_claim("0005"), 295.0, ("Authorization format missing for synthetic payer rule.",), "Business-rule repair"),
    )


def _x12_claim(
    control: str,
    *,
    include_rendering: bool = True,
    include_service: bool = True,
    bad_control: bool = False,
) -> str:
    segments = [
        f"ISA*00*          *00*          *ZZ*SYNTESTSENDER  *ZZ*SYNTESTRECVR   *260511*1200*^*00501*{control}*0*T*:~",
        f"GS*HC*SYNTESTSENDER*SYNTESTRECVR*20260511*1200*{control}*X*005010X222A1~",
        f"ST*837*{control}*005010X222A1~",
        "BHT*0019*00*SYNBATCH*20260511*1200*CH~",
        "NM1*41*2*SYNTHETIC SUBMITTER*****46*SYN-SUBMITTER~",
        "NM1*40*2*SYNTHETIC RECEIVER*****46*SYN-RECEIVER~",
        "NM1*85*2*SYNTHETIC BILLING GROUP*****XX*SYNPROVAA~",
    ]
    if include_rendering:
        segments.append("NM1*82*1*SYNRENDER*PROVIDER****XX*SYNPROVBB~")
    segments.extend(
        [
            f"CLM*SYNCLM{control}*240***11:B:1*Y*A*Y*Y~",
            "LX*1~",
        ]
    )
    if include_service:
        segments.append("SV1*HC:SYNPROC*240*UN*1***1~")
    se_control = "9999" if bad_control else control
    segments.extend(
        [
            f"SE*11*{se_control}~",
            f"GE*1*{control}~",
            f"IEA*1*{control}~",
        ]
    )
    return "".join(segments)


def _failure_catalog() -> tuple[FailureCatalogEntry, ...]:
    return (
        FailureCatalogEntry("Missing rendering provider record", "NM1 loop with rendering-provider role is absent.", "Assign rendering owner and complete provider record before release.", 21, 12600, "Structure repair", "Biller", "Missing required 837P segment NM1."),
        FailureCatalogEntry("Service line not attached", "Claim header exists but no SV1 professional service line is present.", "Hold the claim until charge capture attaches a service line.", 18, 9800, "Structure repair", "Coder", "Claim segment exists but no service line was found."),
        FailureCatalogEntry("Control numbers do not match", "Transaction control number disagrees between ST and SE.", "Regenerate the batch envelope before any payer route.", 15, 8400, "Envelope repair", "Biller", "ST02 does not match SE02 transaction set control number."),
        FailureCatalogEntry("Authorization reference missing", "Synthetic payer rule expects authorization evidence in REF G1.", "Front desk confirms authorization before claim build.", 14, 7600, "Business-rule repair", "Front desk", "REF*G1 synthetic payer requirement failed."),
        FailureCatalogEntry("Diagnosis pointer order failed", "Primary diagnosis pointer is not first on the service line.", "Coder reviews diagnosis ordering before the batch closes.", 12, 6900, "Business-rule repair", "Coder", "SV1 diagnosis pointer ordering failed."),
        FailureCatalogEntry("COB segment not allowed", "Single-coverage claim still carries coordination-of-benefits detail.", "Remove COB detail when the intake record shows single coverage.", 10, 5400, "Business-rule repair", "Biller", "COB segment disallowed for synthetic payer rule."),
        FailureCatalogEntry("Envelope closeout segment missing", "Batch has transaction content but no IEA closeout.", "Repair envelope generation and rerun validator.", 9, 5100, "Envelope repair", "Biller", "Missing required envelope segment IEA."),
        FailureCatalogEntry("Service location incomplete", "Claim lacks the service-location information required by payer rule.", "Front desk completes location field before claim release.", 8, 4200, "Business-rule repair", "Front desk", "Synthetic service-location rule failed."),
    )


def _payer_variance() -> tuple[PayerVarianceRow, ...]:
    return (
        PayerVarianceRow("Synthetic Payer A", "pass", "pass", "N-A", "pass", "fail", "Service location required before release.", "Front desk", 9, 4300),
        PayerVarianceRow("Synthetic Payer B", "N-A", "fail", "pass", "pass", "pass", "Diagnosis pointer order is the main blocker.", "Coder", 11, 6100),
        PayerVarianceRow("Synthetic Payer C", "pass", "pass", "fail", "N-A", "pass", "COB detail must be removed for single coverage.", "Biller", 7, 3600),
        PayerVarianceRow("Synthetic Payer D", "fail", "N-A", "pass", "pass", "pass", "Authorization reference format needs intake cleanup.", "Front desk", 13, 7200),
        PayerVarianceRow("Synthetic Payer E", "pass", "pass", "N-A", "fail", "pass", "Rendering taxonomy evidence needs review.", "Biller", 6, 3100),
    )


def _build_action_plan(
    catalog: tuple[FailureCatalogEntry, ...],
    payer_map: tuple[PayerVarianceRow, ...],
) -> tuple[EdiActionItem, ...]:
    worst_failures = sorted(catalog, key=lambda row: (row.frequency, row.dollars_at_risk), reverse=True)[:3]
    worst_payers = sorted(payer_map, key=lambda row: (row.weekly_claims_at_risk, row.weekly_dollars_at_risk), reverse=True)[:3]
    return (
        EdiActionItem("Days 1-3", worst_failures[0].fix, worst_failures[0].owner, "M", "Unblocks 14-18 synthetic claims per week and about $8K weekly exposure.", worst_failures[0].name),
        EdiActionItem("Days 4-7", worst_failures[1].fix, worst_failures[1].owner, "S", "Unblocks 10-14 synthetic claims per week and reduces service-line repair.", worst_failures[1].name),
        EdiActionItem("Days 8-12", worst_payers[0].note, worst_payers[0].owner, "M", f"Unblocks {worst_payers[0].weekly_claims_at_risk} synthetic claims per week and {dollars(worst_payers[0].weekly_dollars_at_risk)} weekly exposure.", worst_payers[0].payer),
        EdiActionItem("Days 13-18", worst_failures[2].fix, worst_failures[2].owner, "M", "Reduces envelope rework before the next batch is staged.", worst_failures[2].name),
        EdiActionItem("Days 19-24", worst_payers[1].note, worst_payers[1].owner, "S", f"Unblocks {worst_payers[1].weekly_claims_at_risk} synthetic claims per week.", worst_payers[1].payer),
        EdiActionItem("Days 25-30", worst_payers[2].note, worst_payers[2].owner, "S", f"Unblocks {worst_payers[2].weekly_claims_at_risk} synthetic claims per week.", worst_payers[2].payer),
    )


def edi_validation_summary(workspace: EdiValidationWorkspace | None = None) -> dict[str, object]:
    """Return a JSON-safe summary of the EDI workspace."""

    ws = workspace or build_edi_validation_workspace()
    return {
        "boundary": "synthetic-only",
        "ready_to_submit": ws.ready_to_submit,
        "total_claims": ws.total_claims,
        "envelope_pass": ws.envelope_pass,
        "structure_pass": ws.structure_pass,
        "business_rule_pass": ws.business_rule_pass,
        "failure_mix": [asdict(row) for row in ws.failure_mix],
        "validation_runs": [
            {
                "claim_id": run.claim_id,
                "payer": run.payer,
                "billed_amount": run.billed_amount,
                "category": run.category,
                "business_rule_errors": list(run.business_rule_errors),
                "validation_report": validate_x12_text(run.x12_text).to_dict(),
            }
            for run in ws.validation_runs
        ],
        "failure_catalog": [asdict(row) for row in ws.failure_catalog],
        "payer_variance": [asdict(row) for row in ws.payer_variance],
        "action_plan": [asdict(row) for row in ws.action_plan],
        "transaction_rules": {key: list(value) for key, value in TRANSACTION_RULES.items()},
    }


def render_edi_validation_svg(workspace: EdiValidationWorkspace | None = None) -> str:
    """Render the README proof SVG from the same data as the route."""

    ws = workspace or build_edi_validation_workspace()
    width = 1280
    ready_label = f"Ready to submit: {ws.ready_to_submit} of {ws.total_claims} synthetic claims"
    cards = [
        ("Total claims", str(ws.total_claims), "synthetic batch"),
        ("Envelope pass", str(ws.envelope_pass), "ISA/GS/ST/SE/GE/IEA"),
        ("Structure pass", str(ws.structure_pass), "837P required segments"),
        ("Rules pass", str(ws.business_rule_pass), "synthetic payer rules"),
    ]
    card_markup = []
    for index, (label, value, note) in enumerate(cards):
        x = 58 + index * 292
        card_markup.append(
            f'<rect x="{x}" y="178" width="268" height="108" rx="12" fill="#071316" stroke="#21414a"/>'
            f'<text x="{x + 18}" y="210" class="kicker">{esc(label)}</text>'
            f'<text x="{x + 18}" y="250" class="metric">{esc(value)}</text>'
            f'<text x="{x + 18}" y="274" class="tiny">{esc(note)}</text>'
        )

    total_width = 1080
    start_x = 100
    bar_parts = []
    offset = 0.0
    for item in ws.failure_mix:
        part_width = total_width * (item.count / ws.total_claims)
        bar_parts.append(
            f'<rect x="{start_x + offset:.1f}" y="336" width="{part_width:.1f}" height="38" fill="{item.color}"/>'
            f'<text x="{start_x + offset + 12:.1f}" y="361" fill="#031719" font-size="12" font-weight="900">{esc(item.label)} {item.count}</text>'
        )
        offset += part_width

    failures = []
    y = 456
    for entry in ws.failure_catalog:
        failures.append(
            f'<rect x="58" y="{y}" width="544" height="54" rx="8" fill="#071316" stroke="#21414a"/>'
            f'<text x="76" y="{y + 20}" class="small strong">{esc(entry.name)}</text>'
            f'<text x="76" y="{y + 40}" class="tiny">{entry.frequency} synthetic | {dollars(entry.dollars_at_risk)} at risk | {esc(entry.owner)}</text>'
        )
        y += 62

    payer_cells = []
    y = 468
    for row in ws.payer_variance:
        payer_cells.append(f'<text x="652" y="{y}" class="small strong">{esc(row.payer)}</text>')
        x = 840
        for value in (row.auth_ref_g1, row.dx_pointer_order, row.cob_single_coverage, row.rendering_taxonomy, row.service_location):
            color = {"pass": "#00B3A4", "fail": "#fb7185", "N-A": "#64748b"}[value]
            payer_cells.append(
                f'<rect x="{x}" y="{y - 18}" width="54" height="26" rx="6" fill="{color}"/>'
                f'<text x="{x + 27}" y="{y}" fill="#031719" font-size="11" font-weight="900" text-anchor="middle">{esc(value)}</text>'
            )
            x += 66
        y += 46

    actions = []
    y = 1010
    for item in ws.action_plan:
        actions.append(
            f'<rect x="58" y="{y}" width="1162" height="48" rx="9" fill="#071316" stroke="#21414a"/>'
            f'<text x="76" y="{y + 19}" class="tiny strong">{esc(item.day_range)} | {esc(item.owner)} | {esc(item.effort)} | {esc(item.source)}</text>'
            f'<text x="76" y="{y + 38}" class="tiny">{esc(item.action)} Impact: {esc(item.impact)}</text>'
        )
        y += 58

    evidence = esc(json.dumps(edi_validation_summary(ws), indent=2))
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="1420" viewBox="0 0 {width} 1420" role="img" aria-labelledby="title desc">
  <title id="title">RevCycleMGMT EDI Validation Harness proof</title>
  <desc id="desc">Synthetic four-view EDI validation workspace: submission readiness, failure catalog, payer variance map, and 30-day readiness plan.</desc>
  <metadata>{evidence}</metadata>
  <defs>
    <linearGradient id="bg" x1="0" x2="1" y1="0" y2="1">
      <stop stop-color="#071012" offset="0"/>
      <stop stop-color="#123238" offset="1"/>
    </linearGradient>
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
  <rect width="{width}" height="1420" fill="url(#bg)"/>
  <rect x="28" y="28" width="1224" height="1364" rx="18" fill="#091316" stroke="#21414a"/>
  <text x="58" y="76" class="kicker">EDI Validation Harness | Synthetic only</text>
  <text x="58" y="124" class="title">Catch batch defects before claims leave the building.</text>
  <text x="58" y="154" class="subtitle">{esc(ready_label)} with failure mix, repair catalog, payer variance, and owner-ready readiness plan.</text>
  {''.join(card_markup)}
  <rect x="58" y="314" width="1162" height="86" rx="14" fill="#101b20" stroke="#21414a"/>
  <text x="82" y="344" class="kicker">Submission Readiness Check</text>
  <rect x="{start_x}" y="336" width="{total_width}" height="38" rx="19" fill="#071316" stroke="#21414a"/>
  {''.join(bar_parts)}
  <rect x="58" y="428" width="564" height="540" rx="14" fill="#101b20" stroke="#21414a"/>
  <text x="76" y="460" class="kicker">Failure Catalog</text>
  {''.join(failures)}
  <rect x="638" y="428" width="582" height="320" rx="14" fill="#101b20" stroke="#21414a"/>
  <text x="656" y="460" class="kicker">Payer Variance Map</text>
  <text x="840" y="438" class="tiny">Auth</text><text x="906" y="438" class="tiny">Dx</text><text x="972" y="438" class="tiny">COB</text><text x="1038" y="438" class="tiny">Tax</text><text x="1104" y="438" class="tiny">Loc</text>
  {''.join(payer_cells)}
  <rect x="638" y="770" width="582" height="198" rx="14" fill="#101b20" stroke="#21414a"/>
  <text x="656" y="802" class="kicker">Validator Evidence</text>
  <text x="656" y="836" class="small">Rules reused from proof harness TRANSACTION_RULES.</text>
  <text x="656" y="864" class="tiny">837P required segments: BHT / NM1 / CLM / LX / SV1.</text>
  <text x="656" y="892" class="tiny">Envelope checks: ISA / GS / ST / SE / GE / IEA.</text>
  <text x="656" y="920" class="tiny">Business rules remain synthetic payer-specific rules.</text>
  <rect x="58" y="986" width="1162" height="396" rx="14" fill="#101b20" stroke="#21414a"/>
  <text x="76" y="1018" class="kicker">30-Day Readiness Plan</text>
  {''.join(actions)}
  <rect x="58" y="1350" width="1162" height="30" rx="15" fill="#00B3A4"/>
  <text x="640" y="1370" text-anchor="middle" fill="#021415" font-size="14" font-weight="900">All segment values, payer labels, claim IDs, dollar figures, and validation outcomes are synthetic demo data.</text>
</svg>"""


def _segment_counts(segments: list[Segment]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for segment in segments:
        counts[segment.tag] = counts.get(segment.tag, 0) + 1
    return counts


def _control_numbers(segments: list[Segment]) -> dict[str, str]:
    isa = first_segment(segments, "ISA")
    gs = first_segment(segments, "GS")
    st = first_segment(segments, "ST")
    se = first_segment(segments, "SE")
    ge = first_segment(segments, "GE")
    iea = first_segment(segments, "IEA")
    return {
        "isa13": isa.value(12) if isa else "",
        "iea02": iea.value(1) if iea else "",
        "gs06": gs.value(5) if gs else "",
        "ge02": ge.value(1) if ge else "",
        "st02": st.value(1) if st else "",
        "se02": se.value(1) if se else "",
    }


def _st_to_se_segment_count(segments: list[Segment]) -> int | None:
    st_index = next((idx for idx, segment in enumerate(segments) if segment.tag == "ST"), None)
    se_index = next((idx for idx, segment in enumerate(segments) if segment.tag == "SE"), None)
    if st_index is None or se_index is None or se_index < st_index:
        return None
    return se_index - st_index + 1


def _validate_control_numbers(segments: list[Segment], report: ValidationReport) -> None:
    controls = report.control_numbers
    if controls["isa13"] and controls["iea02"] and controls["isa13"] != controls["iea02"]:
        report.errors.append("ISA13 does not match IEA02 interchange control number.")
    if controls["gs06"] and controls["ge02"] and controls["gs06"] != controls["ge02"]:
        report.errors.append("GS06 does not match GE02 functional group control number.")
    if controls["st02"] and controls["se02"] and controls["st02"] != controls["se02"]:
        report.errors.append("ST02 does not match SE02 transaction set control number.")
    se = first_segment(segments, "SE")
    counted = _st_to_se_segment_count(segments)
    if se and counted is not None:
        declared = se.value(0)
        if declared.isdigit() and int(declared) != counted:
            report.errors.append(f"SE01 declares {declared} segments, but ST-to-SE count is {counted}.")
        elif not declared.isdigit():
            report.errors.append("SE01 segment count is not numeric.")


def dollars(value: float) -> str:
    return f"${value:,.0f}"


def esc(value: object) -> str:
    return escape(str(value), quote=True)
