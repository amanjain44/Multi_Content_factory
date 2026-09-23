from typing import Any, Dict
from ..schemas import AIState, TopicAngleOutput
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
    """Analyze the overall context including original source, selected opportunity, and selected platforms."""
    input_text = state.get("input_text", "")
    selected_opportunity = state.get("selected_opportunity", {})
    selected_platforms = state.get("selected_platforms", [])
    
    if not input_text or not selected_opportunity or not selected_platforms:
        return {"error": "Missing required context (input text, selected opportunity, or selected platforms)"}

    provider = get_provider()
    
    platforms_str = ", ".join([p.get("platform", "Unknown") for p in selected_platforms])
    
    prompt = f"""
    Analyze the workflow context to prepare for Topic & Angle generation.
    
    Source Material:
    {input_text}
    
    Selected Content Opportunity:
    Title: {selected_opportunity.get('title')}
    Summary: {selected_opportunity.get('summary')}
    Target Audience: {selected_opportunity.get('potentialAudience')}
    
    Selected Platforms for Distribution:
    {platforms_str}
    
    Identify the core messages that will resonate with this audience on these platforms.
    """
    
    try:
        analysis = await provider.generate_text(prompt)
        return {"intent": analysis}
    except Exception as e:
        return {"error": f"Failed to analyze context: {str(e)}"}

async def generate_angles(state: AIState) -> Dict[str, Any]:
    """Generate topic angles based on the analyzed context."""
    input_text = state.get("input_text", "")
    selected_opportunity = state.get("selected_opportunity", {})
    selected_platforms = state.get("selected_platforms", [])
    analysis = state.get("intent", "")
    
    if state.get("error") and state.get("retries", 0) >= 3:
        return {} # Max retries reached
        
    provider = get_provider()
    
    platforms_info = "\n".join([f"- {p.get('platform')}: {p.get('recommendedFormat')} ({p.get('tone')} tone)" for p in selected_platforms])
    
    grounding_context = state.get("grounding_context", {})
    grounding_text = grounding_context.get("text", "")
    context_str = f"Extra Grounding Context (use if relevant):\n{grounding_text}\n\n" if grounding_text else ""
    
    approved_type = state.get("approved_content_type")
    type_str = f"Target Content Type: {approved_type}\nNOTE: The angles MUST be appropriate for a {approved_type}.\n" if approved_type else ""

    prompt = f"""
    Based on the following context, generate 3-4 distinct topic angles (e.g., Contrarian, Educational, Blueprint, Story-driven) for the content.
    
    Source Material:
    {input_text}
    
    {context_str}
    {type_str}
    Selected Content Opportunity:
    Title: {selected_opportunity.get('title')}
    Summary: {selected_opportunity.get('summary')}
    
    Selected Platforms:
    {platforms_info}
    
    Analysis Context:
    {analysis}
    
    For each angle, provide:
    - A unique ID (e.g., 'ang-1')
    - projectId (any string, will be overridden)
    - A working title
    - The specific angle (e.g. 'Contrarian / Architecture')
    - An opening hook
    - A brief description
    - The target audience
    - The core promise or takeaway
    - How it differentiates from generic content
    - A list of 3-5 supporting points
    - The platforms from the selected list that this angle is best suited for
    """
    
    try:
        result = await provider.generate_structured(prompt, TopicAngleOutput)
        return {
            "structured_output": result.model_dump(),
            "error": None
        }
    except Exception as e:
        retries = state.get("retries", 0)
        return {
            "error": f"Failed to generate topic angles: {str(e)}",
            "retries": retries + 1
        }

async def validate_result(state: AIState) -> Dict[str, Any]:
    """Validate the final output."""
    if state.get("error"):
        return state
        
    output = state.get("structured_output")
    if not output or "angles" not in output:
        return {"error": "Missing angles in generated output"}
        
    if not isinstance(output["angles"], list) or len(output["angles"]) == 0:
        return {"error": "Generated angles list is empty or invalid"}
        
    return state
