"""
ResearchPilot AI — Planner Node
Reads user query → creates structured TODO list + detects topic type.
"""
import time
import json
from graph.state import ResearchState
from graph.llm_factory import get_llm


def planner_node(state: ResearchState) -> dict:
    t0 = time.time()
    query = state["query"]
    logs = list(state.get("agent_logs", []))
    logs.append("[Planner] Analysing query and creating research plan...")

    llm = get_llm(temperature=0.3)

    prompt = f"""You are a research planner. Given a query, produce a structured research plan.

Query: {query}

Return ONLY valid JSON (no markdown, no backticks):
{{
  "topic_domain": "<one of: healthcare, finance, technology, science, history, environment, politics, general>",
  "research_plan": "<2-3 sentence overview of the research approach>",
  "todos": [
    {{"agent": "search_agent",    "task": "<specific search task 1>"}},
    {{"agent": "analysis_agent",  "task": "<what to analyse>"}},
    {{"agent": "examples_agent",  "task": "<what examples/case studies to find>"}}
  ]
}}"""

    response = llm.invoke(prompt)
    raw = response.content.strip()

    # Strip markdown fences if present
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    try:
        data = json.loads(raw)
    except Exception:
        # Fallback defaults
        data = {
            "topic_domain": "general",
            "research_plan": f"Research {query} comprehensively.",
            "todos": [
                {"agent": "search_agent",   "task": f"Search for information about {query}"},
                {"agent": "analysis_agent", "task": f"Analyse key findings about {query}"},
                {"agent": "examples_agent", "task": f"Find real-world examples related to {query}"},
            ]
        }

    todos = data.get("todos", [])
    domain = data.get("topic_domain", "general")
    plan = data.get("research_plan", "")

    logs.append(f"[Planner] Domain detected: {domain}")
    logs.append(f"[Planner] Created {len(todos)} tasks")

    timings = dict(state.get("agent_timings", {}))
    timings["planner"] = round(time.time() - t0, 2)

    return {
        "todos": todos,
        "topic_domain": domain,
        "research_plan": plan,
        "agent_logs": logs,
        "agent_timings": timings,
        "virtual_files": state.get("virtual_files", {}),
        "structured_data": {},
        "citations": [],
        "chart_json": [],
        "thumbnail_svg": None,
        "final_report": "",
        "quality_score": 0.0,
        "retry_count": state.get("retry_count", 0),
        "active_agents": [],
        "generate_thumbnail": state.get("generate_thumbnail", False),
    }
