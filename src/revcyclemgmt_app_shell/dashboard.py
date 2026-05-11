"""RCM Dashboard KPI synthetic workspace model and rendering helpers."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from html import escape
import json


@dataclass(frozen=True)
class KpiCard:
    key: str
    label: str
    current: float
    target: float
    unit: str
    direction: str
    source_batch_date: date
    freshness_days: int
    definition: str
    owner: str

    @property
    def stale(self) -> bool:
        return (SYNTHETIC_AS_OF - self.source_batch_date).days > self.freshness_days

    @property
    def delta(self) -> float:
        return self.current - self.target

    @property
    def status(self) -> str:
        if self.direction == "higher":
            if self.current >= self.target:
                return "green"
            if self.current >= self.target - 0.02:
                return "amber"
            return "red"
        if self.current <= self.target:
            return "green"
        if self.unit == "days":
            return "amber" if self.current <= self.target + 3 else "red"
        return "amber" if self.current <= self.target + 0.02 else "red"


@dataclass(frozen=True)
class TrendPoint:
    week: str
    values: dict[str, float]


@dataclass(frozen=True)
class BreakdownRow:
    slice_name: str
    segment: str
    clean_claim_rate: float
    first_pass_yield: float
    denial_rate: float
    days_in_ar: float
    net_collection_rate: float
    volume: int
    dollars_at_risk: float
    owner: str
    action: str


@dataclass(frozen=True)
class DashboardActionItem:
    day_range: str
    action: str
    owner: str
    effort: str
    impact: str
    source: str


@dataclass(frozen=True)
class DashboardWorkspace:
    as_of: date
    freshness_days: int
    kpis: tuple[KpiCard, ...]
    trends: tuple[TrendPoint, ...]
    breakdowns: dict[str, tuple[BreakdownRow, ...]]
    action_plan: tuple[DashboardActionItem, ...]


SYNTHETIC_AS_OF = date(2026, 5, 11)
FRESHNESS_DAYS = 7

KPI_DEFINITIONS: tuple[tuple[str, str, float, float, str, str, date, str, str], ...] = (
    (
        "clean_claim_rate",
        "Clean claim rate",
        0.916,
        0.950,
        "percent",
        "higher",
        date(2026, 5, 9),
        "Clean claims divided by submitted synthetic claims.",
        "Biller",
    ),
    (
        "first_pass_yield",
        "First-pass yield",
        0.872,
        0.920,
        "percent",
        "higher",
        date(2026, 5, 9),
        "Synthetic claims accepted and adjudicated without rework on the first path.",
        "Biller",
    ),
    (
        "denial_rate",
        "Denial rate",
        0.043,
        0.030,
        "percent",
        "lower",
        date(2026, 5, 10),
        "Denied synthetic claims divided by adjudicated synthetic claims.",
        "Denials specialist",
    ),
    (
        "days_in_ar",
        "Days in A/R",
        38.4,
        30.0,
        "days",
        "lower",
        date(2026, 4, 30),
        "Average synthetic claim age before payment visibility or closure.",
        "A/R follow-up",
    ),
    (
        "net_collection_rate",
        "Net collection rate",
        0.934,
        0.970,
        "percent",
        "higher",
        date(2026, 5, 8),
        "Synthetic allowed collections divided by synthetic collectible revenue.",
        "Posting",
    ),
)


def build_dashboard_workspace() -> DashboardWorkspace:
    """Build the four-view RCM Dashboard KPI workspace."""

    kpis = tuple(
        KpiCard(
            key=key,
            label=label,
            current=current,
            target=target,
            unit=unit,
            direction=direction,
            source_batch_date=batch_date,
            freshness_days=FRESHNESS_DAYS,
            definition=definition,
            owner=owner,
        )
        for key, label, current, target, unit, direction, batch_date, definition, owner in KPI_DEFINITIONS
    )
    breakdowns = _build_breakdowns()
    return DashboardWorkspace(
        as_of=SYNTHETIC_AS_OF,
        freshness_days=FRESHNESS_DAYS,
        kpis=kpis,
        trends=_build_trends(kpis),
        breakdowns=breakdowns,
        action_plan=_build_action_plan(breakdowns),
    )


def _build_trends(kpis: tuple[KpiCard, ...]) -> tuple[TrendPoint, ...]:
    week_start = SYNTHETIC_AS_OF - timedelta(weeks=12)
    values = {
        "clean_claim_rate": (0.842, 0.916),
        "first_pass_yield": (0.791, 0.872),
        "denial_rate": (0.074, 0.043),
        "days_in_ar": (48.8, 38.4),
        "net_collection_rate": (0.887, 0.934),
    }
    points = []
    for index in range(13):
        progress = index / 12
        wave = ((index % 4) - 1.5) * 0.003
        point_values = {}
        for key, (start, end) in values.items():
            raw = start + ((end - start) * progress)
            if key == "days_in_ar":
                point_values[key] = round(raw - (wave * 80), 1)
            else:
                point_values[key] = round(raw + wave, 4)
        points.append(TrendPoint(week=(week_start + timedelta(weeks=index)).isoformat(), values=point_values))
    return tuple(points)


def _build_breakdowns() -> dict[str, tuple[BreakdownRow, ...]]:
    rows = (
        BreakdownRow("Payer", "Synthetic Payer B", 0.891, 0.812, 0.082, 45.6, 0.904, 147, 18200, "Denials specialist", "Pull authorization evidence before resubmission."),
        BreakdownRow("Payer", "Synthetic Payer D", 0.866, 0.798, 0.098, 49.1, 0.897, 82, 15300, "Coder", "Review documentation completeness before release."),
        BreakdownRow("Payer", "Synthetic Payer C", 0.917, 0.861, 0.052, 39.4, 0.928, 96, 7900, "Front desk", "Repair eligibility detail before next batch."),
        BreakdownRow("Payer", "Synthetic Payer A", 0.948, 0.913, 0.026, 27.8, 0.962, 188, 6400, "Posting", "Keep weekly variance audit active."),
        BreakdownRow("Payer", "Synthetic Payer E", 0.959, 0.921, 0.027, 25.9, 0.971, 74, 4100, "Posting", "Separate responsibility balances after remit posting."),
        BreakdownRow("CARC code", "CARC 16 synthetic", 0.844, 0.782, 0.121, 52.8, 0.884, 34, 11650, "Denials specialist", "Create missing-information packet checklist."),
        BreakdownRow("CARC code", "CO 45 synthetic", 0.903, 0.842, 0.065, 43.3, 0.911, 29, 9400, "Posting", "Review allowed-amount variance before closeout."),
        BreakdownRow("CARC code", "PR balance synthetic", 0.926, 0.879, 0.041, 36.7, 0.931, 27, 5400, "A/R follow-up", "Separate patient-balance communication lane."),
        BreakdownRow("CARC code", "Coverage synthetic", 0.872, 0.811, 0.088, 47.6, 0.902, 31, 8800, "Front desk", "Run coverage check script before claim build."),
        BreakdownRow("CARC code", "Clean remit synthetic", 0.963, 0.934, 0.018, 24.4, 0.976, 51, 2600, "Posting", "Keep post-remit variance review weekly."),
        BreakdownRow("Specialty", "Synthetic therapy launch", 0.902, 0.849, 0.061, 41.5, 0.921, 126, 12100, "Coder", "Tighten documentation readiness before charge release."),
        BreakdownRow("Specialty", "Synthetic behavioral launch", 0.884, 0.821, 0.074, 44.9, 0.909, 118, 13700, "Front desk", "Validate eligibility and authorization fields earlier."),
        BreakdownRow("Specialty", "Synthetic primary-care launch", 0.937, 0.892, 0.036, 32.4, 0.948, 163, 7100, "Biller", "Monitor clean-claim drift after weekly batches."),
        BreakdownRow("Specialty", "Synthetic specialty-care launch", 0.871, 0.804, 0.092, 48.6, 0.895, 88, 14950, "Denials specialist", "Split medical-necessity review from posting cleanup."),
        BreakdownRow("Claim type", "New visit synthetic", 0.901, 0.847, 0.064, 42.1, 0.918, 155, 12800, "Coder", "Review first-visit documentation before batch release."),
        BreakdownRow("Claim type", "Follow-up visit synthetic", 0.941, 0.899, 0.032, 29.8, 0.957, 214, 6200, "Biller", "Keep daily acceptance scan active."),
        BreakdownRow("Claim type", "Procedure add-on synthetic", 0.864, 0.793, 0.101, 50.2, 0.889, 69, 15100, "Coder", "Validate modifier and documentation readiness."),
        BreakdownRow("Claim type", "Responsibility balance synthetic", 0.919, 0.866, 0.046, 37.3, 0.929, 73, 7600, "A/R follow-up", "Separate follow-up queue from payment posting."),
    )
    grouped: dict[str, list[BreakdownRow]] = {}
    for row in rows:
        grouped.setdefault(row.slice_name, []).append(row)
    return {key: tuple(value) for key, value in grouped.items()}


def _risk_score(row: BreakdownRow) -> float:
    return (
        (1 - row.clean_claim_rate) * 120
        + (1 - row.first_pass_yield) * 150
        + row.denial_rate * 180
        + max(row.days_in_ar - 30, 0) * 2.2
        + (1 - row.net_collection_rate) * 130
        + row.dollars_at_risk / 900
    )


def worst_three(rows: tuple[BreakdownRow, ...]) -> tuple[BreakdownRow, ...]:
    """Return the three highest-risk rows within a breakdown slice."""

    return tuple(sorted(rows, key=_risk_score, reverse=True)[:3])


def _build_action_plan(breakdowns: dict[str, tuple[BreakdownRow, ...]]) -> tuple[DashboardActionItem, ...]:
    candidates = sorted(
        [row for rows in breakdowns.values() for row in worst_three(rows)],
        key=_risk_score,
        reverse=True,
    )
    unique: list[BreakdownRow] = []
    seen: set[str] = set()
    for row in candidates:
        if row.segment in seen:
            continue
        seen.add(row.segment)
        unique.append(row)
        if len(unique) == 6:
            break
    day_ranges = ("Days 1-3", "Days 4-7", "Days 8-12", "Days 13-18", "Days 19-24", "Days 25-30")
    effort = ("M", "M", "S", "L", "M", "S")
    impacts = (
        "Improve first-pass yield by 180-260 bps.",
        "Reduce denial pressure by 90-140 bps.",
        "Lower days in A/R by 2-4 days.",
        "Protect 220-310 bps of net collection rate.",
        "Cut aged synthetic exposure before month-end review.",
        "Keep weekly scorecard ownership from drifting.",
    )
    return tuple(
        DashboardActionItem(
            day_range=day_ranges[index],
            action=row.action,
            owner=row.owner,
            effort=effort[index],
            impact=impacts[index],
            source=f"{row.slice_name}: {row.segment}",
        )
        for index, row in enumerate(unique)
    )


def dashboard_summary(workspace: DashboardWorkspace | None = None) -> dict[str, object]:
    """Return a JSON-safe summary of the dashboard workspace."""

    ws = workspace or build_dashboard_workspace()
    return {
        "boundary": "synthetic-only",
        "as_of": ws.as_of.isoformat(),
        "freshness_days": ws.freshness_days,
        "headline_kpis": [
            {
                "key": kpi.key,
                "label": kpi.label,
                "current": kpi.current,
                "target": kpi.target,
                "unit": kpi.unit,
                "status": kpi.status,
                "stale": kpi.stale,
                "owner": kpi.owner,
                "definition": kpi.definition,
            }
            for kpi in ws.kpis
        ],
        "trends": [{"week": point.week, "values": point.values} for point in ws.trends],
        "breakdowns": {
            slice_name: [row.__dict__ for row in rows] for slice_name, rows in ws.breakdowns.items()
        },
        "worst_three": {
            slice_name: [row.__dict__ for row in worst_three(rows)] for slice_name, rows in ws.breakdowns.items()
        },
        "action_plan": [row.__dict__ for row in ws.action_plan],
    }


def pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def kpi_value(kpi: KpiCard | str, value: float | None = None, unit: str | None = None) -> str:
    if isinstance(kpi, KpiCard):
        if value is None:
            value = kpi.current
        if unit is None:
            unit = kpi.unit
    assert value is not None and unit is not None
    if unit == "percent":
        return pct(value)
    if unit == "days":
        return f"{value:.1f} days"
    return f"{value:.1f}"


def delta_label(kpi: KpiCard) -> str:
    delta = kpi.delta
    if kpi.unit == "percent":
        return f"{delta * 100:+.1f} pts vs target"
    if kpi.unit == "days":
        return f"{delta:+.1f} days vs target"
    return f"{delta:+.1f} vs target"


def dollars(value: float) -> str:
    return f"${value:,.0f}"


def esc(value: object) -> str:
    return escape(str(value), quote=True)


def _sparkline(values: list[float], x: int, y: int, width: int, height: int, lower_is_better: bool = False) -> str:
    low = min(values)
    high = max(values)
    span = high - low or 1
    step = width / max(len(values) - 1, 1)
    points = []
    for index, value in enumerate(values):
        px = x + index * step
        normalized = (value - low) / span
        py = y + height - (normalized * height)
        if lower_is_better:
            py = y + (normalized * height)
        points.append(f"{px:.1f},{py:.1f}")
    return " ".join(points)


def render_dashboard_svg(workspace: DashboardWorkspace | None = None) -> str:
    """Render the README proof SVG from the same data as the workspace route."""

    ws = workspace or build_dashboard_workspace()
    card_width = 218
    cards = []
    for index, kpi in enumerate(ws.kpis):
        x = 58 + index * (card_width + 16)
        cards.append(
            f'<rect x="{x}" y="174" width="{card_width}" height="142" rx="12" fill="#071316" stroke="{_status_color(kpi.status)}"/>'
            f'<text x="{x + 16}" y="202" class="kicker">{esc(kpi.label)}</text>'
            f'<text x="{x + 16}" y="244" class="metric">{esc(kpi_value(kpi))}</text>'
            f'<text x="{x + 16}" y="272" class="tiny">Target {esc(kpi_value(kpi, kpi.target, kpi.unit))}</text>'
            f'<text x="{x + 16}" y="296" class="tiny">{esc(delta_label(kpi))}</text>'
            f'<text x="{x + card_width - 16}" y="296" class="badge" text-anchor="end">{esc("STALE" if kpi.stale else "FRESH")}</text>'
        )

    trend_lines = []
    trend_labels = []
    trend_keys = [kpi.key for kpi in ws.kpis]
    colors = ["#00B3A4", "#7dd3d8", "#fb7185", "#facc15", "#a7f3d0"]
    for index, key in enumerate(trend_keys):
        values = [point.values[key] for point in ws.trends]
        lower_is_better = key in {"denial_rate", "days_in_ar"}
        points = _sparkline(values, 82, 382, 508, 148, lower_is_better=lower_is_better)
        trend_lines.append(f'<polyline points="{points}" fill="none" stroke="{colors[index]}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>')
        trend_labels.append(
            f'<circle cx="{646}" cy="{388 + index * 26}" r="5" fill="{colors[index]}"/>'
            f'<text x="660" y="{393 + index * 26}" class="tiny">{esc(next(k.label for k in ws.kpis if k.key == key))}</text>'
        )

    breakdown_panels = []
    y = 602
    for panel_index, (slice_name, rows) in enumerate(ws.breakdowns.items()):
        x = 58 + (panel_index % 2) * 594
        panel_y = y + (panel_index // 2) * 152
        breakdown_panels.append(
            f'<rect x="{x}" y="{panel_y}" width="562" height="128" rx="12" fill="#101b20" stroke="#21414a"/>'
            f'<text x="{x + 18}" y="{panel_y + 30}" class="kicker">{esc(slice_name)} worst three</text>'
        )
        row_y = panel_y + 56
        for row in worst_three(rows):
            breakdown_panels.append(
                f'<rect x="{x + 18}" y="{row_y - 20}" width="526" height="28" rx="7" fill="#071316" stroke="#31545c"/>'
                f'<text x="{x + 30}" y="{row_y}" class="small">{esc(row.segment)}</text>'
                f'<text x="{x + 328}" y="{row_y}" class="tiny">Denial {pct(row.denial_rate)} | A/R {row.days_in_ar:.1f}d</text>'
                f'<text x="{x + 508}" y="{row_y}" class="tiny" text-anchor="end">{dollars(row.dollars_at_risk)}</text>'
            )
            row_y += 32

    action_rows = []
    y = 390
    for item in ws.action_plan[:5]:
        action_rows.append(
            f'<rect x="790" y="{y}" width="406" height="46" rx="9" fill="#071316" stroke="#21414a"/>'
            f'<text x="808" y="{y + 18}" class="tiny strong">{esc(item.day_range)} | {esc(item.owner)} | {esc(item.effort)}</text>'
            f'<text x="808" y="{y + 36}" class="tiny">{esc(item.action[:66])}</text>'
        )
        y += 56

    ledger_rows = []
    y = 774
    for slice_name, rows in ws.breakdowns.items():
        ledger_rows.append(f'<text x="82" y="{y}" class="kicker">{esc(slice_name)} operating ledger</text>')
        y += 26
        for row in rows:
            callout = "worst-three" if row in worst_three(rows) else "monitor"
            ledger_rows.append(
                f'<rect x="82" y="{y - 18}" width="1116" height="25" rx="6" fill="#071316" stroke="#1f3941"/>'
                f'<text x="96" y="{y}" class="tiny strong">{esc(row.segment)}</text>'
                f'<text x="302" y="{y}" class="tiny">clean {pct(row.clean_claim_rate)} | first-pass {pct(row.first_pass_yield)} | denial {pct(row.denial_rate)}</text>'
                f'<text x="598" y="{y}" class="tiny">A/R {row.days_in_ar:.1f}d | net collect {pct(row.net_collection_rate)} | volume {row.volume}</text>'
                f'<text x="890" y="{y}" class="tiny">{dollars(row.dollars_at_risk)} synthetic | {esc(row.owner)}</text>'
                f'<text x="1184" y="{y}" class="tiny" text-anchor="end">{callout}</text>'
            )
            y += 31
        y += 12

    evidence = esc(json.dumps(dashboard_summary(ws), indent=2))

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="1600" viewBox="0 0 1280 1600" role="img" aria-labelledby="title desc">
  <title id="title">RevCycleMGMT RCM Dashboard KPI workspace proof</title>
  <desc id="desc">Synthetic four-view dashboard workspace: headline scorecard, 13-week trend, breakdowns, and 30-day action plan.</desc>
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
      .metric {{ font: 900 34px Inter, Arial, sans-serif; fill: #ffffff; }}
      .small {{ font: 800 14px Inter, Arial, sans-serif; fill: #f8fafc; }}
      .tiny {{ font: 650 12px Inter, Arial, sans-serif; fill: #cbd5e1; }}
      .strong {{ font-weight: 900; fill: #f8fafc; }}
      .badge {{ font: 900 10px Inter, Arial, sans-serif; fill: #facc15; letter-spacing: .08em; }}
    </style>
  </defs>
  <rect width="1280" height="1600" fill="url(#bg)"/>
  <rect x="28" y="28" width="1224" height="1544" rx="18" fill="#091316" stroke="#21414a"/>
  <text x="58" y="76" class="kicker">RCM Dashboard KPI Framework | Synthetic only</text>
  <text x="58" y="124" class="title">A clinic owner sees what to fix first.</text>
  <text x="58" y="154" class="subtitle">Headline KPIs, 13-week movement, breakdown risk, and a 30-day operating plan generated from one synthetic batch.</text>
  {''.join(cards)}
  <rect x="58" y="348" width="686" height="210" rx="14" fill="#101b20" stroke="#21414a"/>
  <text x="82" y="380" class="kicker">13-Week Trend</text>
  <path d="M82 530 H590 M82 493 H590 M82 456 H590 M82 419 H590 M82 382 H590" stroke="#1f3941" stroke-width="1"/>
  {''.join(trend_lines)}
  {''.join(trend_labels)}
  <rect x="774" y="348" width="446" height="320" rx="14" fill="#101b20" stroke="#21414a"/>
  <text x="798" y="380" class="kicker">30-Day Action Plan</text>
  {''.join(action_rows)}
  {''.join(breakdown_panels)}
  <rect x="58" y="696" width="1162" height="786" rx="14" fill="#101b20" stroke="#21414a"/>
  <text x="82" y="734" class="kicker">Full synthetic breakdown evidence</text>
  {''.join(ledger_rows)}
  <rect x="58" y="1526" width="1162" height="30" rx="15" fill="#00B3A4"/>
  <text x="640" y="1546" text-anchor="middle" fill="#021415" font-size="14" font-weight="900">All KPI values, payer labels, dates, dollar figures, and workqueue signals are synthetic demo data.</text>
</svg>"""


def _status_color(status: str) -> str:
    return {"green": "#00B3A4", "amber": "#facc15", "red": "#fb7185"}.get(status, "#21414a")
