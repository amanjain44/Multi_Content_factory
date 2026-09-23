from langgraph.graph import StateGraph, START, END
from ..schemas import AIState
from ..nodes.content_type_nodes import recommend_type, validate_result

def should_retry(state: AIState) -> str:
    """Conditional edge logic."""
    if state.get("error"):
        if state.get("retries", 0) < 3:
            return "recommend_type"
        return END
    return "validate_result"

def build_content_type_graph():
    builder = StateGraph(AIState)
    
    # Add nodes
    builder.add_node("recommend_type", recommend_type)
    builder.add_node("validate_result", validate_result)
    
    # Add edges
    builder.add_edge(START, "recommend_type")
    
    # Conditional edge for retries
    builder.add_conditional_edges(
        "recommend_type",
        should_retry,
        {
            "recommend_type": "recommend_type",
            "validate_result": "validate_result",
            END: END
        }
    )
    
    builder.add_edge("validate_result", END)
    
    return builder.compile()
