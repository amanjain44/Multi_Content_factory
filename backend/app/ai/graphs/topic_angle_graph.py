from langgraph.graph import StateGraph, START, END
from ..schemas import AIState
from ..nodes.topic_angle_nodes import analyze_context, generate_angles, validate_result

def should_retry(state: AIState) -> str:
    """Conditional edge logic."""
    if state.get("error"):
        if state.get("retries", 0) < 3:
            return "generate_angles"
        return END
    return "validate_result"

def build_topic_angle_graph():
    builder = StateGraph(AIState)
    
    # Add nodes
    builder.add_node("analyze_context", analyze_context)
    builder.add_node("generate_angles", generate_angles)
    builder.add_node("validate_result", validate_result)
    
    # Add edges
    builder.add_edge(START, "analyze_context")
    builder.add_edge("analyze_context", "generate_angles")
    
    # Conditional edge for retries
    builder.add_conditional_edges(
        "generate_angles",
        should_retry,
        {
            "generate_angles": "generate_angles",
            "validate_result": "validate_result",
            END: END
        }
    )
    
    builder.add_edge("validate_result", END)
    
    return builder.compile()
