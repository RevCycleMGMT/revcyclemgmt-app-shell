"""HTML rendering for the local app shell proof."""

from __future__ import annotations

from html import escape
from urllib.parse import parse_qs

from .data import DASHBOARD_METRICS, DASHBOARD_READOUT, PLACEHOLDER_COPY, ROADMAP_MODULES
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
        body = render_launch(params) if slug == "launch-workspace" else render_dashboard() if slug == "dashboard" else render_placeholder(slug)
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
        <h1>App Shell + Launch Workspace</h1>
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
    cards = [
        ("Claims", f"{DASHBOARD_METRICS['claims_submitted']:,}"),
        ("Clean claim", pct(DASHBOARD_METRICS["clean_claim_rate"])),
        ("Rejection", pct(DASHBOARD_METRICS["clearinghouse_rejection_rate"])),
        ("Denial", pct(DASHBOARD_METRICS["denial_rate"])),
        ("835 match", pct(DASHBOARD_METRICS["remit_match_rate"])),
        ("A/R exposure", dollars(DASHBOARD_METRICS["current_ar_exposure"])),
    ]
    card_html = "".join(f'<div class="kpi"><span>{label}</span><strong>{value}</strong></div>' for label, value in cards)
    readout = "".join(f"<li>{escape(line)}</li>" for line in DASHBOARD_READOUT)
    return f"""
    <section class="panel">
      <p class="eyebrow">Synthetic proof</p>
      <h2>Dashboard Proof visual anchor</h2>
      <div class="kpis">{card_html}</div>
      <ol>{readout}</ol>
      <img class="proof" src="/assets/dashboard-proof-anchor.svg" alt="RevCycleMGMT dashboard proof anchor">
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
.shell { width:100%; padding:28px; }
.topbar { display:flex; align-items:flex-start; justify-content:space-between; gap:24px; margin-bottom:24px; }
h1, h2 { margin:0; letter-spacing:0; }
h1 { font-size:34px; }
h2 { font-size:24px; margin-bottom:14px; }
.eyebrow { margin:0 0 8px; color:var(--teal); text-transform:uppercase; letter-spacing:.08em; font-weight:700; font-size:12px; }
.status, .button, button { background:var(--teal); color:#021415; border:0; border-radius:8px; padding:11px 14px; font-weight:800; text-decoration:none; display:inline-block; }
.grid { display:grid; gap:20px; }
.hero-grid { grid-template-columns:minmax(340px, 1.05fr) minmax(340px, .95fr); align-items:stretch; }
.panel { background:rgba(16,27,32,.92); border:1px solid var(--line); border-radius:8px; padding:22px; box-shadow:0 22px 70px rgba(0,0,0,.25); margin-bottom:20px; }
form { display:grid; grid-template-columns:1fr 1fr; gap:13px; }
label { display:grid; gap:6px; color:var(--muted); font-size:13px; }
input { width:100%; border:1px solid #31545c; border-radius:8px; background:#071316; color:var(--text); padding:11px 12px; font:inherit; }
button { grid-column:1 / -1; cursor:pointer; }
.score-ring { width:118px; height:118px; border-radius:999px; display:grid; place-items:center; border:12px solid var(--teal); font-size:34px; font-weight:900; margin-bottom:18px; background:#071316; }
ol { padding-left:20px; color:#d8e7e5; }
table { width:100%; border-collapse:collapse; overflow:hidden; border-radius:8px; }
th, td { text-align:left; padding:12px; border-bottom:1px solid var(--line); }
th { color:var(--steel); background:#0b171a; }
.kpis { display:grid; grid-template-columns:repeat(6, minmax(120px, 1fr)); gap:12px; margin:18px 0; }
.kpi { background:#071316; border:1px solid #21414a; border-radius:8px; padding:14px; display:grid; gap:8px; }
.kpi span { color:var(--muted); }
.kpi strong { color:var(--steel); font-size:24px; }
.proof { width:100%; max-height:680px; object-fit:contain; border:1px solid var(--line); border-radius:8px; background:#081216; }
.alert { border-color:#7f1d1d; }
@media (max-width: 940px) { body { display:block; } .sidebar { position:relative; width:auto; min-height:0; } .shell { padding:18px; } .hero-grid, form { grid-template-columns:1fr; } .kpis { grid-template-columns:1fr 1fr; } .topbar { display:block; } }
"""
