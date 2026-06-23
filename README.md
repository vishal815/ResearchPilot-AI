<div align="center">

# 🧭 ResearchPilot AI

### Autonomous Multi-Agent Research System

**Give it a topic → Get a complete, evidence-backed research report with charts, citations, and PDF export.**

ResearchPilot AI runs a coordinated team of specialised AI agents — each with a focused job — orchestrated by LangGraph. It plans, routes, searches, analyses, fact-checks, visualises, writes, and self-grades, all from one query.

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://python.org)
[![LangGraph](https://img.shields.io/badge/LangGraph-Orchestration-7C3AED)](https://langchain-ai.github.io/langgraph/)
[![Groq](https://img.shields.io/badge/Groq-Llama_3.3_70B-F97316)](https://groq.com)
[![Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io)
[![Plotly](https://img.shields.io/badge/Charts-Plotly-3F4F75)](https://plotly.com)
[![ReportLab](https://img.shields.io/badge/PDF-ReportLab-1E3A5F)](https://www.reportlab.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-22C55E)](LICENSE)

[🚀 Live Demo](#) · [📄 Report Sample](#) · [👨‍💻 Portfolio](https://vishal-lazrus-portfolio.vercel.app/)

</div>

---

## 📌 Table of Contents

| # | Section |
|---|---|
| 1 | [What is ResearchPilot AI?](#-what-is-researchpilot-ai) |
| 2 | [What Makes It Different](#-what-makes-it-different) |
| 3 | [Architecture](#-architecture) |
| 4 | [How It Works — Real Example](#-how-it-works--real-example) |
| 5 | [Folder Structure](#-folder-structure) |
| 6 | [The Five Agents](#-the-five-agents) |
| 7 | [The Six Chart Types](#-the-six-chart-types) |
| 8 | [Getting API Keys (Free)](#-getting-api-keys-free) |
| 9 | [Installation & Setup](#-installation--setup) |
| 10 | [Running the Project](#-running-the-project) |
| 11 | [Deploy to Hugging Face Spaces](#-deploy-to-hugging-face-spaces) |
| 12 | [Concepts Covered](#-concepts-covered) |
| 13 | [Troubleshooting](#-troubleshooting) |
| 14 | [Roadmap](#-roadmap) |
| 15 | [Connect With Me](#-connect-with-me) |

---

## 🤔 What is ResearchPilot AI?

ResearchPilot AI is a **multi-agent AI research system** built with LangGraph. You type one query — say, *"Impact of AI on healthcare market growth"* — and it autonomously runs an 8-node pipeline:

```
Query → Plan → Route → Research + Analyse → Visualise → Write → Grade → Deliver
```

The system produces:
- ✅ A **structured markdown report** (Executive Summary → Key Findings → Analysis → Expert Perspective → Conclusion → References)
- 📊 Up to **6 interactive Plotly charts** generated from real statistical data
- 📄 A **professional academic PDF** with embedded charts and APA citations
- 🗂️ A **CSV file** of the raw statistics for further analysis

> This is not a chatbot wrapper. It implements the **planner → router → workers → critic** pattern used in production agentic AI systems.

### Who is this for?

| 🎓 Students | 💼 Professionals | 🧑‍💻 Developers |
|---|---|---|
| Research papers, literature reviews, assignment prep | Market research, competitive analysis, technology evaluation | Learn LangGraph, conditional routing, agentic design patterns |

---

## ✨ What Makes It Different

| Feature | What it does |
|---|---|
| 🔀 **Dynamic Router Agent** | One LLM call decides *per-query* which of 5 specialist agents to activate. A history question never wastes time running a Statistics agent. A finance query gets Fact Checker. Nothing runs unless it adds value. |
| 📊 **Statistics → Charts pipeline** | The Statistics agent returns *structured JSON* (not prose) — metrics, time-series, regional breakdowns — which directly drives 6 Plotly chart types with no extra LLM calls. |
| 🎓 **Persona-driven Domain Expert** | Adopts a credentialed persona per domain ("Dr. Sarah Chen, Harvard physician" for healthcare; "Marcus Reid, ex-Goldman analyst" for finance) — sharper than a generic "you are an expert" prompt. |
| ✅ **Dedicated Fact Checker** | Extracts specific claims, runs independent search evidence per claim, labels each: Verified / Partially True / Disputed / Unverifiable. |
| 🏆 **Self-grading + auto-retry** | Quality Gate scores the report 0–10 against five weighted criteria. Below 7 → automatic retry with explicit feedback. Capped at 2 retries to prevent runaway cost. |
| 🖼️ **Cover runs after scoring** | The SVG cover card is generated *last* — after Quality Gate — so it always shows the real quality score, not zero. |
| 📄 **ReportLab academic PDF** | Flowable single-column layout, deep-blue academic headings, horizontal rule separators, charts embedded directly under their matching report section. |

---

## 🏗️ Architecture

> **Exact node execution order as wired in `graph/graph_builder.py`:**

```
                    ┌─────────────────────────────────┐
                    │         USER QUERY               │
                    └────────────────┬────────────────┘
                                     │
                                     ▼
                          ┌──────────────────┐
                          │    🧠 PLANNER    │
                          │                  │
                          │ • Detects domain │
                          │ • Builds 3 tasks │
                          └────────┬─────────┘
                                   │
                                   ▼
                          ┌──────────────────┐
                          │    🔀 ROUTER     │
                          │                  │
                          │ Single LLM call  │
                          │ → active_agents  │
                          │   list in state  │
                          └────────┬─────────┘
                                   │
                                   ▼
     ┌─────────────────────────────────────────────────────────┐
     │                  ⚙️ WORKERS NODE                        │
     │           Only activated agents run                      │
     │                                                          │
     │  ┌────────────┐  ┌────────────┐  ┌──────────────────┐   │
     │  │ 🔍Research │  │ 📊Stats    │  │ 🎓Domain Expert  │   │
     │  │            │  │            │  │                  │   │
     │  │ 3 Tavily   │  │ Structured │  │ Persona prompt   │   │
     │  │ searches   │  │ JSON →     │  │ per domain       │   │
     │  │ → LLM      │  │ chart data │  │                  │   │
     │  └─────┬──────┘  └─────┬──────┘  └────────┬─────────┘   │
     │        │               │                   │             │
     │  ┌─────┴──────┐  ┌─────┴──────┐           │             │
     │  │ ✅Fact     │  │ 📖Refs     │           │             │
     │  │ Checker    │  │            │           │             │
     │  │ Claim-by-  │  │ APA format │           │             │
     │  │ claim      │  │ citations  │           │             │
     │  └─────┬──────┘  └─────┬──────┘           │             │
     │        │               │                   │             │
     │        └───────────────┴──────┬────────────┘             │
     │                    Virtual File System                    │
     │              (shared dict living in state)                │
     └───────────────────────────┬─────────────────────────────┘
                                 │
                                 ▼
                      ┌──────────────────┐
                      │  📈 VISUALIZATION │
                      │                  │
                      │ Statistics JSON  │
                      │ → 6 Plotly charts│
                      │ (no LLM call)    │
                      └────────┬─────────┘
                               │
                               ▼
                      ┌──────────────────┐
                      │   ✍️ WRITER      │
                      │                  │
                      │ Reads all 5 VFS  │
                      │ files → builds   │
                      │ final report     │
                      └────────┬─────────┘
                               │
                               ▼
                      ┌──────────────────┐
             ┌────────┤  🏆 QUALITY GATE │◄────────────────────┐
             │        │                  │                      │
             │        │ LLM scores 0-10  │                      │
             │        └────────┬─────────┘                      │
             │                 │                                 │
             │    score ≥ 7    │    score < 7 (max 2 retries)    │
             │        ┌────────┘        └──────────────────────► Writer
             │        ▼
             │ ┌──────────────────┐
             │ │   🖼️ COVER       │
             │ │                  │
             │ │ SVG card with    │
             │ │ real score baked │
             │ │ in (runs last)   │
             │ └────────┬─────────┘
             │          │
             └──────────┘
                        │
                        ▼
                    STREAMLIT UI
          ┌────────────────────────────────┐
          │ 🔬 Research  │ 📊 Data&Charts  │
          │ 📖 References│ 📄 Report       │
          │              │ ⏱️ Trace        │
          └────────────────────────────────┘
                 MD · CSV · PDF downloads
```

---

## ⚡ How It Works — Real Example

**Query typed:** `"Impact of AI on healthcare market growth: adoption rates, investment trends and future outlook"`

| Step | Node | What happens |
|---|---|---|
| 1 | **Planner** | Detects `topic_domain = "healthcare"`. Creates tasks: search clinical data, find market numbers, locate key organisations. |
| 2 | **Router** | One LLM call → `["research", "statistics", "domain_expert", "fact_checker", "citation"]`. All 5 activate because healthcare needs everything. |
| 3a | **Research** | Runs 3 Tavily searches: raw query + "latest developments 2025" + "key findings evidence". LLM synthesises into structured deep-research. Writes `research_deep.txt` to VFS. |
| 3b | **Statistics** | Searches for "$45B market size", "29% CAGR" etc. Forces LLM to return exact JSON schema (metrics array + trends array + comparisons array). Writes `statistics.txt` + `statistics_data.csv`. |
| 3c | **Domain Expert** | Persona: *"Dr. Sarah Chen, Harvard-trained physician"*. Reads `research_deep.txt`, adds clinical nuance. Writes `expert_analysis.txt`. |
| 3d | **Fact Checker** | Extracts 6 specific claims. Verifies 4 individually via fresh Tavily searches. Labels ✅/⚠️/❌. Writes `fact_check.txt`. |
| 3e | **References** | Formats all sources from `raw_search.txt` into APA JSON. Writes `references.txt`. Returns structured `citations` list. |
| 4 | **Visualization** | No LLM call. Reads `structured_data` dict → builds 6 Plotly figures → stores as JSON strings in `chart_json`. |
| 5 | **Writer** | Checks each VFS key. Builds context from whichever files exist. One large LLM call produces 9-section markdown report. |
| 6 | **Quality Gate** | LLM scores the report: **7.5/10**. `should_retry()` returns `"done"`. Routes to Cover. |
| 7 | **Cover** | Now has `quality_score = 7.5`. Generates SVG card with real score baked in. |
| **End** | **UI** | 5 sections rendered. Download MD + CSV + PDF available. |

---

## 📁 Folder Structure

```
ResearchPilot AI/                   ← root folder
│
├── graph/                          ← LangGraph nodes (the "brain")
│   ├── __init__.py
│   ├── state.py                    ← ResearchState TypedDict — shared memory
│   │                                  every node reads from and writes to
│   ├── llm_factory.py              ← get_llm() — Groq primary, Gemini fallback
│   │                                  every node imports this, never hardcodes
│   ├── planner.py                  ← Node 1: detects domain, builds task list
│   ├── router.py                   ← Node 2: LLM → active_agents list
│   ├── workers.py                  ← Node 3: all 5 specialist agents
│   │                                  conditionally called by if "agent" in active_agents
│   ├── visualization.py            ← Node 4: structured_data JSON → 6 Plotly charts
│   │                                  (no LLM call — pure Python/Plotly)
│   ├── synthesizer.py              ← Node 5 (displayed as "Writer"):
│   │                                  reads VFS → one LLM call → final report
│   ├── quality_gate.py             ← Node 6: scores report + should_retry() function
│   │                                  drives the conditional edge / retry loop
│   ├── thumbnail.py                ← Node 7 (displayed as "Cover"):
│   │                                  runs AFTER quality_gate so score exists
│   └── graph_builder.py            ← Wires all 7 nodes + edges + conditional edge
│                                      into one compiled StateGraph object
│
├── tools/                          ← Utilities used by nodes (not nodes themselves)
│   ├── __init__.py
│   ├── search_tool.py              ← web_search() wraps Tavily API
│   │                                  returns plain string for LLM context
│   ├── file_system.py              ← vfs_write() / vfs_read() helpers
│   │                                  copy-on-write to keep state immutable
│   └── pdf_generator.py            ← ReportLab flowable PDF
│                                      strips duplicate References section,
│                                      embeds charts under matching headings
│
├── ui/
│   └── app.py                      ← Single-page Streamlit UI (~800 lines)
│                                      st.session_state caches results so
│                                      download clicks don't re-run the pipeline
│
├── .streamlit/
│   └── config.toml                 ← Dark theme + port 7860 for HF Spaces
│
├── Dockerfile                      ← Production Docker image for HF Spaces
├── main.py                         ← Terminal test runner (no UI)
├── app.py                          ← HF Spaces entry point
├── requirements.txt
├── .env.example                    ← API key template
├── .gitignore                      ← Excludes .env, __pycache__, *.pdf
└── README.md
```

---

## 🤖 The Five Agents

| Agent | File | Activates when | What it produces |
|---|---|---|---|
| **Research** | `workers.py` | Always | 3-angle Tavily search + LLM synthesis → `research_deep.txt` |
| **Statistics** | `workers.py` | Topic has numbers/trends | Structured JSON (metrics + trends + comparisons) + CSV → `statistics.txt` |
| **Domain Expert** | `workers.py` | Specialised topic | Persona-primed analysis → `expert_analysis.txt` |
| **Fact Checker** | `workers.py` | Claims need verification | Per-claim Tavily verify → `fact_check.txt` |
| **References** | `workers.py` | Citations add value | APA-formatted JSON list → `references.txt` |

All agents share data through the **Virtual File System** — a `Dict[str, str]` inside LangGraph state. Zero disk I/O.

---

## 📊 The Six Chart Types

All generated from Statistics agent JSON with zero extra LLM calls:

| # | Chart | Driven by |
|---|---|---|
| 1 | **Horizontal Bar** | `metrics` array |
| 2 | **Multi-series Area / Trend** | `trends[].data_points` |
| 3 | **Donut / Pie** | `comparisons` array |
| 4 | **Gauge** | First 0–100 metric value |
| 5 | **Bubble Scatter** | All `metrics` (size = relative value) |
| 6 | **Year-on-Year Bar** | `trends[0].data_points` |

---

## 🔑 Getting API Keys (Free)

### Groq — Primary LLM ⭐ Required

Fast open-source inference (14,400 free requests/day):
1. [console.groq.com](https://console.groq.com) → Sign up → API Keys → Create
2. Copy: `gsk_...`

### Tavily — Web Search ✅ Required

Real-time web search for agents:
1. [app.tavily.com](https://app.tavily.com) → Sign up → Dashboard
2. Copy: `tvly-...`
3. Free: 1,000 searches/month

### Google Gemini — Fallback LLM (optional)

Only needed if no Groq key:
1. [aistudio.google.com](https://aistudio.google.com) → Get API Key
2. Copy: `AIzaSy...`

### LangSmith — Tracing (optional but recommended)

See every node execution, LLM call, and retry as a visual timeline:
1. [smith.langchain.com](https://smith.langchain.com) → Settings → API Keys → Create
2. Copy: `lsv2_...`

---

## ⚙️ Installation & Setup

**Prerequisites:** Python 3.11+, Git

```bash
# 1. Clone
git clone https://github.com/vishal815/ResearchPilot-AI.git
cd ResearchPilot-AI

# 2. Virtual environment
python -m venv .venv

# 3. Activate
# Windows:
.venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Set up API keys
cp .env.example .env
# Now open .env and fill in your keys
```

Your `.env` file:
```env
GROQ_API_KEY=gsk_your_key_here
TAVILY_API_KEY=tvly_your_key_here
# GOOGLE_API_KEY=AIzaSy_your_key_here    (optional fallback)
# LANGCHAIN_API_KEY=lsv2_your_key_here   (optional tracing)
# LANGCHAIN_TRACING_V2=true
# LANGCHAIN_PROJECT=researchpilot-ai
```

---

## ▶️ Running the Project

### Terminal mode (test the pipeline first)

```bash
python main.py
```

Output:
```
============================================================
  ResearchPilot AI
  Query: Impact of AI on healthcare market growth...
============================================================
[NODE: PLANNER]    Domain detected: healthcare | 3 tasks created
[NODE: ROUTER]     Activated: ['research', 'statistics', 'domain_expert', 'fact_checker', 'citation']
[NODE: WORKERS]    Research done | Statistics: 8 metrics, 3 trends | Expert done | FactCheck done | Refs: 8 sources
[NODE: VISUALIZATION]  6 charts generated
[NODE: WRITER]     Report generated
[NODE: QUALITY_GATE]   Score: 7.5/10
[NODE: COVER]      SVG cover card generated
============================================================
  Total time: 52.3s | Saved to output_report_v2.md
```

### Streamlit Web UI

```bash
streamlit run ui/app.py
```

Opens at `http://localhost:8501`

---

## 🐳 Deploy to Hugging Face Spaces

The project ships with a ready `Dockerfile` that targets port 7860 (Hugging Face's required port).

### Step 1 — Push to GitHub

```bash
git add .
git commit -m "Initial ResearchPilot AI upload"
git push origin main
```

### Step 2 — Create a Hugging Face Space

1. Go to [huggingface.co/spaces](https://huggingface.co/spaces)
2. Click **Create new Space**
3. Set:
   - **Space name:** `ResearchPilot-AI`
   - **License:** MIT
   - **SDK:** **Docker** ← important, not Streamlit
   - **Visibility:** Public

### Step 3 — Add API Keys as Secrets

> ⚠️ Never put real API keys in code or `Dockerfile`. Use HF Secrets — they're injected as environment variables at runtime, invisible in the repo.

Go to your Space → **Settings** → **Repository secrets** → **New secret**:

| Secret Name | Value | Required? |
|---|---|---|
| `GROQ_API_KEY` | Your Groq key (`gsk_...`) | ✅ Required |
| `TAVILY_API_KEY` | Your Tavily key (`tvly_...`) | ✅ Required |
| `LANGCHAIN_API_KEY` | Your LangSmith key (`lsv2_...`) | Optional |
| `LANGCHAIN_TRACING_V2` | `true` | Optional (with LangSmith) |
| `GOOGLE_API_KEY` | Your Gemini key | Optional fallback |

**Why secrets, not `.env`?** HF Spaces clones your repo publicly — your `.env` must never be committed (it's in `.gitignore`). Secrets are stored encrypted in HF's vault and injected at container start time.

Your `Dockerfile` already sets:
```dockerfile
ENV LANGCHAIN_PROJECT="researchpilot-ai"
```
This constant is safe to hardcode because it's not sensitive — it's just the project name in LangSmith's dashboard.

The `LANGCHAIN_TRACING_V2=true` env var activates LangSmith auto-tracing — set it as a secret alongside your `LANGCHAIN_API_KEY`. Once both are set, every run appears in your [LangSmith dashboard](https://smith.langchain.com) showing exactly which node ran, how long each LLM call took, and the full prompt/response for every agent call.

### Step 4 — Link GitHub Repo

In your Space → **Files** → **Connect to GitHub repo** → select your repo → HF auto-builds on every push.

Or push directly to the HF Space's git remote:
```bash
git remote add hf https://huggingface.co/spaces/YOUR_HF_USERNAME/ResearchPilot-AI
git push hf main
```

### Step 5 — Wait for Build

HF Spaces shows a build log. The first build takes ~3-5 minutes (downloads dependencies). After that, code-only pushes rebuild in ~60 seconds.

---

## 📚 Concepts Covered

| Concept | Where in code | One-line description |
|---|---|---|
| **Agentic AI** | All nodes | Agents decide and act, not just reply |
| **LangGraph StateGraph** | `graph_builder.py` | Stateful multi-node orchestration with cycles |
| **Conditional Edge / Routing** | `graph_builder.py` + `quality_gate.py` | `should_retry()` returns string → LangGraph picks next node |
| **Shared State (TypedDict)** | `state.py` | One dict flows through every node — how agents "talk" |
| **Tool Use** | `search_tool.py` | Agents calling Tavily external API |
| **Virtual File System** | `file_system.py` | Dict-as-filesystem for zero-I/O context sharing |
| **Persona Priming** | `workers.py` | Named, credentialed identity → sharper domain output |
| **Structured Output Forcing** | `workers.py` | Force LLM to return exact JSON schema for deterministic chart rendering |
| **LLM-as-Judge** | `quality_gate.py` | Separate LLM call evaluates the first LLM's output |
| **Self-Correction Loop** | `quality_gate.py` | Cycle in graph capped by `retry_count` |
| **RAG** | `workers.py` | Search first → synthesise over retrieved context |
| **Flowable PDF** | `pdf_generator.py` | ReportLab auto-layout vs. manual x/y coordinate mess |
| **Streamlit Session State** | `ui/app.py` | Cache results across reruns so downloads don't re-trigger agents |

---

## 🔧 Troubleshooting

| Error | Cause | Fix |
|---|---|---|
| `ModuleNotFoundError` | venv not activated | `.venv\Scripts\activate` then `pip install -r requirements.txt` |
| `ImportError: cannot import name 'web_search'` | Old `search_tool.py` | Confirm file has `def web_search(query, max_results=5):` |
| Charts missing / only 1 chart | rgba color bug (old version) | Make sure you have the latest `visualization.py` |
| Cover shows `Score: 0.0` | Old graph wiring (cover before quality_gate) | Make sure you have the latest `graph_builder.py` |
| PDF has two References sections | LLM writes its own + structured list | Make sure you have latest `pdf_generator.py` with `_strip_references_section()` |
| `kaleido` error in PDF | Wrong kaleido version | `pip install kaleido==0.2.1` (pin to 0.2.1 exactly) |
| Page "resets" on download | Old `app.py` without session_state cache | Make sure you have latest `ui/app.py` |
| `429` rate limit | Hit LLM free tier | Wait 60s and retry, or switch to Gemini fallback |

---

## 🛣️ Roadmap

- [ ] AI-generated cover image via Pollinations AI (free, no key needed)
- [ ] LangGraph checkpointing for session memory across multiple queries
- [ ] Upload a PDF/document as additional research context
- [ ] Model selector in UI (Groq / Gemini / OpenRouter)
- [ ] Auto-generate PowerPoint slide deck from the report
- [ ] LangSmith evaluation dashboard integration

---

## 📜 License

MIT License — free to use, modify, and distribute with attribution.

---

## 🙏 Acknowledgements

[LangGraph](https://langchain-ai.github.io/langgraph/) · [Groq](https://groq.com) · [Google Gemini](https://aistudio.google.com) · [Tavily](https://tavily.com) · [Plotly](https://plotly.com) · [Streamlit](https://streamlit.io) · [ReportLab](https://www.reportlab.com) · [LangSmith](https://smith.langchain.com)

---

## 👨‍💻 Connect With Me

<div align="center">

[🌐 Portfolio](https://vishal-lazrus-portfolio.vercel.app/) &nbsp;•&nbsp;
[💼 LinkedIn](https://www.linkedin.com/in/vishal-lazrus/) &nbsp;•&nbsp;
[🐙 GitHub](https://github.com/vishal815)

**If this helped you learn something, give it a ⭐ on GitHub!**

*Built by Vishal Lazrus during AI Internship at Infosys, June 2026*

</div>
