from typing import Any, Dict
from ..schemas import AIState, ContentStrategyOutput
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
    """Analyze the overall context including original source, opportunity, platforms, and topic angle."""
    input_text = state.get("input_text", "")
    selected_opportunity = state.get("selected_opportunity", {})
    selected_platforms = state.get("selected_platforms", [])
    selected_angle = state.get("selected_angle", {})
    
    if not input_text or not selected_opportunity or not selected_platforms or not selected_angle:
        return {"error": "Missing required context for content strategy"}

    provider = get_provider()
    
    platforms_str = ", ".join([p.get("platform", "Unknown") for p in selected_platforms])
    
    prompt = f"""
    Analyze the workflow context to prepare for Content Strategy generation.
    
    Source Material:
    {input_text}
    
    Selected Content Opportunity:
    Title: {selected_opportunity.get('title')}
    Target Audience: {selected_opportunity.get('potentialAudience')}
    
    Selected Platforms:
    {platforms_str}
    
    Selected Topic Angle:
    Title: {selected_angle.get('title')}
    Angle: {selected_angle.get('angle')}
    Hook: {selected_angle.get('hook')}
    Core Promise: {selected_angle.get('corePromise')}
    
    Identify the overarching objective and narrative structure that ties these elements together.
    """
    
    try:
        analysis = await provider.generate_text(prompt)
        return {"intent": analysis}
    except Exception as e:
        return {"error": f"Failed to analyze context: {str(e)}"}

async def generate_strategy(state: AIState) -> Dict[str, Any]:
    """Generate the full content strategy based on the analyzed context."""
    input_text = state.get("input_text", "")
    selected_opportunity = state.get("selected_opportunity", {})
    selected_platforms = state.get("selected_platforms", [])
    selected_angle = state.get("selected_angle", {})
    analysis = state.get("intent", "")
    
    if state.get("error") and state.get("retries", 0) >= 3:
        return {} # Max retries reached
        
    provider = get_provider()
    
    platforms_info = "\n".join([f"- {p.get('platform')}: {p.get('recommendedFormat')}" for p in selected_platforms])
    
    grounding_context = state.get("grounding_context", {})
    grounding_text = grounding_context.get("text", "")
    approved_type = state.get("approved_content_type")
    type_str = f"""
CRITICAL INSTRUCTION:
The user has explicitly approved the Content Type: {approved_type}.
You MUST generate a content strategy that is 100% {approved_type}-oriented.
The strategy MUST be compatible with {approved_type}. Do NOT recommend any other content type.
""" if approved_type else ""
    context_str = f"Extra Grounding Context (use if relevant):\n{grounding_text}\n\n" if grounding_text else ""

    prompt = f"""
    Based on the following context and analysis, generate a comprehensive content strategy.
    
    Source Material:
    {input_text}
    
    {context_str}
    {type_str}
    Selected Content Opportunity:
    Title: {selected_opportunity.get('title')}
    
    Selected Platforms:
    {platforms_info}
    
    Selected Topic Angle:
    Title: {selected_angle.get('title')}
    Angle: {selected_angle.get('angle')}
    Hook: {selected_angle.get('hook')}
    Core Promise: {selected_angle.get('corePromise')}
    Supporting Points: {", ".join(selected_angle.get('supportingPoints', []))}
    
    Analysis Context:
    {analysis}
    
    Provide a full content strategy that acts as a blueprint for the content creator.
    Ensure you include specific platform adaptations for the selected platforms.
    """
    
    try:
        result = await provider.generate_structured(prompt, ContentStrategyOutput)
        return {
            "structured_output": result.model_dump(),
            "error": None
        }
    except Exception as e:
        retries = state.get("retries", 0)
        return {
            "error": f"Failed to generate content strategy: {str(e)}",
            "retries": retries + 1
        }

async def validate_result(state: AIState) -> Dict[str, Any]:
    """Validate the final output."""
    if state.get("error"):
        return state
        
    output = state.get("structured_output")
    if not output or "strategy" not in output:
        return {"error": "Missing strategy in generated output"}
        
    return state
