from langgraph.graph import StateGraph, START, END
from ..schemas import AIState
from ..nodes.content_selection_nodes import analyze_source, generate_recommendations, validate_result

def should_retry(state: AIState) -> str:
    """Conditional edge logic."""
    if state.get("error"):
        if state.get("retries", 0) < 3:
            return "generate_recommendations"
        return END
    return "validate_result"

def build_content_selection_graph():
    builder = StateGraph(AIState)
    
    # Add nodes
    builder.add_node("analyze_source", analyze_source)
    builder.add_node("generate_recommendations", generate_recommendations)
    builder.add_node("validate_result", validate_result)
    
    # Add edges
    builder.add_edge(START, "analyze_source")
    builder.add_edge("analyze_source", "generate_recommendations")
    
    # Conditional edge for retries
    builder.add_conditional_edges(
        "generate_recommendations",
        should_retry,
        {
            "generate_recommendations": "generate_recommendations",
            "validate_result": "validate_result",
            END: END
        }
    )
    
    builder.add_edge("validate_result", END)
    
    return builder.compile()
