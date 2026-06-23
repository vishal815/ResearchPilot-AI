"""
ResearchPilot AI — Graph Builder
Flow: planner → router → workers → visualization → writer → quality_gate
      → [retry: writer | done: cover → END]
Cover runs LAST so the quality score is available for the thumbnail.
"""
from langgraph.graph import StateGraph, END
from graph.state import ResearchState
from graph.planner      import planner_node
from graph.router       import router_node
from graph.workers      import workers_node
from graph.visualization import visualization_node
from graph.thumbnail    import thumbnail_node
from graph.synthesizer  import synthesizer_node
from graph.quality_gate import quality_gate_node, should_retry


def build_graph():
    b = StateGraph(ResearchState)
    b.add_node("planner",       planner_node)
    b.add_node("router",        router_node)
    b.add_node("workers",       workers_node)
    b.add_node("visualization", visualization_node)
    b.add_node("cover",         thumbnail_node)    # renamed from thumbnail
    b.add_node("writer",        synthesizer_node)  # renamed from synthesizer
    b.add_node("quality_gate",  quality_gate_node)

    b.set_entry_point("planner")
    b.add_edge("planner",       "router")
    b.add_edge("router",        "workers")
    b.add_edge("workers",       "visualization")
    b.add_edge("visualization", "writer")
    b.add_conditional_edges(
        "quality_gate", should_retry,
        {"retry": "writer", "done": "cover"}
    )
    b.add_edge("writer", "quality_gate")
    b.add_edge("cover", END)
    return b.compile()


graph = build_graph()
