from typing import Any, Dict
from ..schemas import AIState, StoryboardOutput
from ..providers.factory import AIProviderFactory
from ..config import AIConfig

def get_provider():
    from ...core.config import settings
    config = AIConfig(
        provider=settings.AI_PROVIDER,
        api_key=settings.OPENAI_API_KEY,
        model_name=settings.AI_MODEL_NAME,
        temperature=settings.AI_TEMPERATURE
    )
    return AIProviderFactory.get_provider(config)

async def analyze_context(state: AIState) -> Dict[str, Any]:
    """Analyze the overall context including original source, opportunity, platforms, angle, and strategy."""
    input_text = state.get("input_text", "")
    selected_opportunity = state.get("selected_opportunity", {})
    selected_platforms = state.get("selected_platforms", [])
    selected_angle = state.get("selected_angle", {})
    approved_strategy = state.get("approved_strategy", {})
    
    if not input_text or not selected_opportunity or not selected_platforms or not selected_angle or not approved_strategy:
        return {"error": "Missing required context for storyboard"}

    provider = get_provider()
    
    prompt = f"""
    Analyze the workflow context to prepare for Storyboard generation.
    
    Approved Content Strategy:
    Objective: {approved_strategy.get('objective')}
    Format: {approved_strategy.get('format')}
    Structure: {approved_strategy.get('contentStructure')}
    Tone: {approved_strategy.get('tone')}
    
    Selected Topic Angle:
    Title: {selected_angle.get('title')}
    Core Promise: {selected_angle.get('corePromise')}
    
    Identify the key narrative beats required to translate this strategy into a sequential storyboard.
    """
    
    try:
        analysis = await provider.generate_text(prompt)
        return {"intent": analysis}
    except Exception as e:
        return {"error": f"Failed to analyze context: {str(e)}"}

async def generate_storyboard(state: AIState) -> Dict[str, Any]:
    """Generate the full storyboard based on the analyzed context."""
    input_text = state.get("input_text", "")
    selected_opportunity = state.get("selected_opportunity", {})
    selected_platforms = state.get("selected_platforms", [])
    selected_angle = state.get("selected_angle", {})
    approved_strategy = state.get("approved_strategy", {})
    analysis = state.get("intent", "")
    
    if state.get("error") and state.get("retries", 0) >= 3:
        return {} # Max retries reached
        
    provider = get_provider()
    
    platforms_info = "\n".join([f"- {p.get('platform')}: {p.get('format')}" for p in approved_strategy.get('platformAdaptations', [])])
    if not platforms_info:
        platforms_info = "\n".join([f"- {p.get('platform')}" for p in selected_platforms])
    
    grounding_context = state.get("grounding_context", {})
    grounding_text = grounding_context.get("text", "")
    context_str = f"Extra Grounding Context (use if relevant):\n{grounding_text}\n\n" if grounding_text else ""
    
    approved_type = state.get("approved_content_type")
    type_str = f"""
CRITICAL INSTRUCTION:
The user has explicitly approved the Content Type: {approved_type}.
You MUST generate a storyboard/outline that is 100% {approved_type}-oriented.
For Video, generate scenes. For Carousel, generate slides. For Article/Newsletter/Social Post, generate structural sections.
Do NOT recommend any other content type.
""" if approved_type else ""

    prompt = f"""
    Based on the following context and analysis, generate a comprehensive scene-by-scene storyboard.
    
    {context_str}
    {type_str}
    Approved Content Strategy:
    Objective: {approved_strategy.get('objective')}
    Target Audience: {approved_strategy.get('targetAudience')}
    Core Message: {approved_strategy.get('coreMessage')}
    Structure: {approved_strategy.get('contentStructure')}
    Talking Points: {", ".join(approved_strategy.get('keyTalkingPoints', []))}
    
    Platforms:
    {platforms_info}
    
    Analysis Context:
    {analysis}
    
    Generate a storyboard with a sequence of scenes that brings the structure to life.
    Each scene must have a purpose, narration, visual direction, on-screen text, transition, and estimated duration.
    Ensure the storyboard is logically derived from the strategy and forms a coherent narrative.
    """
    
    try:
        result = await provider.generate_structured(prompt, StoryboardOutput)
        return {
            "structured_output": result.model_dump(),
            "error": None
        }
    except Exception as e:
        retries = state.get("retries", 0)
        return {
            "error": f"Failed to generate storyboard: {str(e)}",
            "retries": retries + 1
        }

async def validate_result(state: AIState) -> Dict[str, Any]:
    """Validate the final output."""
    if state.get("error"):
        return state
        
    output = state.get("structured_output")
    if not output or "storyboard" not in output:
        return {"error": "Missing storyboard in generated output"}
        
    return state
