from langgraph.graph import StateGraph, START, END
from ..schemas import AIState
from ..nodes.platform_strategy_nodes import analyze_content, generate_platforms, validate_result

def should_retry(state: AIState) -> str:
    """Conditional edge logic."""
    if state.get("error"):
        if state.get("retries", 0) < 3:
            return "generate_platforms"
        return END
    return "validate_result"

def build_platform_strategy_graph():
    builder = StateGraph(AIState)
    
    # Add nodes
    builder.add_node("analyze_content", analyze_content)
    builder.add_node("generate_platforms", generate_platforms)
    builder.add_node("validate_result", validate_result)
    
    # Add edges
    builder.add_edge(START, "analyze_content")
    builder.add_edge("analyze_content", "generate_platforms")
    
    # Conditional edge for retries
    builder.add_conditional_edges(
        "generate_platforms",
        should_retry,
        {
            "generate_platforms": "generate_platforms",
            "validate_result": "validate_result",
            END: END
        }
    )
    
    builder.add_edge("validate_result", END)
    
    return builder.compile()
