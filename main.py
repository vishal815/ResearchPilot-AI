"""
ResearchPilot AI — Terminal Test Runner
Run: python main.py
Tests the full pipeline without Streamlit.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from graph.graph_builder import graph

TEST_QUERY = "Impact of artificial intelligence on healthcare in 2025"

def main():
    print("=" * 60)
    print("  ResearchPilot AI")
    print(f"  Query: {TEST_QUERY}")
    print("=" * 60)

    initial_state = {
        "query":            TEST_QUERY,
        "todos":            [],
        "research_plan":    "",
        "active_agents":    [],
        "topic_domain":     "general",
        "virtual_files":    {},
        "structured_data":  {},
        "citations":        [],
        "chart_json":       [],
        "thumbnail_svg":    None,
        "final_report":     "",
        "quality_score":    0.0,
        "retry_count":      0,
        "agent_logs":       [],
        "agent_timings":    {},
        "generate_thumbnail": True,
    }

    final_state = {}
    for update in graph.stream(initial_state):
        node_name = list(update.keys())[0]
        node_data  = update[node_name]
        print(f"\n[NODE: {node_name.upper()}]")

        logs = node_data.get("agent_logs", [])
        for log in logs[-3:]:   # show last 3 logs per node
            print(f"  {log}")

        for k, v in node_data.items():
            if v is not None:
                final_state[k] = v

    print("\n" + "=" * 60)
    print(f"  Quality Score : {final_state.get('quality_score', 0):.1f}/10")
    print(f"  Active Agents : {final_state.get('active_agents', [])}")
    print(f"  Domain        : {final_state.get('topic_domain', 'general')}")
    print(f"  Charts        : {len(final_state.get('chart_json', []))}")
    print(f"  Citations     : {len(final_state.get('citations', []))}")
    print("=" * 60)

    report = final_state.get("final_report", "")
    if report:
        with open("output_report_v2.md", "w", encoding="utf-8") as f:
            f.write(report)
        print("\n✅ Report saved to output_report_v2.md")

    timings = final_state.get("agent_timings", {})
    if timings:
        print("\n⏱  Timings:")
        for k, v in timings.items():
            print(f"   {k:20s} {v:.2f}s")
        print(f"   {'TOTAL':20s} {sum(timings.values()):.2f}s")

if __name__ == "__main__":
    main()
