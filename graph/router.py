"""
ResearchPilot AI — Router Node
The key new node. Reads query + domain → decides which specialist agents to activate.
Returns active_agents list used by conditional edges.
"""
import time
import json
from graph.state import ResearchState
from graph.llm_factory import get_llm

# All available specialist agents
ALL_AGENTS = ["research", "statistics", "domain_expert", "fact_checker", "citation"]

# Domain → typical agent set (used as hint to LLM)
DOMAIN_HINTS = {
    "healthcare":    ["research", "statistics", "domain_expert", "fact_checker", "citation"],
    "finance":       ["research", "statistics", "fact_checker", "citation"],
    "technology":    ["research", "statistics", "domain_expert", "citation"],
    "science":       ["research", "statistics", "domain_expert", "fact_checker", "citation"],
    "history":       ["research", "domain_expert", "citation"],
    "environment":   ["research", "statistics", "domain_expert", "citation"],
    "politics":      ["research", "fact_checker", "citation"],
    "general":       ["research", "citation"],
}


def router_node(state: ResearchState) -> dict:
    t0 = time.time()
    query = state["query"]
    domain = state.get("topic_domain", "general")
    plan = state.get("research_plan", "")
    logs = list(state.get("agent_logs", []))
    logs.append("[Router] Deciding which specialist agents to activate...")

    llm = get_llm(temperature=0.1)

    hint = DOMAIN_HINTS.get(domain, ALL_AGENTS)

    prompt = f"""You are a research routing agent. Based on the query and domain, decide which specialist agents are needed.

Query: {query}
Domain: {domain}
Research plan: {plan}

Available agents and when to use them:
- research       → ALWAYS include (core web search)
- statistics     → include if the topic involves numbers, trends, market size, percentages, growth rates
- domain_expert  → include if topic needs specialised knowledge (medical, legal, financial, technical)
- fact_checker   → include if topic involves claims that should be verified (news, health claims, technical specs)
- citation       → include if academic/professional citations add value (research papers, reports)

Hint based on domain: {hint}

Return ONLY a JSON array of agent names. Example: ["research", "statistics", "domain_expert"]
No explanation, no markdown, just the JSON array."""

    response = llm.invoke(prompt)
    raw = response.content.strip()

    # Strip fences
    if "```" in raw:
        raw = raw.split("```")[1].strip()
        if raw.startswith("json"):
            raw = raw[4:].strip()

    try:
        agents = json.loads(raw)
        # Sanitise — only known agents
        agents = [a for a in agents if a in ALL_AGENTS]
        if "research" not in agents:
            agents.insert(0, "research")  # always run
    except Exception:
        agents = hint  # fallback to domain hint

    logs.append(f"[Router] Activated agents: {agents}")

    timings = dict(state.get("agent_timings", {}))
    timings["router"] = round(time.time() - t0, 2)

    return {
        "active_agents": agents,
        "agent_logs": logs,
        "agent_timings": timings,
    }
