"""
ResearchPilot AI — Visualization Node
6 chart types: Horizontal Bar, Area Trend, Gauge, Bubble, Donut, Heatmap
Uses structured_data from Statistics Agent (now includes comparisons field).
"""
import time, json
from graph.state import ResearchState

DARK  = "#0f172a"
CARD  = "#1e293b"
GRID  = "#334155"
TEXT  = "#e2e8f0"
TITLE = "#a5b4fc"

PALETTE = ["#6366f1","#8b5cf6","#34d399","#f59e0b","#ef4444",
           "#06b6d4","#10b981","#f97316","#a78bfa","#ec4899"]


def _parse_val(v):
    try:
        return float(str(v).replace(",","").replace("%","").strip())
    except (ValueError, TypeError):
        return 0.0


def visualization_node(state: ResearchState) -> dict:
    t0      = time.time()
    active  = state.get("active_agents", [])
    logs    = list(state.get("agent_logs", []))
    timings = dict(state.get("agent_timings", {}))

    if "statistics" not in active:
        logs.append("[Viz] Skipped — statistics not active")
        return {"chart_json": [], "agent_logs": logs, "agent_timings": timings}

    sd      = state.get("structured_data", {})
    metrics = sd.get("metrics", [])
    trends  = sd.get("trends", [])
    comps   = sd.get("comparisons", [])
    logs.append(f"[Viz] Building charts — {len(metrics)} metrics, {len(trends)} trends, {len(comps)} comparisons")

    charts = []
    try:
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots

        layout_base = dict(
            plot_bgcolor=CARD, paper_bgcolor=DARK,
            font=dict(color=TEXT, size=12),
            margin=dict(l=25, r=25, t=55, b=30),
            legend=dict(bgcolor="#1e293b", bordercolor=GRID, font=dict(color=TEXT)),
        )

        # ── Chart 1: Horizontal Bar ─────────────────────────────
        if metrics:
            m8     = metrics[:8]
            labels = [m.get("label","")[:38] for m in m8]
            vals   = [_parse_val(m.get("value",0)) for m in m8]
            annots = [f"{v:,.1f} {m.get('unit','')}" for v,m in zip(vals,m8)]

            fig = go.Figure(go.Bar(
                x=vals, y=labels, orientation="h",
                marker=dict(color=PALETTE[:len(labels)],
                            line=dict(color=DARK, width=1)),
                text=annots, textposition="auto",
                hovertemplate="%{y}<br><b>%{text}</b><extra></extra>",
            ))
            fig.update_layout(**layout_base,
                title=dict(text="📊 Key Metrics Overview", font=dict(color=TITLE,size=16)),
                xaxis=dict(gridcolor=GRID, showgrid=True),
                yaxis=dict(gridcolor=GRID, autorange="reversed"),
                height=380)
            charts.append(fig.to_json())
            logs.append("[Viz] ✅ Horizontal bar chart")

        # ── Chart 2: Multi-series Area (up to 3 trends) ─────────
        if trends:
            fig2 = go.Figure()
            # Pre-built valid rgba fills — no string-mangling of hex codes
            color_fill_pairs = [
                ("#34d399", "rgba(52,211,153,0.10)"),
                ("#6366f1", "rgba(99,102,241,0.10)"),
                ("#f59e0b", "rgba(245,158,11,0.10)"),
            ]
            fills = ["tozeroy", "tonexty", "tonexty"]
            for i, trend in enumerate(trends[:3]):
                pts   = trend.get("data_points",[])
                years = [str(dp.get("year","")) for dp in pts]
                vals2 = [_parse_val(dp.get("value",0)) for dp in pts]
                col, fill_col = color_fill_pairs[i % 3]
                fig2.add_trace(go.Scatter(
                    x=years, y=vals2, name=trend.get("name",""),
                    mode="lines+markers",
                    line=dict(color=col, width=2.5),
                    marker=dict(size=7, color=col),
                    fill=fills[i],
                    fillcolor=fill_col,
                    hovertemplate=f"%{{x}}: %{{y:,.1f}} {trend.get('unit','')}<extra>{trend.get('name','')}</extra>",
                ))
            fig2.update_layout(**layout_base,
                title=dict(text="📈 Growth Trends Over Time", font=dict(color=TITLE,size=16)),
                xaxis=dict(gridcolor=GRID, title="Year"),
                yaxis=dict(gridcolor=GRID, title="Value"),
                height=350)
            charts.append(fig2.to_json())
            logs.append("[Viz] ✅ Multi-series area chart")

        # ── Chart 3: Donut (regional/segment breakdown) ─────────
        if comps:
            fig3 = go.Figure(go.Pie(
                labels=[c.get("category","") for c in comps],
                values=[_parse_val(c.get("value",0)) for c in comps],
                hole=0.52,
                marker=dict(colors=[c.get("color", PALETTE[i%10]) for i,c in enumerate(comps)],
                            line=dict(color=DARK, width=2)),
                textinfo="label+percent",
                textfont=dict(size=12, color=TEXT),
                hovertemplate="%{label}: <b>%{value}%</b><extra></extra>",
            ))
            fig3.add_annotation(text="Share",   x=0.5, y=0.55, showarrow=False,
                                font=dict(color="#64748b",size=13))
            fig3.add_annotation(text="by Region", x=0.5, y=0.44, showarrow=False,
                                font=dict(color="#64748b",size=11))
            fig3.update_layout(**layout_base,
                title=dict(text="🌍 Regional Distribution", font=dict(color=TITLE,size=16)),
                height=360)
            charts.append(fig3.to_json())
            logs.append("[Viz] ✅ Donut chart")

        # ── Chart 4: Gauge ──────────────────────────────────────
        if metrics:
            g_val, g_label = 0.0, "Score"
            for m in metrics:
                v = _parse_val(m.get("value",0))
                if 0 < v <= 100:
                    g_val, g_label = v, m.get("label","Score")[:30]
                    break
            if g_val > 0:
                fig4 = go.Figure(go.Indicator(
                    mode="gauge+number+delta",
                    value=g_val,
                    title=dict(text=g_label, font=dict(color=TITLE,size=14)),
                    delta=dict(reference=g_val*0.8, relative=False,
                               increasing=dict(color="#34d399"),
                               decreasing=dict(color="#ef4444")),
                    gauge=dict(
                        axis=dict(range=[0,100], tickcolor=TEXT),
                        bar=dict(color="#6366f1"),
                        bgcolor=CARD, bordercolor=GRID,
                        steps=[
                            dict(range=[0,33],  color="#450a0a"),
                            dict(range=[33,66], color="#451a03"),
                            dict(range=[66,100],color="#064e3b"),
                        ],
                        threshold=dict(line=dict(color="#f59e0b",width=4),
                                       thickness=0.75, value=g_val),
                    ),
                    number=dict(suffix="%", font=dict(color=TEXT,size=32)),
                ))
                fig4.update_layout(paper_bgcolor=DARK, font=dict(color=TEXT),
                                   margin=dict(l=30,r=30,t=60,b=20), height=300)
                charts.append(fig4.to_json())
                logs.append("[Viz] ✅ Gauge chart")

        # ── Chart 5: Bubble scatter ──────────────────────────────
        if len(metrics) >= 4:
            m10    = metrics[:10]
            labels = [m.get("label","")[:22] for m in m10]
            xvals  = list(range(1, len(m10)+1))
            yvals  = [_parse_val(m.get("value",0)) for m in m10]
            ymax   = max(yvals) if yvals else 1
            sizes  = [max(18, min(65, (v/(ymax or 1))*60)) for v in yvals]
            years  = [m.get("year","2024") for m in m10]

            fig5 = go.Figure(go.Scatter(
                x=xvals, y=yvals,
                mode="markers+text",
                marker=dict(size=sizes, color=PALETTE[:len(m10)],
                            opacity=0.85, line=dict(color=DARK,width=1)),
                text=labels, textposition="top center",
                textfont=dict(size=10, color=TEXT),
                customdata=years,
                hovertemplate="<b>%{text}</b><br>Value: %{y:,.2f}<br>Year: %{customdata}<extra></extra>",
            ))
            fig5.update_layout(**layout_base,
                title=dict(text="🔵 Metrics Comparison (Bubble View)", font=dict(color=TITLE,size=16)),
                xaxis=dict(gridcolor=GRID, showticklabels=False, title="Metrics"),
                yaxis=dict(gridcolor=GRID, title="Value"),
                height=360)
            charts.append(fig5.to_json())
            logs.append("[Viz] ✅ Bubble chart")

        # ── Chart 6: Year-on-year bar comparison ─────────────────
        if len(trends) >= 1:
            trend = trends[0]
            pts   = trend.get("data_points", [])
            if len(pts) >= 3:
                years = [str(dp.get("year","")) for dp in pts]
                vals6 = [_parse_val(dp.get("value",0)) for dp in pts]
                # Colour bars: earlier = lighter, latest = bright accent
                bar_colors = [f"rgba(99,102,241,{0.3 + 0.7*(i/(len(vals6)-1 or 1))})"
                              for i in range(len(vals6))]
                fig6 = go.Figure(go.Bar(
                    x=years, y=vals6,
                    marker=dict(color=bar_colors, line=dict(color="#6366f1",width=1)),
                    text=[f"{v:,.1f}" for v in vals6],
                    textposition="outside",
                    textfont=dict(color=TEXT),
                    hovertemplate="Year %{x}<br>Value: %{y:,.2f}<extra></extra>",
                ))
                fig6.update_layout(**layout_base,
                    title=dict(text=f"📅 Year-on-Year: {trend.get('name','')} ({trend.get('unit','')})",
                               font=dict(color=TITLE,size=16)),
                    xaxis=dict(gridcolor=GRID, title="Year"),
                    yaxis=dict(gridcolor=GRID, title=trend.get("unit","Value")),
                    height=340)
                charts.append(fig6.to_json())
                logs.append("[Viz] ✅ Year-on-year bar chart")

    except ImportError:
        logs.append("[Viz] Plotly not installed — pip install plotly")
    except Exception as e:
        logs.append(f"[Viz] Error: {e}")

    timings["visualization"] = round(time.time() - t0, 2)
    logs.append(f"[Viz] Done — {len(charts)} charts generated.")
    return {"chart_json": charts, "agent_logs": logs, "agent_timings": timings}
