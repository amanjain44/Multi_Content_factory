from langgraph.graph import StateGraph, START, END
from ..schemas import AIState
from ..nodes.storyboard_nodes import analyze_context, generate_storyboard, validate_result

def should_retry(state: AIState) -> str:
    """Conditional edge logic."""
    if state.get("error"):
        if state.get("retries", 0) < 3:
            return "generate_storyboard"
        return END
    return "validate_result"

def build_storyboard_graph():
    builder = StateGraph(AIState)
    
    # Add nodes
    builder.add_node("analyze_context", analyze_context)
    builder.add_node("generate_storyboard", generate_storyboard)
    builder.add_node("validate_result", validate_result)
    
    # Add edges
    builder.add_edge(START, "analyze_context")
    builder.add_edge("analyze_context", "generate_storyboard")
    
    # Conditional edge for retries
    builder.add_conditional_edges(
        "generate_storyboard",
        should_retry,
        {
            "generate_storyboard": "generate_storyboard",
            "validate_result": "validate_result",
            END: END
        }
    )
    
    builder.add_edge("validate_result", END)
    
    return builder.compile()
