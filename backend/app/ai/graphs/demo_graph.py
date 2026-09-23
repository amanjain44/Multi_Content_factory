from langgraph.graph import StateGraph, START, END
from ..schemas import AIState
from ..nodes.demo_nodes import analyze_input, generate_result, validate_result

def should_retry(state: AIState) -> str:
    """Conditional edge logic."""
    if state.get("error"):
        if state.get("retries", 0) < 3:
            return "generate_result"
        return END
    return "validate_result"

def should_end(state: AIState) -> str:
    return END

def build_demo_graph():
    builder = StateGraph(AIState)
    
    # Add nodes
    builder.add_node("analyze_input", analyze_input)
    builder.add_node("generate_result", generate_result)
    builder.add_node("validate_result", validate_result)
    
    # Add edges
    builder.add_edge(START, "analyze_input")
    builder.add_edge("analyze_input", "generate_result")
    
    # Conditional edge for retries
    builder.add_conditional_edges(
        "generate_result",
        should_retry,
        {
            "generate_result": "generate_result",
            "validate_result": "validate_result",
            END: END
        }
    )
    
    builder.add_edge("validate_result", END)
    
    return builder.compile()
