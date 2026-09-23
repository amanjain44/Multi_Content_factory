from langgraph.graph import StateGraph, START, END
from ..schemas import AIState
from ..nodes.script_nodes import analyze_storyboard_context, generate_script, validate_script_result


def should_retry(state: AIState) -> str:
    """Conditional edge: retry on error up to 3 times, then END or validate."""
    if state.get("error"):
        if state.get("retries", 0) < 3:
            return "generate_script"
        return END
    return "validate_script_result"


def build_script_graph():
    builder = StateGraph(AIState)

    # Add nodes
    builder.add_node("analyze_storyboard_context", analyze_storyboard_context)
    builder.add_node("generate_script", generate_script)
    builder.add_node("validate_script_result", validate_script_result)

    # Add edges
    builder.add_edge(START, "analyze_storyboard_context")
    builder.add_edge("analyze_storyboard_context", "generate_script")

    # Conditional edge for retries
    builder.add_conditional_edges(
        "generate_script",
        should_retry,
        {
            "generate_script": "generate_script",
            "validate_script_result": "validate_script_result",
            END: END
        }
    )

    builder.add_edge("validate_script_result", END)

    return builder.compile()
