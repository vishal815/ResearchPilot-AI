"""
ResearchPilot AI — Single-Page UI
All sections on one scrollable page with sticky nav.
Fixes: anchor links, SVG via components.html, PDF crash, renamed labels.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import streamlit as st
import streamlit.components.v1 as components

from graph.graph_builder import graph
from tools.pdf_generator import generate_pdf

st.set_page_config(
    page_title="ResearchPilot AI",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ────────────────────────────────────────────────────────
st.markdown("""<style>
/* Base */
.stApp{background:#0f172a;color:#e2e8f0;}
.block-container{padding-top:0;max-width:1120px;}
section[data-testid="stSidebar"]{background:#0b1120;border-right:1px solid #1e293b;}

/* Example query cards */
section[data-testid="stSidebar"] button[kind="secondary"]{
  background:#111827;border:1px solid #1e293b;border-radius:9px;
  font-size:11.5px;font-weight:600;color:#cbd5e1;
  padding:8px 6px;transition:all .15s;text-align:left;
}
section[data-testid="stSidebar"] button[kind="secondary"]:hover{
  background:#1e293b;border-color:#6366f1;color:#a5b4fc;
  transform:translateY(-1px);
}

/* Sticky nav */
#researchpilot-nav{
  position:sticky;top:0;z-index:1000;
  background:#080f1e;
  border-bottom:1px solid #1e293b;
  padding:9px 0 7px 0;
  display:flex;gap:6px;flex-wrap:wrap;
  margin-bottom:0;
}
.nav-pill{
  background:#111827;border:1px solid #1e293b;
  border-radius:22px;padding:6px 20px;
  font-size:12.5px;font-weight:700;
  color:#64748b;cursor:pointer;
  text-decoration:none!important;
  transition:all .18s;letter-spacing:.3px;
  white-space:nowrap;
}
.nav-pill:hover{background:#1e293b;color:#a5b4fc;border-color:#6366f1;}

/* Section wrappers — each has a unique left-border colour */
.sec-wrap{border-radius:14px;padding:28px 26px 22px 26px;margin:22px 0;}
.sec-research  {background:#0d1a2e;border-left:4px solid #6366f1;}
.sec-charts    {background:#0a1a14;border-left:4px solid #10b981;}
.sec-references{background:#130d2e;border-left:4px solid #a78bfa;}
.sec-report    {background:#1a130d;border-left:4px solid #f59e0b;}
.sec-trace     {background:#0d1a1a;border-left:4px solid #06b6d4;}

.sec-title{font-size:1.15rem;font-weight:800;margin:0 0 16px 0;letter-spacing:.3px;}
.t-indigo{color:#a5b4fc;} .t-green{color:#34d399;}
.t-purple{color:#c4b5fd;} .t-amber{color:#fcd34d;} .t-cyan{color:#67e8f9;}

/* Cards */
.kpi-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:16px;}
.kpi{background:#1e293b;border-radius:10px;padding:14px 16px;border:1px solid #334155;}
.kpi-label{font-size:11px;color:#64748b;font-weight:600;letter-spacing:.5px;margin-bottom:4px;}
.kpi-value{font-size:22px;font-weight:800;color:#e2e8f0;}

/* Node pipeline */
.node-done   {display:inline-block;background:#064e3b;color:#34d399;border:1px solid #10b981;border-radius:8px;padding:5px 12px;margin:3px;font-size:11.5px;font-weight:700;}
.node-active {display:inline-block;background:#1c1a0e;color:#f59e0b;border:1px solid #f59e0b;border-radius:8px;padding:5px 12px;margin:3px;font-size:11.5px;font-weight:700;}
.node-pending{display:inline-block;background:#1e293b;color:#475569;border:1px solid #334155;border-radius:8px;padding:5px 12px;margin:3px;font-size:11.5px;font-weight:700;}

/* Cite card */
.cite-card{background:#1e293b;border-left:3px solid #a78bfa;border-radius:8px;padding:10px 14px;margin:8px 0;font-size:12px;}
.cite-card a{color:#818cf8;}

/* Chip */
.chip{display:inline-block;background:#1e293b;border:1px solid #6366f1;border-radius:18px;padding:3px 13px;margin:3px;font-size:11.5px;color:#a5b4fc;}

/* Log */
.log-ok  {color:#10b981;font-size:11.5px;padding:1px 0;}
.log-run {color:#f59e0b;font-size:11.5px;padding:1px 0;}
.log-info{color:#64748b;font-size:11.5px;padding:1px 0;}

/* Score badges */
.badge-hi{background:#064e3b;color:#34d399;border-radius:8px;padding:5px 16px;font-weight:800;font-size:20px;}
.badge-md{background:#451a03;color:#fb923c;border-radius:8px;padding:5px 16px;font-weight:800;font-size:20px;}
.badge-lo{background:#450a0a;color:#f87171;border-radius:8px;padding:5px 16px;font-weight:800;font-size:20px;}

/* VFS expander tweak */
details summary{color:#a5b4fc!important;}

/* Report body */
.rpt h1{color:#fcd34d;font-size:1.45rem;margin-top:8px;}
.rpt h2{color:#a5b4fc;font-size:1.1rem;border-bottom:1px solid #1e293b;padding-bottom:4px;margin-top:18px;}
.rpt p,.rpt li{color:#cbd5e1;line-height:1.75;}
</style>""", unsafe_allow_html=True)


# ── STICKY NAV ─────────────────────────────────────────────────
# Uses JS to inject the nav above Streamlit's own header
st.markdown("""
<div id="researchpilot-nav">
  <a class="nav-pill" href="#sec-research">🔬 Research</a>
  <a class="nav-pill" href="#sec-charts">📊 Data &amp; Charts</a>
  <a class="nav-pill" href="#sec-references">📖 References</a>
  <a class="nav-pill" href="#sec-report">📄 Report</a>
  <a class="nav-pill" href="#sec-trace">⏱️ Trace</a>
</div>
<script>
// Smooth scroll for anchor links inside Streamlit iframe
document.querySelectorAll('a.nav-pill').forEach(a=>{
  a.addEventListener('click',function(e){
    e.preventDefault();
    const id=this.getAttribute('href').slice(1);
    const el=document.getElementById(id);
    if(el){el.scrollIntoView({behavior:'smooth'});}
  });
});
</script>
""", unsafe_allow_html=True)


# ── HEADER ─────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;padding:18px 0 4px 0;">
  <h1 style="color:#a5b4fc;font-size:2.15rem;margin:0;font-weight:900;letter-spacing:-0.5px;">
    🧭 ResearchPilot <span style="color:#6366f1;">AI</span>
  </h1>
  <p style="color:#334155;font-size:.92rem;margin:5px 0 0 0;">
    Autonomous Multi-Agent Research · Router · Statistics · Domain Expert · Fact Checker · Writer
  </p>
</div>
<hr style="border-color:#1e293b;margin:10px 0 0 0;">
""", unsafe_allow_html=True)


# ── SIDEBAR ─────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Options")
    generate_thumbnail = st.toggle("Generate cover card", value=True)

    st.markdown("### 💡 Try a Topic")
    st.markdown(
        "<p style='color:#475569;font-size:11.5px;margin:-6px 0 10px 0'>"
        "Curated picks that showcase rich charts, expert analysis & fact-checking. "
        "Click any card to load it instantly.</p>",
        unsafe_allow_html=True,
    )

    # Curated examples — each one is chosen to trigger multiple agents and
    # produce strong chart-worthy statistics, so a first-time user sees the
    # system at its best.
    EXAMPLES = [
        {"emoji": "🚀", "label": "AI in Healthcare",   "query": "Impact of AI on healthcare market growth: adoption rates, investment trends and future outlook"},
        {"emoji": "📈", "label": "Renewable Energy",   "query": "Global renewable energy adoption trends: solar, wind and investment growth by region"},
        {"emoji": "🤖", "label": "Multi-Agent AI",     "query": "Future of multi-agent AI systems: architecture, real-world adoption and key players"},
        {"emoji": "💰", "label": "AI in Banking",      "query": "AI in banking and financial services: fraud detection, market size and adoption statistics"},
        {"emoji": "⚡", "label": "Electric Vehicles",  "query": "Future of electric vehicles worldwide: sales growth, battery costs and market share by region"},
        {"emoji": "🛡️", "label": "Cybersecurity 2026", "query": "Cybersecurity threat landscape 2026: emerging attack trends, breach costs and industry response"},
        {"emoji": "🎓", "label": "AI in Education",    "query": "AI transformation in education: adoption rates, learning outcomes and classroom case studies"},
        {"emoji": "🌍", "label": "Climate Change",     "query": "Climate change: data, risks and emerging solutions across global regions"},
    ]


    # 2-column grid of clickable example cards
    cols = st.columns(2)
    for idx, ex in enumerate(EXAMPLES):
        with cols[idx % 2]:
            if st.button(
                f"{ex['emoji']} {ex['label']}",
                use_container_width=True,
                key=f"ex_{idx}",
                help=ex["query"],
            ):
                st.session_state["query_input"] = ex["query"]
                st.rerun()

    st.markdown(
        "<div style='margin-top:8px'></div>", unsafe_allow_html=True
    )
    if st.button("🎲 Surprise me", use_container_width=True, key="ex_random"):
        import random
        st.session_state["query_input"] = random.choice(EXAMPLES)["query"]
        st.rerun()

    st.markdown("---")
    st.markdown("### 🤖 Pipeline")
    for icon, name, desc in [
        ("🧠","Planner",    "Query → tasks + domain"),
        ("🔀","Router",     "Decides active agents"),
        ("🔍","Research",   "Deep web intelligence"),
        ("📊","Statistics", "Mine quantitative data"),
        ("🎓","Expert",     "Domain expert analysis"),
        ("✅","FactCheck",  "Verify key claims"),
        ("📖","References", "APA source formatting"),
        ("📈","Viz",        "6 interactive charts"),
        ("🖼️","Cover",     "SVG cover card"),
        ("✍️","Writer",    "Structured report"),
        ("🏆","QualityGate","Score + retry"),
    ]:
        st.markdown(
            f"<div style='background:#111827;border:1px solid #1e293b;border-radius:8px;"
            f"padding:8px 12px;margin:4px 0;font-size:12px;color:#e2e8f0'>"
            f"{icon} <b>{name}</b><br>"
            f"<span style='color:#475569;font-size:10.5px'>{desc}</span></div>",
            unsafe_allow_html=True)

    st.markdown("---")
    if st.session_state.get("rf_has_run"):
        if st.button("🔄 New Research", use_container_width=True):
            for k in list(st.session_state.keys()):
                if k.startswith("rf_") or k.startswith("pdf_cache_"):
                    del st.session_state[k]
            st.rerun()

    st.markdown("### 🔗 Links")
    st.markdown(
        "[👉 GitHub Repo](https://github.com/vishal815) · "
        "[🤝 LinkedIn](https://www.linkedin.com/in/vishal-lazrus/) · "
        "[🌐 Portfolio](https://vishal-lazrus-portfolio.vercel.app/)"
    )


# ── QUERY INPUT ─────────────────────────────────────────────────
col_q, col_btn = st.columns([5, 1])
with col_q:
    query = st.text_input(
        "🔎 Research Topic",
        value=st.session_state.get("query_input",""),
        placeholder="e.g. How is generative AI transforming software development in 2025?",
        key="query_input",
        label_visibility="collapsed",
    )
with col_btn:
    run_btn = st.button("🚀 Research", type="primary", use_container_width=True)

st.markdown("<hr style='border-color:#1e293b;margin:8px 0 0 0;'>", unsafe_allow_html=True)

NODE_ORDER = ["planner","router","workers","visualization","cover","writer","quality_gate"]


def node_pills(completed, current=None):
    labels = {
        "planner":"🧠 Planner","router":"🔀 Router","workers":"⚙️ Workers",
        "visualization":"📈 Viz","cover":"🖼️ Cover",
        "writer":"✍️ Writer","quality_gate":"🏆 Gate",
        "synthesizer":"✍️ Writer","thumbnail":"🖼️ Cover",
    }
    parts = []
    for n in NODE_ORDER:
        lbl = labels.get(n, n)
        if n in completed:   parts.append(f"<span class='node-done'>✅ {lbl}</span>")
        elif n == current:   parts.append(f"<span class='node-active'>⚡ {lbl}</span>")
        else:                parts.append(f"<span class='node-pending'>○ {lbl}</span>")
    return "<div style='line-height:2.6'>" + " ".join(parts) + "</div>"


def log_class(l):
    return "log-ok" if "Done" in l or "✅" in l else (
           "log-run" if any(x in l for x in ["Starting","Searching","Mining","Building","Applying","Evaluating","Merging","Generating","Verifying","Formatting"]) else
           "log-info")


# ──────────────────────────────────────────────────────────────
#  PIPELINE RUN — cached in session_state so download clicks
#  (which trigger a Streamlit rerun) don't re-run the agents.
# ──────────────────────────────────────────────────────────────
if run_btn and query.strip():
    st.session_state["rf_query"] = query
    st.session_state["rf_has_run"] = True
    st.session_state.pop("rf_final", None)   # force fresh run

should_run_pipeline = (
    st.session_state.get("rf_has_run", False)
    and "rf_final" not in st.session_state
)

if should_run_pipeline:

    initial = {
        "query":query,"todos":[],"research_plan":"",
        "active_agents":[],"topic_domain":"general",
        "virtual_files":{},"structured_data":{},"citations":[],
        "chart_json":[],"thumbnail_svg":None,
        "final_report":"","quality_score":0.0,
        "retry_count":0,"agent_logs":[],"agent_timings":{},
        "generate_thumbnail":generate_thumbnail,
    }
    completed, final = [], dict(initial)

    # ── SECTION 1: RESEARCH (live) ────────────────────────────
    st.markdown('<a id="sec-research"></a>', unsafe_allow_html=True)
    st.markdown('<div class="sec-wrap sec-research">', unsafe_allow_html=True)
    st.markdown('<div class="sec-title t-indigo">🔬 Research — Live Pipeline</div>', unsafe_allow_html=True)

    status_box = st.empty()
    graph_box  = st.empty()
    agent_box  = st.empty()

    with st.spinner("ResearchPilot AI is working..."):
        for update in graph.stream(initial):
            node_name = list(update.keys())[0]
            node_data  = update[node_name]
            completed.append(node_name)
            for k, v in node_data.items():
                if v is not None:
                    final[k] = v

            logs   = final.get("agent_logs", [])
            active = final.get("active_agents", [])

            recent = logs[-6:]
            log_html = "".join(
                f"<div class='{log_class(l)}'>→ {l}</div>" for l in recent
            )
            status_box.markdown(
                f"<div style='background:#111827;border-radius:10px;padding:12px 16px;"
                f"border:1px solid #1e293b'>"
                f"<b style='color:#f59e0b'>⚡ Running: {node_name}</b>"
                f"<div style='margin-top:8px'>{log_html}</div></div>",
                unsafe_allow_html=True,
            )
            graph_box.markdown(node_pills(completed, node_name), unsafe_allow_html=True)
            if active:
                chips = "".join(f"<span class='chip'>🤖 {a}</span>" for a in active)
                agent_box.markdown(
                    f"<div style='margin:6px 0'><span style='color:#475569;font-size:11px'>"
                    f"Active agents:</span> {chips}</div>",
                    unsafe_allow_html=True,
                )

    # ── Save to session_state so download-button reruns reuse it ──
    st.session_state["rf_final"] = final
    st.session_state["rf_completed"] = completed

    # Metrics row
    score  = final.get("quality_score", 0)
    active = final.get("active_agents", [])
    domain = final.get("topic_domain", "general")
    vfs    = final.get("virtual_files", {})
    sc_cls = "badge-hi" if score>=7 else ("badge-md" if score>=4 else "badge-lo")

    st.markdown(
        f"<div class='kpi-grid'>"
        f"<div class='kpi'><div class='kpi-label'>DOMAIN</div><div class='kpi-value'>{domain.upper()}</div></div>"
        f"<div class='kpi'><div class='kpi-label'>AGENTS USED</div><div class='kpi-value'>{len(active)}</div></div>"
        f"<div class='kpi'><div class='kpi-label'>QUALITY SCORE</div><div class='kpi-value'><span class='{sc_cls}'>{score:.1f}/10</span></div></div>"
        f"</div>",
        unsafe_allow_html=True,
    )

    # VFS files
    if vfs:
        st.markdown("**📁 Agent Outputs**")
        for fname, content in vfs.items():
            icon = "📊" if "csv" in fname else ("🔍" if "research" in fname else ("📖" if "ref" in fname or "cite" in fname else "📄"))
            with st.expander(f"{icon} {fname}"):
                if fname.endswith(".csv"):
                    try:
                        import pandas as pd, io
                        df = pd.read_csv(io.StringIO(content))
                        st.dataframe(df, use_container_width=True)
                    except Exception:
                        st.text_area("", content, height=150, disabled=True, key=f"vfs_{fname}")
                else:
                    st.text_area("", content, height=160, disabled=True, key=f"vfs_{fname}")

    with st.expander("📋 Full Agent Log"):
        for l in final.get("agent_logs", []):
            st.markdown(f"<div class='{log_class(l)}'>→ {l}</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)  # close sec-wrap


    # ── SECTION 2: DATA & CHARTS ───────────────────────────────
    st.markdown('<a id="sec-charts"></a>', unsafe_allow_html=True)
    st.markdown('<div class="sec-wrap sec-charts">', unsafe_allow_html=True)
    st.markdown('<div class="sec-title t-green">📊 Data & Charts</div>', unsafe_allow_html=True)

    chart_list = final.get("chart_json", [])
    structured = final.get("structured_data", {})

    if chart_list:
        try:
            import plotly.graph_objects as go
            # Show charts in 2-column grid where possible
            c_pairs = [chart_list[i:i+2] for i in range(0, len(chart_list), 2)]
            for pair in c_pairs:
                if len(pair) == 2:
                    ca, cb = st.columns(2)
                    with ca:
                        st.plotly_chart(go.Figure(json.loads(pair[0])),
                                        use_container_width=True, key=f"c{chart_list.index(pair[0])}")
                    with cb:
                        st.plotly_chart(go.Figure(json.loads(pair[1])),
                                        use_container_width=True, key=f"c{chart_list.index(pair[1])}")
                else:
                    st.plotly_chart(go.Figure(json.loads(pair[0])),
                                    use_container_width=True, key=f"c{chart_list.index(pair[0])}")
        except ImportError:
            st.warning("Install plotly: `pip install plotly`")
    else:
        st.info("No charts — Statistics agent was not activated for this topic.")

    # CSV download
    csv_data = vfs.get("statistics_data.csv","")
    if csv_data:
        col_csv1, col_csv2 = st.columns([1,4])
        with col_csv1:
            st.download_button("⬇️ Download CSV", data=csv_data,
                file_name="researchpilot_data.csv", mime="text/csv",
                use_container_width=True, key="csv_dl_first")
        with col_csv2:
            if structured.get("summary"):
                st.markdown(f"> 📝 {structured['summary']}")

    if structured.get("metrics"):
        st.markdown("**🔢 Data Table**")
        import pandas as pd
        df = pd.DataFrame(structured["metrics"])
        st.dataframe(df, use_container_width=True, hide_index=True)

    # Cover thumbnail
    thumb = final.get("thumbnail_svg")
    if thumb:
        st.markdown("**🖼️ Cover Card**")
        components.html(
            f'<div style="background:#0f172a;padding:8px;border-radius:12px;'
            f'border:1px solid #1e293b">{thumb}</div>',
            height=460, scrolling=False,
        )

    st.markdown("</div>", unsafe_allow_html=True)


    # ── SECTION 3: REFERENCES ─────────────────────────────────
    st.markdown('<a id="sec-references"></a>', unsafe_allow_html=True)
    st.markdown('<div class="sec-wrap sec-references">', unsafe_allow_html=True)
    st.markdown('<div class="sec-title t-purple">📖 References</div>', unsafe_allow_html=True)

    citations = final.get("citations", [])
    if citations:
        st.markdown(f"<p style='color:#64748b;font-size:13px'>{len(citations)} sources found</p>",
                    unsafe_allow_html=True)
        for c in citations:
            url  = c.get("url","")
            link = f'<a href="{url}" target="_blank" style="font-size:11px">{url[:70]}…</a>' if url else ""
            st.markdown(
                f"<div class='cite-card'>"
                f"<b style='color:#c4b5fd'>[{c.get('number','')}]</b> "
                f"<b style='color:#e2e8f0'>{c.get('title','')}</b><br>"
                f"<span style='color:#64748b'>{c.get('apa','')}</span><br>{link}"
                f"</div>",
                unsafe_allow_html=True,
            )
    else:
        ref_text = vfs.get("references.txt","")
        if ref_text and ref_text != "No references extracted.":
            st.markdown(ref_text)
        else:
            st.info("No references extracted for this topic.")

    st.markdown("</div>", unsafe_allow_html=True)


    # ── SECTION 4: REPORT ─────────────────────────────────────
    st.markdown('<a id="sec-report"></a>', unsafe_allow_html=True)
    st.markdown('<div class="sec-wrap sec-report">', unsafe_allow_html=True)
    st.markdown('<div class="sec-title t-amber">📄 Report</div>', unsafe_allow_html=True)

    report = final.get("final_report","")
    if report:
        st.markdown(f'<div class="rpt">{report}</div>', unsafe_allow_html=True)
        st.markdown("---")
        dl1, dl2 = st.columns(2)
        with dl1:
            st.download_button(
                "⬇️ Download Markdown", data=report,
                file_name=f"researchpilot_{query[:28].replace(' ','_')}.md",
                mime="text/markdown", use_container_width=True, key="md_dl_first",
            )
        with dl2:
            pdf_key = f"pdf_cache_{hash(report) % 100000}"
            if pdf_key not in st.session_state:
                with st.spinner("Building PDF..."):
                    st.session_state[pdf_key] = generate_pdf(
                        report=report, query=query,
                        quality_score=final.get("quality_score",0),
                        citations=final.get("citations",[]),
                        chart_json_list=final.get("chart_json",[]),
                        thumbnail_svg=None,
                        active_agents=final.get("active_agents",[]),
                    )
            pdf_bytes = st.session_state[pdf_key]
            if pdf_bytes:
                st.download_button(
                    "⬇️ Download PDF", data=pdf_bytes,
                    file_name=f"researchpilot_{query[:28].replace(' ','_')}.pdf",
                    mime="application/pdf", use_container_width=True, key="pdf_dl_first",
                )
            else:
                st.caption("PDF needs fpdf2: `pip install fpdf2`")

    st.markdown("</div>", unsafe_allow_html=True)


    # ── SECTION 5: TRACE ──────────────────────────────────────
    st.markdown('<a id="sec-trace"></a>', unsafe_allow_html=True)
    st.markdown('<div class="sec-wrap sec-trace">', unsafe_allow_html=True)
    st.markdown('<div class="sec-title t-cyan">⏱️ Trace</div>', unsafe_allow_html=True)

    timings = final.get("agent_timings",{})
    if timings:
        try:
            import plotly.graph_objects as go
            fig_t = go.Figure(go.Bar(
                x=list(timings.keys()),
                y=list(timings.values()),
                marker=dict(color=["#6366f1","#8b5cf6","#34d399","#f59e0b",
                                   "#06b6d4","#ef4444","#10b981"][:len(timings)],
                            line=dict(color="#0f172a",width=1)),
                text=[f"{v:.1f}s" for v in timings.values()],
                textposition="outside", textfont=dict(color="#e2e8f0"),
                hovertemplate="%{x}: %{y:.2f}s<extra></extra>",
            ))
            fig_t.update_layout(
                title=dict(text="Node Execution Time (seconds)",font=dict(color="#67e8f9",size=15)),
                plot_bgcolor="#0d1a1a", paper_bgcolor="#0d1a1a",
                font=dict(color="#e2e8f0"),
                xaxis=dict(gridcolor="#1e293b"),
                yaxis=dict(gridcolor="#1e293b", title="Seconds"),
                margin=dict(l=20,r=20,t=50,b=20), height=300,
            )
            st.plotly_chart(fig_t, use_container_width=True, key="timing_chart")
        except ImportError:
            for k,v in timings.items():
                st.write(f"`{k}`: {v:.2f}s")

    total = sum(timings.values()) if timings else 0
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("⏱ Total Time",   f"{total:.1f}s")
    c2.metric("🌐 Domain",       domain.upper())
    c3.metric("🤖 Agents",       len(active))
    c4.metric("🔁 Retries",      final.get("retry_count",0))

    langsmith = os.getenv("LANGCHAIN_API_KEY","")
    if langsmith:
        st.markdown("**[🔗 View LangSmith Trace →](https://smith.langchain.com)**")
    else:
        st.info("Add `LANGCHAIN_API_KEY` to .env to enable LangSmith traces at smith.langchain.com")

    st.markdown("</div>", unsafe_allow_html=True)

    st.divider()
    st.markdown("### 🔗 Links")
    st.markdown(
        "[👉 GitHub Repo](https://github.com/vishal815) · "
        "[🤝 LinkedIn](https://www.linkedin.com/in/vishal-lazrus/) · "
        "[🌐 Portfolio](https://vishal-lazrus-portfolio.vercel.app/)"
    )

elif run_btn and not query.strip():
    st.warning("Please enter a research topic.")

elif st.session_state.get("rf_has_run") and "rf_final" in st.session_state:
    # ── Rerun triggered by a download button — reuse cached result, skip re-running agents ──
    final     = st.session_state["rf_final"]
    completed = st.session_state.get("rf_completed", [])
    query     = st.session_state.get("rf_query", query)

    score  = final.get("quality_score", 0)
    active = final.get("active_agents", [])
    domain = final.get("topic_domain", "general")
    vfs    = final.get("virtual_files", {})
    sc_cls = "badge-hi" if score>=7 else ("badge-md" if score>=4 else "badge-lo")

    # ── SECTION 1: RESEARCH (cached summary, no re-streaming) ─
    st.markdown('<a id="sec-research"></a>', unsafe_allow_html=True)
    st.markdown('<div class="sec-wrap sec-research">', unsafe_allow_html=True)
    st.markdown('<div class="sec-title t-indigo">🔬 Research — Pipeline Summary</div>', unsafe_allow_html=True)
    st.markdown(node_pills(completed, None), unsafe_allow_html=True)
    if active:
        chips = "".join(f"<span class='chip'>🤖 {a}</span>" for a in active)
        st.markdown(f"<div style='margin:6px 0'><span style='color:#475569;font-size:11px'>Active agents:</span> {chips}</div>", unsafe_allow_html=True)

    st.markdown(
        f"<div class='kpi-grid'>"
        f"<div class='kpi'><div class='kpi-label'>DOMAIN</div><div class='kpi-value'>{domain.upper()}</div></div>"
        f"<div class='kpi'><div class='kpi-label'>AGENTS USED</div><div class='kpi-value'>{len(active)}</div></div>"
        f"<div class='kpi'><div class='kpi-label'>QUALITY SCORE</div><div class='kpi-value'><span class='{sc_cls}'>{score:.1f}/10</span></div></div>"
        f"</div>",
        unsafe_allow_html=True,
    )
    if vfs:
        st.markdown("**📁 Agent Outputs**")
        for fname, content in vfs.items():
            icon = "📊" if "csv" in fname else ("🔍" if "research" in fname else ("📖" if "ref" in fname or "cite" in fname else "📄"))
            with st.expander(f"{icon} {fname}"):
                if fname.endswith(".csv"):
                    try:
                        import pandas as pd, io
                        df = pd.read_csv(io.StringIO(content))
                        st.dataframe(df, use_container_width=True)
                    except Exception:
                        st.text_area("", content, height=150, disabled=True, key=f"vfs_cached_{fname}")
                else:
                    st.text_area("", content, height=160, disabled=True, key=f"vfs_cached_{fname}")
    with st.expander("📋 Full Agent Log"):
        for l in final.get("agent_logs", []):
            st.markdown(f"<div class='{log_class(l)}'>→ {l}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # ── SECTION 2: DATA & CHARTS ───────────────────────────────
    st.markdown('<a id="sec-charts"></a>', unsafe_allow_html=True)
    st.markdown('<div class="sec-wrap sec-charts">', unsafe_allow_html=True)
    st.markdown('<div class="sec-title t-green">📊 Data & Charts</div>', unsafe_allow_html=True)

    chart_list = final.get("chart_json", [])
    structured = final.get("structured_data", {})
    if chart_list:
        try:
            import plotly.graph_objects as go
            c_pairs = [chart_list[i:i+2] for i in range(0, len(chart_list), 2)]
            for pair in c_pairs:
                if len(pair) == 2:
                    ca, cb = st.columns(2)
                    with ca:
                        st.plotly_chart(go.Figure(json.loads(pair[0])), use_container_width=True, key=f"cc{chart_list.index(pair[0])}")
                    with cb:
                        st.plotly_chart(go.Figure(json.loads(pair[1])), use_container_width=True, key=f"cc{chart_list.index(pair[1])}")
                else:
                    st.plotly_chart(go.Figure(json.loads(pair[0])), use_container_width=True, key=f"cc{chart_list.index(pair[0])}")
        except ImportError:
            st.warning("Install plotly: `pip install plotly`")
    else:
        st.info("No charts — Statistics agent was not activated for this topic.")

    csv_data = vfs.get("statistics_data.csv","")
    if csv_data:
        col_csv1, col_csv2 = st.columns([1,4])
        with col_csv1:
            st.download_button("⬇️ Download CSV", data=csv_data,
                file_name="researchpilot_data.csv", mime="text/csv",
                use_container_width=True, key="csv_dl_cached")
        with col_csv2:
            if structured.get("summary"):
                st.markdown(f"> 📝 {structured['summary']}")
    if structured.get("metrics"):
        st.markdown("**🔢 Data Table**")
        import pandas as pd
        df = pd.DataFrame(structured["metrics"])
        st.dataframe(df, use_container_width=True, hide_index=True)

    thumb = final.get("thumbnail_svg")
    if thumb:
        st.markdown("**🖼️ Cover Card**")
        components.html(
            f'<div style="background:#0f172a;padding:8px;border-radius:12px;'
            f'border:1px solid #1e293b">{thumb}</div>',
            height=460, scrolling=False,
        )
    st.markdown("</div>", unsafe_allow_html=True)

    # ── SECTION 3: REFERENCES ─────────────────────────────────
    st.markdown('<a id="sec-references"></a>', unsafe_allow_html=True)
    st.markdown('<div class="sec-wrap sec-references">', unsafe_allow_html=True)
    st.markdown('<div class="sec-title t-purple">📖 References</div>', unsafe_allow_html=True)
    citations = final.get("citations", [])
    if citations:
        st.markdown(f"<p style='color:#64748b;font-size:13px'>{len(citations)} sources found</p>", unsafe_allow_html=True)
        for c in citations:
            url  = c.get("url","")
            link = f'<a href="{url}" target="_blank" style="font-size:11px">{url[:70]}…</a>' if url else ""
            st.markdown(
                f"<div class='cite-card'>"
                f"<b style='color:#c4b5fd'>[{c.get('number','')}]</b> "
                f"<b style='color:#e2e8f0'>{c.get('title','')}</b><br>"
                f"<span style='color:#64748b'>{c.get('apa','')}</span><br>{link}"
                f"</div>",
                unsafe_allow_html=True,
            )
    else:
        ref_text = vfs.get("references.txt","")
        if ref_text and ref_text != "No references extracted.":
            st.markdown(ref_text)
        else:
            st.info("No references extracted for this topic.")
    st.markdown("</div>", unsafe_allow_html=True)

    # ── SECTION 4: REPORT ─────────────────────────────────────
    st.markdown('<a id="sec-report"></a>', unsafe_allow_html=True)
    st.markdown('<div class="sec-wrap sec-report">', unsafe_allow_html=True)
    st.markdown('<div class="sec-title t-amber">📄 Report</div>', unsafe_allow_html=True)
    report = final.get("final_report","")
    if report:
        st.markdown(f'<div class="rpt">{report}</div>', unsafe_allow_html=True)
        st.markdown("---")
        dl1, dl2 = st.columns(2)
        with dl1:
            st.download_button(
                "⬇️ Download Markdown", data=report,
                file_name=f"researchpilot_{query[:28].replace(' ','_')}.md",
                mime="text/markdown", use_container_width=True, key="md_dl_cached",
            )
        with dl2:
            pdf_key = f"pdf_cache_{hash(report) % 100000}"
            if pdf_key not in st.session_state:
                with st.spinner("Building PDF..."):
                    st.session_state[pdf_key] = generate_pdf(
                        report=report, query=query,
                        quality_score=final.get("quality_score",0),
                        citations=final.get("citations",[]),
                        chart_json_list=final.get("chart_json",[]),
                        thumbnail_svg=None,
                        active_agents=final.get("active_agents",[]),
                    )
            pdf_bytes = st.session_state[pdf_key]
            if pdf_bytes:
                st.download_button(
                    "⬇️ Download PDF", data=pdf_bytes,
                    file_name=f"researchpilot_{query[:28].replace(' ','_')}.pdf",
                    mime="application/pdf", use_container_width=True, key="pdf_dl_cached",
                )
            else:
                st.caption("PDF needs fpdf2: `pip install fpdf2`")
    st.markdown("</div>", unsafe_allow_html=True)

    # ── SECTION 5: TRACE ──────────────────────────────────────
    st.markdown('<a id="sec-trace"></a>', unsafe_allow_html=True)
    st.markdown('<div class="sec-wrap sec-trace">', unsafe_allow_html=True)
    st.markdown('<div class="sec-title t-cyan">⏱️ Trace</div>', unsafe_allow_html=True)
    timings = final.get("agent_timings",{})
    if timings:
        try:
            import plotly.graph_objects as go
            fig_t = go.Figure(go.Bar(
                x=list(timings.keys()), y=list(timings.values()),
                marker=dict(color=["#6366f1","#8b5cf6","#34d399","#f59e0b","#06b6d4","#ef4444","#10b981"][:len(timings)],
                            line=dict(color="#0f172a",width=1)),
                text=[f"{v:.1f}s" for v in timings.values()],
                textposition="outside", textfont=dict(color="#e2e8f0"),
                hovertemplate="%{x}: %{y:.2f}s<extra></extra>",
            ))
            fig_t.update_layout(
                title=dict(text="Node Execution Time (seconds)",font=dict(color="#67e8f9",size=15)),
                plot_bgcolor="#0d1a1a", paper_bgcolor="#0d1a1a",
                font=dict(color="#e2e8f0"),
                xaxis=dict(gridcolor="#1e293b"), yaxis=dict(gridcolor="#1e293b", title="Seconds"),
                margin=dict(l=20,r=20,t=50,b=20), height=300,
            )
            st.plotly_chart(fig_t, use_container_width=True, key="timing_chart_cached")
        except ImportError:
            for k,v in timings.items():
                st.write(f"`{k}`: {v:.2f}s")
    total = sum(timings.values()) if timings else 0
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("⏱ Total Time", f"{total:.1f}s")
    c2.metric("🌐 Domain", domain.upper())
    c3.metric("🤖 Agents", len(active))
    c4.metric("🔁 Retries", final.get("retry_count",0))
    langsmith = os.getenv("LANGCHAIN_API_KEY","")
    if langsmith:
        st.markdown("**[🔗 View LangSmith Trace →](https://smith.langchain.com)**")
    else:
        st.info("Add `LANGCHAIN_API_KEY` to .env to enable LangSmith traces at smith.langchain.com")
    st.markdown("</div>", unsafe_allow_html=True)

    st.divider()
    st.markdown("### 🔗 Links")
    st.markdown(
        "[👉 GitHub Repo](https://github.com/vishal815) · "
        "[🤝 LinkedIn](https://www.linkedin.com/in/vishal-lazrus/) · "
        "[🌐 Portfolio](https://vishal-lazrus-portfolio.vercel.app/)"
    )

else:
    # Landing placeholders — one per section, each styled distinctly
    for anchor, sec_cls, title_cls, icon, title, desc in [
        ("sec-research",  "sec-research",   "t-indigo", "🔬", "Research",      "Live agent pipeline, domain detection, VFS file browser"),
        ("sec-charts",    "sec-charts",     "t-green",  "📊", "Data & Charts", "6 interactive Plotly charts + CSV export + cover card"),
        ("sec-references","sec-references", "t-purple", "📖", "References",    "APA-formatted sources extracted from the web"),
        ("sec-report",    "sec-report",     "t-amber",  "📄", "Report",        "Full structured report — Markdown + PDF download"),
        ("sec-trace",     "sec-trace",      "t-cyan",   "⏱️", "Trace",         "Per-node timing chart + LangSmith integration"),
    ]:
        st.markdown(f'<a id="{anchor}"></a>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="sec-wrap {sec_cls}" style="opacity:0.45">'
            f'<div class="sec-title {title_cls}">{icon} {title}</div>'
            f'<p style="color:#475569;font-size:13px;margin:0">{desc}</p>'
            f'</div>',
            unsafe_allow_html=True,
        )
    st.markdown("---")
    st.markdown("### 🔗 Links")
    st.markdown(
        "[👉 GitHub Repo](https://github.com/vishal815) · "
        "[🤝 LinkedIn](https://www.linkedin.com/in/vishal-lazrus/) · "
        "[🌐 Portfolio](https://vishal-lazrus-portfolio.vercel.app/)"
    )
