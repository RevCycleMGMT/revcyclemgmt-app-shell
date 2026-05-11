"""HTML rendering for the local app shell proof."""

from __future__ import annotations

from html import escape
from urllib.parse import parse_qs

from .claims_pipeline import build_claims_pipeline_workspace, dollars
from .clearinghouse_responses import build_clearinghouse_responses_workspace
from .dashboard import (
    build_dashboard_workspace,
    delta_label,
    kpi_value,
    pct as dashboard_pct,
    worst_three,
)
from .edi_validation import build_edi_validation_workspace
from .data import PLACEHOLDER_COPY, ROADMAP_MODULES
from .privacy import PrivacyBoundaryError
from .workspace import build_workspace


ROUTES = {
    "/": "launch-workspace",
    "/app/overview": "launch-workspace",
    "/app/intake": "launch-workspace",
    "/app/launch-workspace": "launch-workspace",
    "/app/claims-pipeline": "claims-pipeline",
    "/app/dashboard": "dashboard",
    "/app/edi-validation": "edi-validation",
    "/app/coding-readiness": "coding-readiness",
    "/app/clearinghouse-responses": "clearinghouse-responses",
    "/app/835-matchback": "835-matchback",
    "/app/denial-workqueues": "denial-workqueues",
    "/app/evidence": "evidence",
    "/app/site-qa": "site-qa",
}


def route_statuses() -> dict[str, int]:
    return {route: 200 for route in ROUTES}


def render_route(path: str = "/", query: str = "") -> tuple[int, str, str]:
    slug = ROUTES.get(path)
    if slug is None:
        return 404, "text/html; charset=utf-8", render_page("not-found", "<h1>Route not found</h1>")
    params = {key: values[-1] for key, values in parse_qs(query).items()}
    try:
        body = (
            render_launch(params)
            if slug == "launch-workspace"
            else render_claims_pipeline(params)
            if slug == "claims-pipeline"
            else render_dashboard()
            if slug == "dashboard"
            else render_edi_validation()
            if slug == "edi-validation"
            else render_clearinghouse_responses()
            if slug == "clearinghouse-responses"
            else render_placeholder(slug)
        )
        return 200, "text/html; charset=utf-8", render_page(slug, body)
    except PrivacyBoundaryError as exc:
        body = f"""
        <section class="panel alert">
          <p class="eyebrow">Synthetic boundary</p>
          <h1>Input rejected</h1>
          <p>{escape(str(exc))}</p>
          <a class="button" href="/app/intake">Return to safe intake</a>
        </section>
        """
        return 422, "text/html; charset=utf-8", render_page(slug, body)


def render_page(active_slug: str, body: str) -> str:
    titles = {
        "launch-workspace": "App Shell + Launch Workspace",
        "claims-pipeline": "Claims Pipeline Mapper",
        "dashboard": "RCM Dashboard KPI Workspace",
        "edi-validation": "EDI Validation Harness",
        "clearinghouse-responses": "Clearinghouse Response Tracker",
    }
    page_title = titles.get(active_slug, "Roadmap Module")
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>RevCycleMGMT App Shell</title>
  <style>{CSS}</style>
</head>
<body>
  <aside class="sidebar">
    <div class="brand">RevCycleMGMT</div>
    <div class="env">No-PHI Launch Workspace</div>
    <nav>{render_nav(active_slug)}</nav>
  </aside>
  <main class="shell">
    <header class="topbar">
      <div>
        <p class="eyebrow">Revenue infrastructure for independent healthcare practices</p>
        <h1>{escape(page_title)}</h1>
      </div>
      <div class="status">Synthetic only</div>
    </header>
    {body}
  </main>
</body>
</html>"""


def render_nav(active_slug: str) -> str:
    links = []
    route_map = {
        "launch-workspace": "/app/intake",
        "claims-pipeline": "/app/claims-pipeline",
        "dashboard": "/app/dashboard",
        "edi-validation": "/app/edi-validation",
        "coding-readiness": "/app/coding-readiness",
        "clearinghouse-responses": "/app/clearinghouse-responses",
        "835-matchback": "/app/835-matchback",
        "denial-workqueues": "/app/denial-workqueues",
        "evidence": "/app/evidence",
        "site-qa": "/app/site-qa",
    }
    for module in ROADMAP_MODULES:
        active = "active" if module["slug"] == active_slug else ""
        links.append(
            f'<a class="{active}" href="{route_map[module["slug"]]}"><span>{escape(module["label"])}</span><small>{escape(module["status"])}</small></a>'
        )
    return "\n".join(links)


def render_launch(params: dict[str, str]) -> str:
    workspace = build_workspace(params)
    intake = workspace.intake
    checklist = "".join(f"<li>{escape(item)}</li>" for item in workspace.checklist)
    journey = "".join(
        "<tr>"
        f"<td>{escape(row['claim_id'])}</td><td>{escape(row['stage'])}</td><td>{escape(row['ack'])}</td>"
        f"<td>{escape(row['status'])}</td><td>{escape(row['remit'])}</td><td>{escape(row['owner'])}</td>"
        "</tr>"
        for row in workspace.claims_journey
    )
    return f"""
    <section class="grid hero-grid">
      <div class="panel intake">
        <p class="eyebrow">Live intake</p>
        <h2>No-PHI startup-clinic launch intake</h2>
        <form method="get" action="/app/intake">
          {input_field("organization_name", "Organization", intake["organization_name"])}
          {input_field("specialty", "Specialty", intake["specialty"])}
          {input_field("ehr", "EHR/PM", intake["ehr"])}
          {input_field("clearinghouse_intent", "Routing intent", intake["clearinghouse_intent"])}
          {input_field("payer_mix", "Payer mix", intake["payer_mix"])}
          {input_field("monthly_claim_volume", "Monthly claim volume", intake["monthly_claim_volume"])}
          {input_field("launch_timing", "Launch timing", intake["launch_timing"])}
          {input_field("denial_focus", "Denial focus", intake["denial_focus"])}
          <button type="submit">Generate workspace</button>
        </form>
      </div>
      <div class="panel score">
        <p class="eyebrow">Generated workspace</p>
        <div class="score-ring">{workspace.readiness_score}</div>
        <h2>{escape(workspace.first_build)}</h2>
        <p>Recommended module: <strong>{escape(workspace.recommended_module)}</strong></p>
        <ol>{checklist}</ol>
      </div>
    </section>
    <section class="panel">
      <p class="eyebrow">Synthetic claims journey preview</p>
      <h2>Claims movement pulled into the Launch Workspace</h2>
      <table>
        <thead><tr><th>Claim</th><th>Stage</th><th>999</th><th>Status</th><th>835</th><th>Owner</th></tr></thead>
        <tbody>{journey}</tbody>
      </table>
    </section>
    """


def input_field(name: str, label: str, value: str) -> str:
    return f'<label>{escape(label)}<input name="{escape(name)}" value="{escape(value)}"></label>'


def render_dashboard() -> str:
    workspace = build_dashboard_workspace()
    card_html = "".join(
        f"""
        <article class="kpi-card {escape(kpi.status)}">
          <div class="kpi-card-top">
            <span>{escape(kpi.label)}</span>
            <em class="freshness {'stale' if kpi.stale else 'fresh'}">{'stale data' if kpi.stale else 'fresh batch'}</em>
          </div>
          <strong>{escape(kpi_value(kpi))}</strong>
          <dl>
            <div><dt>90-day target</dt><dd>{escape(kpi_value(kpi, kpi.target, kpi.unit))}</dd></div>
            <div><dt>Delta</dt><dd>{escape(delta_label(kpi))}</dd></div>
            <div><dt>Owner</dt><dd>{escape(kpi.owner)}</dd></div>
          </dl>
          <p>{escape(kpi.definition)}</p>
        </article>
        """
        for kpi in workspace.kpis
    )
    trend_svg = render_dashboard_trend(workspace)
    slice_links = "".join(
        f'<a href="#slice-{escape(slice_name.lower().replace(" ", "-"))}">{escape(slice_name)}</a>'
        for slice_name in workspace.breakdowns
    )
    breakdown_sections = "".join(
        render_breakdown_slice(slice_name, rows) for slice_name, rows in workspace.breakdowns.items()
    )
    action_items = "".join(
        f"""
        <article class="action-item">
          <span>{escape(item.day_range)}</span>
          <h3>{escape(item.action)}</h3>
          <dl>
            <div><dt>Owner</dt><dd>{escape(item.owner)}</dd></div>
            <div><dt>Effort</dt><dd>{escape(item.effort)}</dd></div>
            <div><dt>Impact</dt><dd>{escape(item.impact)}</dd></div>
            <div><dt>Source</dt><dd>{escape(item.source)}</dd></div>
          </dl>
        </article>
        """
        for item in workspace.action_plan
    )
    return f"""
    <section class="panel mapper-hero dashboard-hero">
      <div>
        <p class="eyebrow">Live workspace</p>
        <h2>RCM Dashboard KPI Framework</h2>
        <p>A clinic owner gets five action-grade metrics, 13 weeks of movement, the worst risk rows, and a 30-day operating plan from one synthetic batch.</p>
      </div>
      <div class="mapper-stats">
        <div><span>Headline KPIs</span><strong>{len(workspace.kpis)}</strong></div>
        <div><span>Trend buckets</span><strong>{len(workspace.trends)}</strong></div>
        <div><span>Freshness window</span><strong>{workspace.freshness_days}d</strong><em>synthetic</em></div>
      </div>
    </section>
    <section class="panel">
      <p class="eyebrow">Headline Scorecard</p>
      <h2>Every card has a target, owner, and action signal.</h2>
      <div class="dashboard-kpis">{card_html}</div>
    </section>
    <section class="panel">
      <p class="eyebrow">13-Week Trend</p>
      <h2>Static SVG trend lines use the same synthetic KPI batch.</h2>
      {trend_svg}
    </section>
    <section class="panel">
      <p class="eyebrow">Breakdowns</p>
      <h2>Worst-three callouts show where the owner should look first.</h2>
      <div class="slice-tabs">{slice_links}</div>
      <div class="breakdown-grid">{breakdown_sections}</div>
    </section>
    <section class="panel">
      <p class="eyebrow">30-Day Action Plan</p>
      <h2>Programmatic next moves pulled from the highest-risk rows.</h2>
      <div class="action-grid">{action_items}</div>
    </section>
    """


def render_dashboard_trend(workspace) -> str:
    keys = [kpi.key for kpi in workspace.kpis]
    labels = {kpi.key: kpi.label for kpi in workspace.kpis}
    colors = {
        "clean_claim_rate": "#00b3a4",
        "first_pass_yield": "#7dd3d8",
        "denial_rate": "#fb7185",
        "days_in_ar": "#facc15",
        "net_collection_rate": "#a7f3d0",
    }
    polylines = []
    legend = []
    for index, key in enumerate(keys):
        values = [point.values[key] for point in workspace.trends]
        lower_is_better = key in {"denial_rate", "days_in_ar"}
        points = svg_points(values, 42, 28, 760, 210, lower_is_better)
        polylines.append(
            f'<polyline points="{points}" fill="none" stroke="{colors[key]}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" />'
        )
        legend.append(
            f'<span><i style="background:{colors[key]}"></i>{escape(labels[key])}</span>'
        )
    first_week = escape(workspace.trends[0].week)
    last_week = escape(workspace.trends[-1].week)
    return f"""
    <div class="trend-wrap">
      <svg class="trend-chart" viewBox="0 0 860 280" role="img" aria-label="13-week KPI trend">
        <path d="M42 238 H802 M42 186 H802 M42 134 H802 M42 82 H802 M42 30 H802" stroke="#21414a" stroke-width="1" />
        {''.join(polylines)}
        <text x="42" y="268" fill="#9ab5b5" font-size="13">{first_week}</text>
        <text x="802" y="268" fill="#9ab5b5" font-size="13" text-anchor="end">{last_week}</text>
      </svg>
      <div class="trend-legend">{''.join(legend)}</div>
    </div>
    """


def svg_points(values: list[float], x: int, y: int, width: int, height: int, lower_is_better: bool) -> str:
    low = min(values)
    high = max(values)
    span = high - low or 1
    step = width / max(len(values) - 1, 1)
    points = []
    for index, value in enumerate(values):
        normalized = (value - low) / span
        py = y + height - (normalized * height)
        if lower_is_better:
            py = y + (normalized * height)
        points.append(f"{x + index * step:.1f},{py:.1f}")
    return " ".join(points)


def render_breakdown_slice(slice_name: str, rows) -> str:
    section_id = f"slice-{slice_name.lower().replace(' ', '-')}"
    worst = {row.segment for row in worst_three(rows)}
    table_rows = "".join(
        f"""
        <tr class="{'worst-three' if row.segment in worst else ''}">
          <td>{escape(row.segment)}{' <span>Worst three</span>' if row.segment in worst else ''}</td>
          <td>{dashboard_pct(row.clean_claim_rate)}</td>
          <td>{dashboard_pct(row.first_pass_yield)}</td>
          <td>{dashboard_pct(row.denial_rate)}</td>
          <td>{row.days_in_ar:.1f}</td>
          <td>{dashboard_pct(row.net_collection_rate)}</td>
          <td>{row.volume}</td>
          <td>{dollars(row.dollars_at_risk)} synthetic</td>
          <td>{escape(row.owner)}</td>
          <td>{escape(row.action)}</td>
        </tr>
        """
        for row in rows
    )
    return f"""
    <section class="breakdown-slice" id="{escape(section_id)}">
      <h3>{escape(slice_name)}</h3>
      <table>
        <thead><tr><th>Segment</th><th>Clean claim</th><th>First-pass</th><th>Denial</th><th>Days A/R</th><th>Net collect</th><th>Volume</th><th>Risk</th><th>Owner</th><th>Action</th></tr></thead>
        <tbody>{table_rows}</tbody>
      </table>
    </section>
    """


def render_edi_validation() -> str:
    workspace = build_edi_validation_workspace()
    readiness_cards = "".join(
        f"""
        <article class="kpi-card {'green' if label == 'Ready' else 'amber'}">
          <div class="kpi-card-top"><span>{escape(label)}</span><em class="freshness fresh">synthetic</em></div>
          <strong>{value}</strong>
          <p>{escape(note)}</p>
        </article>
        """
        for label, value, note in (
            ("Ready", f"{workspace.ready_to_submit} / {workspace.total_claims}", "Ready to submit synthetic claims after envelope, structure, and business-rule checks."),
            ("Envelope pass", str(workspace.envelope_pass), "Claims passing ISA, GS, ST, SE, GE, and IEA envelope checks."),
            ("Structure pass", str(workspace.structure_pass), "Claims passing the 837P required segment checks."),
            ("Business-rule pass", str(workspace.business_rule_pass), "Claims passing synthetic payer-specific pre-submission rules."),
        )
    )
    stacked_bar = render_readiness_bar(workspace)
    failure_rows = "".join(
        f"""
        <tr>
          <td><strong>{escape(entry.name)}</strong><span>{escape(entry.evidence)}</span></td>
          <td>{escape(entry.trigger)}</td>
          <td>{escape(entry.fix)}</td>
          <td>{entry.frequency}</td>
          <td>{dollars(entry.dollars_at_risk)} synthetic</td>
          <td>{escape(entry.owner)}</td>
        </tr>
        """
        for entry in workspace.failure_catalog
    )
    variance_rows = "".join(
        f"""
        <tr>
          <td><strong>{escape(row.payer)}</strong><span>{escape(row.note)}</span></td>
          {variance_cell(row.auth_ref_g1)}
          {variance_cell(row.dx_pointer_order)}
          {variance_cell(row.cob_single_coverage)}
          {variance_cell(row.rendering_taxonomy)}
          {variance_cell(row.service_location)}
          <td>{escape(row.owner)}</td>
          <td>{row.weekly_claims_at_risk} / {dollars(row.weekly_dollars_at_risk)} synthetic</td>
        </tr>
        """
        for row in workspace.payer_variance
    )
    action_items = "".join(
        f"""
        <article class="action-item">
          <span>{escape(item.day_range)}</span>
          <h3>{escape(item.action)}</h3>
          <dl>
            <div><dt>Owner</dt><dd>{escape(item.owner)}</dd></div>
            <div><dt>Effort</dt><dd>{escape(item.effort)}</dd></div>
            <div><dt>Impact</dt><dd>{escape(item.impact)}</dd></div>
            <div><dt>Source</dt><dd>{escape(item.source)}</dd></div>
          </dl>
        </article>
        """
        for item in workspace.action_plan
    )
    return f"""
    <section class="panel mapper-hero dashboard-hero">
      <div>
        <p class="eyebrow">Live workspace</p>
        <h2>EDI Validation Harness</h2>
        <p>See which synthetic claims are ready to submit, which defects block the batch, and which owner should repair them before a launch workflow scales.</p>
      </div>
      <div class="mapper-stats">
        <div><span>Ready to submit</span><strong>{workspace.ready_to_submit}</strong><em>of {workspace.total_claims}</em></div>
        <div><span>Failure entries</span><strong>{len(workspace.failure_catalog)}</strong></div>
        <div><span>Synthetic payers</span><strong>{len(workspace.payer_variance)}</strong></div>
      </div>
    </section>
    <section class="panel">
      <p class="eyebrow">Submission Readiness Check</p>
      <h2>Ready to submit: {workspace.ready_to_submit} of {workspace.total_claims} synthetic claims.</h2>
      <div class="dashboard-kpis edi-kpis">{readiness_cards}</div>
      {stacked_bar}
    </section>
    <section class="panel">
      <p class="eyebrow">Failure Catalog</p>
      <h2>The top pre-submission blockers are translated into owner-ready work.</h2>
      <table>
        <thead><tr><th>Failure</th><th>Trigger</th><th>Operating fix</th><th>Frequency</th><th>Dollars at risk</th><th>Owner</th></tr></thead>
        <tbody>{failure_rows}</tbody>
      </table>
    </section>
    <section class="panel">
      <p class="eyebrow">Payer Variance Map</p>
      <h2>Five synthetic payer routes show requirement drift before a batch goes out.</h2>
      <table>
        <thead><tr><th>Payer</th><th>Auth REF G1</th><th>Dx pointer</th><th>COB single coverage</th><th>Rendering taxonomy</th><th>Service location</th><th>Owner</th><th>Weekly risk</th></tr></thead>
        <tbody>{variance_rows}</tbody>
      </table>
    </section>
    <section class="panel">
      <p class="eyebrow">30-Day Readiness Plan</p>
      <h2>Readiness work is generated from the highest-risk failure and payer rows.</h2>
      <div class="action-grid">{action_items}</div>
    </section>
    """


def render_readiness_bar(workspace) -> str:
    parts = []
    for item in workspace.failure_mix:
        width = max(5, item.count / workspace.total_claims * 100)
        parts.append(
            f'<span style="width:{width:.2f}%;background:{item.color}"><strong>{escape(item.label)}</strong><em>{item.count}</em></span>'
        )
    legend = "".join(
        f'<li><i style="background:{item.color}"></i>{escape(item.label)}: {item.count}</li>'
        for item in workspace.failure_mix
    )
    return f"""
    <div class="stacked-bar">{''.join(parts)}</div>
    <ul class="bar-legend">{legend}</ul>
    """


def variance_cell(value: str) -> str:
    return f'<td><span class="variance-cell {escape(value.lower().replace("-", ""))}">{escape(value)}</span></td>'


def render_clearinghouse_responses() -> str:
    workspace = build_clearinghouse_responses_workspace()
    state_bar = render_response_state_bar(workspace)
    timeline_rows = "".join(
        f"""
        <tr>
          <td><strong>{escape(claim.claim_id)}</strong><span>{escape(claim.current_state)}</span></td>
          <td>{escape(claim.payer)}</td>
          <td>{escape(claim.submitted_at)}</td>
          <td>{claim.days_since_submission}</td>
          <td>{dollars(claim.amount)} synthetic</td>
          <td>{'Within SLA' if claim.within_sla else 'Watch'}</td>
        </tr>
        """
        for claim in workspace.timeline
    )
    parser_cards = "".join(
        f"""
        <article class="parser-card">
          <span>{escape(parser.response_type)}</span>
          <pre>{escape(chr(10).join(parser.raw_segments))}</pre>
          <ul>{''.join(f'<li>{escape(line)}</li>' for line in parser.interpretation)}</ul>
          <small>{escape(parser.owner)} | {parser.frequency} synthetic examples</small>
        </article>
        """
        for parser in workspace.parser_examples
    )
    stuck_rows = "".join(
        f"""
        <tr>
          <td>{escape(row.claim_id)}</td>
          <td>{escape(row.payer)}</td>
          <td>{escape(row.stuck_stage)}</td>
          <td>{row.days_stuck}</td>
          <td>{dollars(row.dollar_exposure)} synthetic</td>
          <td>{escape(row.recommended_action)}</td>
          <td>{escape(row.owner)}</td>
        </tr>
        """
        for row in workspace.stuck_inventory
    )
    action_items = "".join(
        f"""
        <article class="action-item">
          <span>{escape(item.day_range)}</span>
          <h3>{escape(item.action)}</h3>
          <dl>
            <div><dt>Owner</dt><dd>{escape(item.owner)}</dd></div>
            <div><dt>Effort</dt><dd>{escape(item.effort)}</dd></div>
            <div><dt>Impact</dt><dd>{escape(item.impact)}</dd></div>
            <div><dt>Source</dt><dd>{escape(item.source)}</dd></div>
          </dl>
        </article>
        """
        for item in workspace.action_plan
    )
    return f"""
    <section class="panel mapper-hero dashboard-hero">
      <div>
        <p class="eyebrow">Live workspace</p>
        <h2>Clearinghouse Response Tracker</h2>
        <p>See whether synthetic claims are moving through 999, 277CA, and 277 response stages before silent delays turn into aged follow-up.</p>
      </div>
      <div class="mapper-stats">
        <div><span>Tracking</span><strong>{workspace.acknowledged_within_sla}</strong><em>of {workspace.total_claims} in SLA</em></div>
        <div><span>Parser views</span><strong>{len(workspace.parser_examples)}</strong></div>
        <div><span>Stuck rows</span><strong>{len(workspace.stuck_inventory)}</strong></div>
      </div>
    </section>
    <section class="panel">
      <p class="eyebrow">Submission Timeline</p>
      <h2>Synthetic claims tracking: {workspace.acknowledged_within_sla} of {workspace.total_claims} acknowledged within SLA.</h2>
      {state_bar}
      <table>
        <thead><tr><th>Claim</th><th>Payer</th><th>Submitted</th><th>Days</th><th>Amount</th><th>SLA</th></tr></thead>
        <tbody>{timeline_rows}</tbody>
      </table>
    </section>
    <section class="panel">
      <p class="eyebrow">Response Parser View</p>
      <h2>Raw responses become operating instructions.</h2>
      <div class="parser-grid">{parser_cards}</div>
    </section>
    <section class="panel">
      <p class="eyebrow">Stuck-in-Clearinghouse Inventory</p>
      <h2>Past-SLA synthetic claims are grouped by the missing response stage.</h2>
      <table>
        <thead><tr><th>Claim</th><th>Payer</th><th>Stuck stage</th><th>Days stuck</th><th>Exposure</th><th>Recommended action</th><th>Owner</th></tr></thead>
        <tbody>{stuck_rows}</tbody>
      </table>
    </section>
    <section class="panel">
      <p class="eyebrow">30-Day Tracking Plan</p>
      <h2>Response tracking work is generated from worst stuck rows and parser signals.</h2>
      <div class="action-grid">{action_items}</div>
    </section>
    """


def render_response_state_bar(workspace) -> str:
    parts = []
    for item in workspace.state_mix:
        width = max(6, item.count / workspace.total_claims * 100)
        parts.append(
            f'<span style="width:{width:.2f}%;background:{item.color}"><strong>{escape(item.label)}</strong><em>{item.count}</em></span>'
        )
    legend = "".join(
        f'<li><i style="background:{item.color}"></i>{escape(item.label)}: {item.count}</li>'
        for item in workspace.state_mix
    )
    return f'<div class="stacked-bar">{"".join(parts)}</div><ul class="bar-legend">{legend}</ul>'


def render_claims_pipeline(params: dict[str, str]) -> str:
    workspace = build_claims_pipeline_workspace(params.get("path"))
    selected = workspace.selected_path
    path_links = "".join(
        f'<a class="path-chip {"active" if path.slug == selected.slug else ""}" href="/app/claims-pipeline?path={escape(path.slug)}">'
        f'<strong>{escape(path.label)}</strong><span>{escape(path.current_status)}</span></a>'
        for path in workspace.paths
    )
    timeline_nodes = "".join(
        f"""
        <article class="timeline-node {escape(node.status)}">
          <span>{escape(node.status)}</span>
          <h3>{escape(node.stage)}</h3>
          <p>{node.elapsed_days} elapsed days</p>
          <small>{escape(node.owner)}</small>
        </article>
        """
        for node in selected.nodes
    )
    ownership_rows = "".join(
        f"""
        <tr class="{'loud' if row.unassigned or row.owner == 'Unassigned' else ''}">
          <td>{escape(row.stage)}</td>
          <td>{escape(row.owner)}</td>
          <td>{escape(row.role)}</td>
          <td>{row.queue_load}</td>
          <td>{row.unassigned}</td>
          <td>{escape(row.note)}</td>
        </tr>
        """
        for row in workspace.ownership
    )
    stuck_rows = "".join(
        f"""
        <tr>
          <td>{escape(row.group)}</td>
          <td>{escape(row.stuck_at)}</td>
          <td>{row.count}</td>
          <td>{row.aged_days}</td>
          <td>{dollars(row.dollars_at_risk)} synthetic</td>
          <td>{escape(row.action)}</td>
        </tr>
        """
        for row in workspace.stuck_points
    )
    action_items = "".join(
        f"""
        <article class="action-item">
          <span>{escape(item.day_range)}</span>
          <h3>{escape(item.action)}</h3>
          <dl>
            <div><dt>Owner</dt><dd>{escape(item.owner)}</dd></div>
            <div><dt>Effort</dt><dd>{escape(item.effort)}</dd></div>
            <div><dt>Impact</dt><dd>{escape(item.impact)}</dd></div>
          </dl>
        </article>
        """
        for item in workspace.action_plan
    )
    risk_total = sum(row.dollars_at_risk for row in workspace.stuck_points)
    unassigned_total = sum(row.unassigned for row in workspace.ownership)
    return f"""
    <section class="panel mapper-hero">
      <div>
        <p class="eyebrow">Live workspace</p>
        <h2>Claims Pipeline Mapper</h2>
        <p>See exactly where synthetic claims move, stall, and need ownership before a startup clinic adds more volume.</p>
      </div>
      <div class="mapper-stats">
        <div><span>Sample paths</span><strong>{len(workspace.paths)}</strong></div>
        <div><span>Unassigned slots</span><strong>{unassigned_total}</strong></div>
        <div><span>Dollars at risk</span><strong>{dollars(risk_total)}</strong><em>synthetic</em></div>
      </div>
    </section>
    <section class="panel">
      <p class="eyebrow">Claim Path Timeline</p>
      <div class="path-picker">{path_links}</div>
      <div class="selected-claim">
        <h2>{escape(selected.label)}: {escape(selected.claim_id)}</h2>
        <p>{escape(selected.summary)}</p>
        <span>{dollars(selected.billed_amount)} billed | {dollars(selected.dollars_at_risk)} synthetic dollars at risk</span>
      </div>
      <div class="timeline">{timeline_nodes}</div>
    </section>
    <section class="panel">
      <p class="eyebrow">Ownership Map</p>
      <h2>Owner gaps are intentionally loud.</h2>
      <table>
        <thead><tr><th>Stage</th><th>Owner</th><th>Role</th><th>Queue</th><th>Unassigned</th><th>Operating note</th></tr></thead>
        <tbody>{ownership_rows}</tbody>
      </table>
    </section>
    <section class="panel">
      <p class="eyebrow">Stuck-Point Inventory</p>
      <h2>Synthetic cohorts grouped by where the claim path stalls.</h2>
      <table>
        <thead><tr><th>Cohort</th><th>Stuck at</th><th>Count</th><th>Aged days</th><th>Dollars at risk</th><th>Recommended next action</th></tr></thead>
        <tbody>{stuck_rows}</tbody>
      </table>
    </section>
    <section class="panel">
      <p class="eyebrow">First 30-Day Action Plan</p>
      <h2>Week-one operating moves after the Launch Workspace handoff.</h2>
      <div class="action-grid">{action_items}</div>
    </section>
    """


def render_placeholder(slug: str) -> str:
    module = next(item for item in ROADMAP_MODULES if item["slug"] == slug)
    return f"""
    <section class="panel placeholder">
      <p class="eyebrow">{escape(module["status"])}</p>
      <h2>{escape(module["label"])}</h2>
      <p>{escape(module["description"])}</p>
      <p>{escape(PLACEHOLDER_COPY.get(slug, "Reserved for the product roadmap."))}</p>
      <a class="button" href="/app/intake">Return to Launch Workspace</a>
    </section>
    """


def pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def dollars(value: float) -> str:
    return f"${value:,.0f}"


CSS = """
:root { color-scheme: dark; --bg:#071012; --panel:#101b20; --line:#21414a; --text:#eef7f5; --muted:#9ab5b5; --teal:#00b3a4; --steel:#7dd3d8; --risk:#eab308; }
* { box-sizing: border-box; }
body { margin:0; min-height:100vh; display:flex; background:radial-gradient(circle at 80% 0%, #173a40 0, transparent 38%), var(--bg); color:var(--text); font:15px/1.45 Inter, ui-sans-serif, system-ui, -apple-system, Segoe UI, sans-serif; }
.sidebar { width:286px; flex:0 0 286px; min-height:100vh; padding:22px 16px; background:#091316; border-right:1px solid var(--line); position:sticky; top:0; }
.brand { font-size:22px; font-weight:800; color:var(--steel); }
.env { margin:8px 0 20px; color:var(--muted); font-size:12px; text-transform:uppercase; letter-spacing:.08em; }
nav { display:grid; gap:7px; }
nav a { color:var(--text); text-decoration:none; padding:11px 12px; border:1px solid transparent; border-radius:8px; display:grid; gap:2px; }
nav a.active, nav a:hover { background:#10242a; border-color:#1f5960; }
nav small { color:var(--muted); }
.shell { flex:1 1 auto; min-width:0; padding:28px; }
.topbar { display:flex; align-items:flex-start; justify-content:space-between; gap:24px; margin-bottom:24px; }
h1, h2 { margin:0; letter-spacing:0; }
h1 { font-size:34px; }
h2 { font-size:24px; margin-bottom:14px; }
.eyebrow { margin:0 0 8px; color:var(--teal); text-transform:uppercase; letter-spacing:.08em; font-weight:700; font-size:12px; }
.status, .button, button { background:var(--teal); color:#021415; border:0; border-radius:8px; padding:11px 14px; font-weight:800; text-decoration:none; display:inline-block; }
.grid { display:grid; gap:20px; }
.hero-grid { grid-template-columns:minmax(340px, 1.05fr) minmax(340px, .95fr); align-items:stretch; }
.panel { background:rgba(16,27,32,.92); border:1px solid var(--line); border-radius:8px; padding:22px; box-shadow:0 22px 70px rgba(0,0,0,.25); margin-bottom:20px; max-width:100%; overflow-x:auto; }
form { display:grid; grid-template-columns:1fr 1fr; gap:13px; }
label { display:grid; gap:6px; color:var(--muted); font-size:13px; }
input { width:100%; border:1px solid #31545c; border-radius:8px; background:#071316; color:var(--text); padding:11px 12px; font:inherit; }
button { grid-column:1 / -1; cursor:pointer; }
.score-ring { width:118px; height:118px; border-radius:999px; display:grid; place-items:center; border:12px solid var(--teal); font-size:34px; font-weight:900; margin-bottom:18px; background:#071316; }
ol { padding-left:20px; color:#d8e7e5; }
table { width:100%; min-width:760px; border-collapse:collapse; overflow:hidden; border-radius:8px; }
th, td { text-align:left; padding:12px; border-bottom:1px solid var(--line); }
th { color:var(--steel); background:#0b171a; }
.kpis { display:grid; grid-template-columns:repeat(6, minmax(120px, 1fr)); gap:12px; margin:18px 0; }
.kpi { background:#071316; border:1px solid #21414a; border-radius:8px; padding:14px; display:grid; gap:8px; }
.kpi span { color:var(--muted); }
.kpi strong { color:var(--steel); font-size:24px; }
.proof { width:100%; max-height:680px; object-fit:contain; border:1px solid var(--line); border-radius:8px; background:#081216; }
.alert { border-color:#7f1d1d; }
.dashboard-hero h2 { font-size:30px; }
.dashboard-kpis { display:grid; grid-template-columns:repeat(5,minmax(180px,1fr)); gap:14px; }
.kpi-card { background:#071316; border:1px solid #21414a; border-radius:8px; padding:16px; display:grid; gap:13px; min-height:260px; }
.kpi-card.green { border-color:#00b3a4; }
.kpi-card.amber { border-color:#facc15; }
.kpi-card.red { border-color:#fb7185; }
.kpi-card-top { display:flex; justify-content:space-between; gap:10px; align-items:flex-start; }
.kpi-card-top span { color:var(--muted); font-size:13px; font-weight:800; text-transform:uppercase; letter-spacing:.05em; }
.kpi-card strong { color:#fff; font-size:31px; line-height:1; }
.kpi-card p { color:#cbd5e1; margin:0; }
.edi-kpis { grid-template-columns:repeat(4,minmax(180px,1fr)); }
.freshness { flex:0 0 auto; border-radius:999px; padding:4px 7px; font-style:normal; font-size:10px; font-weight:900; text-transform:uppercase; letter-spacing:.05em; color:#021415; background:var(--teal); }
.freshness.stale { background:#facc15; }
.stacked-bar { display:flex; min-height:48px; overflow:hidden; border:1px solid #21414a; border-radius:8px; background:#071316; margin:18px 0 12px; }
.stacked-bar span { display:flex; align-items:center; justify-content:space-between; min-width:84px; padding:0 10px; color:#021415; font-size:12px; font-weight:900; }
.stacked-bar em { font-style:normal; opacity:.8; }
.bar-legend { display:flex; flex-wrap:wrap; gap:12px; padding:0; margin:0; list-style:none; color:#d8e7e5; }
.bar-legend li { display:flex; gap:7px; align-items:center; }
.bar-legend i { width:10px; height:10px; border-radius:999px; display:inline-block; }
td > span { display:block; color:var(--muted); margin-top:4px; font-size:12px; }
.variance-cell { display:inline-block; min-width:54px; text-align:center; margin:0; border-radius:999px; padding:5px 8px; color:#021415; font-weight:900; text-transform:uppercase; font-size:11px; }
.variance-cell.pass { background:var(--teal); }
.variance-cell.fail { background:#fb7185; }
.variance-cell.na { background:#64748b; color:#f8fafc; }
.parser-grid { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:14px; }
.parser-card { background:#071316; border:1px solid #21414a; border-radius:8px; padding:16px; display:grid; gap:12px; }
.parser-card > span { color:var(--teal); font-weight:900; text-transform:uppercase; letter-spacing:.08em; font-size:12px; }
.parser-card pre { white-space:pre-wrap; margin:0; padding:12px; background:#030b0d; border:1px solid #1f3941; border-radius:8px; color:#d8e7e5; font-size:12px; overflow:auto; }
.parser-card ul { margin:0; padding-left:18px; color:#d8e7e5; }
.parser-card small { color:var(--muted); }
.trend-wrap { display:grid; grid-template-columns:minmax(0,1fr) 220px; gap:22px; align-items:center; }
.trend-chart { width:100%; min-height:250px; background:#071316; border:1px solid #21414a; border-radius:8px; }
.trend-legend { display:grid; gap:12px; }
.trend-legend span { color:#d8e7e5; display:flex; gap:9px; align-items:center; }
.trend-legend i { width:12px; height:12px; border-radius:999px; display:inline-block; }
.slice-tabs { display:flex; flex-wrap:wrap; gap:9px; margin:14px 0 18px; }
.slice-tabs a { color:#021415; background:var(--steel); border-radius:999px; padding:8px 12px; text-decoration:none; font-weight:900; }
.breakdown-grid { display:grid; gap:18px; }
.breakdown-slice { background:#071316; border:1px solid #21414a; border-radius:8px; padding:16px; overflow-x:auto; }
.breakdown-slice h3 { margin:0 0 12px; font-size:18px; color:var(--steel); }
tr.worst-three td { background:rgba(250,204,21,.12); color:#fff8d0; }
tr.worst-three td:first-child { color:#facc15; font-weight:900; }
tr.worst-three span { display:inline-block; margin-left:8px; color:#021415; background:#facc15; border-radius:999px; padding:3px 7px; font-size:10px; font-weight:900; text-transform:uppercase; }
.mapper-hero { display:flex; justify-content:space-between; gap:24px; align-items:stretch; }
.mapper-hero p { color:var(--muted); max-width:720px; }
.mapper-stats { display:grid; grid-template-columns:repeat(3, minmax(130px,1fr)); gap:12px; min-width:min(100%, 520px); }
.mapper-stats div { background:#071316; border:1px solid #21414a; border-radius:8px; padding:14px; display:grid; gap:4px; }
.mapper-stats span, .mapper-stats em { color:var(--muted); font-style:normal; }
.mapper-stats strong { color:var(--steel); font-size:26px; }
.path-picker { display:grid; grid-template-columns:repeat(5,minmax(0,1fr)); gap:10px; margin:18px 0; }
.path-chip { color:var(--text); text-decoration:none; border:1px solid #21414a; background:#071316; border-radius:8px; padding:12px; display:grid; gap:4px; min-height:72px; }
.path-chip.active { border-color:var(--teal); box-shadow:0 0 0 1px rgba(0,179,164,.35), 0 0 22px rgba(0,179,164,.12); }
.path-chip span { color:var(--muted); text-transform:uppercase; font-size:11px; letter-spacing:.06em; }
.selected-claim { background:#071316; border:1px solid #21414a; border-radius:8px; padding:16px; margin-bottom:18px; }
.selected-claim p { color:var(--muted); margin-top:8px; }
.selected-claim span { display:inline-block; margin-top:10px; color:var(--steel); font-weight:800; }
.timeline { display:grid; grid-template-columns:repeat(8,minmax(130px,1fr)); gap:10px; overflow-x:auto; padding-bottom:8px; }
.timeline-node { min-width:130px; border:1px solid #21414a; border-radius:8px; padding:12px; background:#071316; position:relative; }
.timeline-node span { display:inline-block; color:#021415; background:var(--steel); border-radius:999px; padding:3px 7px; font-size:11px; font-weight:900; text-transform:uppercase; }
.timeline-node.paid span { background:var(--teal); }
.timeline-node.stuck span { background:#facc15; }
.timeline-node.denied span { background:#fb7185; }
.timeline-node h3 { margin:10px 0 8px; font-size:15px; }
.timeline-node p, .timeline-node small { color:var(--muted); }
tr.loud td { background:rgba(251,113,133,.12); color:#ffe8ee; }
tr.loud td:nth-child(2), tr.loud td:nth-child(5) { color:#fb7185; font-weight:900; }
.action-grid { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:14px; }
.action-item { background:#071316; border:1px solid #21414a; border-radius:8px; padding:16px; }
.action-item > span { color:var(--teal); font-weight:900; text-transform:uppercase; font-size:12px; letter-spacing:.06em; }
.action-item h3 { margin:10px 0 14px; font-size:17px; line-height:1.3; }
dl { display:grid; gap:9px; margin:0; }
dl div { display:grid; gap:3px; }
dt { color:var(--muted); font-size:12px; text-transform:uppercase; letter-spacing:.06em; }
dd { margin:0; color:#d8e7e5; }
@media (max-width: 1180px) { .timeline { grid-template-columns:repeat(4,minmax(150px,1fr)); } .path-picker, .action-grid, .dashboard-kpis, .edi-kpis, .parser-grid { grid-template-columns:repeat(2,minmax(0,1fr)); } .mapper-hero { display:block; } .mapper-stats { margin-top:18px; } .trend-wrap { grid-template-columns:1fr; } .trend-legend { grid-template-columns:repeat(2,minmax(0,1fr)); } }
@media (max-width: 940px) { body { display:block; overflow-x:hidden; } .sidebar { position:relative; width:auto; min-height:0; padding:16px; border-right:0; border-bottom:1px solid var(--line); } .env { margin-bottom:12px; } nav { display:flex; overflow-x:auto; gap:8px; padding-bottom:4px; } nav a { flex:0 0 210px; } .shell { padding:18px; width:100%; } .hero-grid, form { grid-template-columns:1fr; } .kpis, .mapper-stats, .path-picker, .action-grid, .dashboard-kpis, .trend-legend, .parser-grid { grid-template-columns:1fr; } .topbar { display:block; } .timeline { grid-template-columns:1fr; overflow-x:visible; } table { min-width:680px; } }
"""
