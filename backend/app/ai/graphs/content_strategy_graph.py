from langgraph.graph import StateGraph, START, END
from ..schemas import AIState
from ..nodes.content_strategy_nodes import analyze_context, generate_strategy, validate_result

def should_retry(state: AIState) -> str:
    """Conditional edge logic."""
    if state.get("error"):
        if state.get("retries", 0) < 3:
            return "generate_strategy"
        return END
    return "validate_result"

def build_content_strategy_graph():
    builder = StateGraph(AIState)
    
    # Add nodes
    builder.add_node("analyze_context", analyze_context)
    builder.add_node("generate_strategy", generate_strategy)
    builder.add_node("validate_result", validate_result)
    
    # Add edges
    builder.add_edge(START, "analyze_context")
    builder.add_edge("analyze_context", "generate_strategy")
    
    # Conditional edge for retries
    builder.add_conditional_edges(
        "generate_strategy",
        should_retry,
        {
            "generate_strategy": "generate_strategy",
            "validate_result": "validate_result",
            END: END
        }
    )
    
    builder.add_edge("validate_result", END)
    
    return builder.compile()
