"""
ResearchPilot AI — Thumbnail Node
SVG cover card with correct project name + Pollinations AI image option.
"""
import time, html
from datetime import date
from graph.state import ResearchState

DOMAIN_COLORS = {
    "healthcare":   ("#10b981","#064e3b"),
    "finance":      ("#f59e0b","#451a03"),
    "technology":   ("#6366f1","#1e1b4b"),
    "science":      ("#3b82f6","#1e3a5f"),
    "history":      ("#a78bfa","#2e1065"),
    "environment":  ("#22c55e","#052e16"),
    "politics":     ("#ef4444","#450a0a"),
    "general":      ("#94a3b8","#0f172a"),
}
DOMAIN_ICONS = {
    "healthcare":"⚕","finance":"₿","technology":"⚙",
    "science":"🔬","history":"📜","environment":"🌍",
    "politics":"🏛","general":"🔍",
}


def thumbnail_node(state: ResearchState) -> dict:
    t0 = time.time()
    logs    = list(state.get("agent_logs", []))
    timings = dict(state.get("agent_timings", {}))

    if not state.get("generate_thumbnail", False):
        logs.append("[Cover] Skipped — not requested")
        return {"thumbnail_svg": None, "agent_logs": logs, "agent_timings": timings}

    logs.append("[Cover] Generating SVG cover card...")
    query  = state.get("query", "Research Report")
    domain = state.get("topic_domain", "general")   # fixed: was state.get("domain")
    score  = state.get("quality_score", 0)
    active = state.get("active_agents", [])
    today  = date.today().strftime("%B %d, %Y")

    accent, bg = DOMAIN_COLORS.get(domain, DOMAIN_COLORS["general"])
    icon       = DOMAIN_ICONS.get(domain, "🔍")
    title      = html.escape(query[:75])
    dlabel     = domain.upper()
    score_str  = f"{score:.1f}/10" if score > 0 else "—"
    agents_str = " · ".join(active[:5]) if active else "multi-agent"

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 820 440" width="820" height="440">
  <defs>
    <linearGradient id="gbg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%"   stop-color="{bg}"/>
      <stop offset="100%" stop-color="#0f172a"/>
    </linearGradient>
    <linearGradient id="gstripe" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%"   stop-color="{accent}"/>
      <stop offset="100%" stop-color="{accent}" stop-opacity="0.2"/>
    </linearGradient>
    <filter id="glow">
      <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
      <feMerge><feMergeNode in="coloredBlur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>

  <rect width="820" height="440" fill="url(#gbg)" rx="16"/>
  <rect x="0" y="0" width="6" height="440" fill="{accent}" rx="3"/>
  <rect x="6" y="0" width="814" height="4" fill="url(#gstripe)"/>

  <!-- Decorative circles -->
  <circle cx="720" cy="80"  r="90" fill="{accent}" fill-opacity="0.05"/>
  <circle cx="760" cy="360" r="60" fill="{accent}" fill-opacity="0.07"/>

  <!-- Icon circle -->
  <circle cx="78" cy="78" r="42" fill="{accent}" fill-opacity="0.15" filter="url(#glow)"/>
  <text x="78" y="94" text-anchor="middle" font-size="34">{icon}</text>

  <!-- Brand name — ResearchPilot AI -->
  <text x="138" y="62" font-family="'Segoe UI',Arial,sans-serif" font-size="12"
        font-weight="700" fill="{accent}" letter-spacing="2.5">RESEARCHPILOT AI</text>

  <!-- Domain badge -->
  <rect x="138" y="70" width="{len(dlabel)*9+20}" height="22" rx="11"
        fill="{accent}" fill-opacity="0.18"/>
  <text x="{138 + len(dlabel)*4.5 + 10}" y="86" text-anchor="middle"
        font-family="'Segoe UI',Arial,sans-serif" font-size="11" font-weight="700"
        fill="{accent}">{dlabel}</text>

  <!-- Title -->
  <foreignObject x="38" y="130" width="745" height="155">
    <body xmlns="http://www.w3.org/1999/xhtml">
      <p style="margin:0;font-family:'Segoe UI',Arial,sans-serif;font-size:25px;
                font-weight:700;color:#f1f5f9;line-height:1.35;word-wrap:break-word;">
        {title}
      </p>
    </body>
  </foreignObject>

  <!-- Agents strip -->
  <rect x="38" y="296" width="744" height="26" rx="6" fill="{accent}" fill-opacity="0.1"/>
  <text x="50" y="314" font-family="'Segoe UI',Arial,sans-serif" font-size="11"
        fill="{accent}" font-weight="600">Agents: {agents_str}</text>

  <!-- Bottom bar -->
  <rect x="0"  y="374" width="820" height="66" fill="#000" fill-opacity="0.25"/>
  <rect x="0"  y="370" width="820" height="4"  fill="url(#gstripe)"/>
  <text x="50"  y="406" font-family="'Segoe UI',Arial,sans-serif" font-size="12" fill="#94a3b8">{today}</text>
  <text x="410" y="406" text-anchor="middle" font-family="'Segoe UI',Arial,sans-serif"
        font-size="11" fill="#475569">Autonomous Multi-Agent Research System</text>
  <text x="770" y="406" text-anchor="end" font-family="'Segoe UI',Arial,sans-serif"
        font-size="12" fill="{accent}">Score: {score_str}</text>
</svg>"""

    timings["cover"] = round(time.time() - t0, 2)
    logs.append("[Cover] Done. SVG cover generated.")
    return {"thumbnail_svg": svg, "agent_logs": logs, "agent_timings": timings}
