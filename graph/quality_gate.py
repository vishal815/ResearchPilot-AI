"""
ResearchForge v2 — Quality Gate Node
Scores the report 0–10. Routes back to synthesizer if below threshold.
"""
import time
import re
from graph.state import ResearchState
from graph.llm_factory import get_llm

QUALITY_THRESHOLD = 7.0
MAX_RETRIES = 2


def quality_gate_node(state: ResearchState) -> dict:
    t0 = time.time()
    report = state.get("final_report", "")
    retry = state.get("retry_count", 0)
    logs = list(state.get("agent_logs", []))
    timings = dict(state.get("agent_timings", {}))

    logs.append("[Quality Gate] Evaluating report quality...")

    llm = get_llm(temperature=0.1)

    prompt = f"""You are a strict research quality evaluator. Score this report from 0 to 10.

Report:
{report[:4000]}

Scoring criteria:
- Depth and comprehensiveness (0-2 points)
- Evidence and factual support (0-2 points)  
- Structure and clarity (0-2 points)
- Analytical insight beyond surface facts (0-2 points)
- Practical value and actionable conclusions (0-2 points)

Respond with ONLY this format (no other text):
SCORE: X.X
REASON: one sentence explaining the score"""

    response = llm.invoke(prompt)
    text = response.content.strip()

    # Parse score
    score = 0.0
    match = re.search(r"SCORE:\s*(\d+\.?\d*)", text)
    if match:
        score = min(10.0, float(match.group(1)))

    reason_match = re.search(r"REASON:\s*(.+)", text)
    reason = reason_match.group(1) if reason_match else "No reason provided."

    logs.append(f"[Quality Gate] Score: {score}/10 — {reason}")

    timings["quality_gate"] = round(time.time() - t0, 2)

    return {
        "quality_score": score,
        "retry_count": retry + 1,
        "agent_logs": logs,
        "agent_timings": timings,
    }


def should_retry(state: ResearchState) -> str:
    """Conditional edge function: 'retry' → synthesizer, 'done' → end."""
    score = state.get("quality_score", 0)
    retry = state.get("retry_count", 0)

    if score < QUALITY_THRESHOLD and retry <= MAX_RETRIES:
        return "retry"
    return "done"
