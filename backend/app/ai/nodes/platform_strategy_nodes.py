from typing import Any, Dict
from ..schemas import AIState, PlatformStrategyOutput
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

async def analyze_content(state: AIState) -> Dict[str, Any]:
    """Analyze the original source and the selected opportunity."""
    input_text = state.get("input_text", "")
    selected_opportunity = state.get("selected_opportunity", {})
    
    if not input_text or not selected_opportunity:
        return {"error": "Missing input text or selected opportunity"}

    provider = get_provider()
    
    prompt = f"""
    Analyze the following source material and the specific content opportunity the user selected.
    Extract the core themes and the target audience to prepare for platform strategy recommendations.
    
    Source Material:
    {input_text}
    
    Selected Opportunity:
    Title: {selected_opportunity.get('title')}
    Summary: {selected_opportunity.get('summary')}
    Target Audience: {selected_opportunity.get('potentialAudience')}
    Key Points: {selected_opportunity.get('keyPoints')}
    """
    
    try:
        analysis = await provider.generate_text(prompt)
        return {"intent": analysis}
    except Exception as e:
        return {"error": f"Failed to analyze content: {str(e)}"}

async def generate_platforms(state: AIState) -> Dict[str, Any]:
    """Generate platform recommendations based on the analysis."""
    input_text = state.get("input_text", "")
    selected_opportunity = state.get("selected_opportunity", {})
    analysis = state.get("intent", "")
    
    if state.get("error") and state.get("retries", 0) >= 3:
        return {} # Max retries reached
        
    provider = get_provider()
    
    grounding_context = state.get("grounding_context", {})
    grounding_text = grounding_context.get("text", "")
    context_str = f"Extra Grounding Context (use if relevant):\n{grounding_text}\n\n" if grounding_text else ""
    
    approved_type = state.get("approved_content_type")
    type_str = f"""
CRITICAL INSTRUCTION:
The user has explicitly approved the Content Type: {approved_type}.
You MUST generate platform recommendations that are 100% {approved_type}-oriented.
The format MUST be compatible with {approved_type}. Do NOT recommend any other content type.
""" if approved_type else ""
    
    prompt = f"""
    Based on the following source material, the selected content opportunity, and the analysis, recommend 2-4 platforms that would be highly suitable for publishing this content.
    
    Source Material:
    {input_text}
    
    Selected Opportunity:
    Title: {selected_opportunity.get('title')}
    Summary: {selected_opportunity.get('summary')}
    
    {context_str}
    Analysis Context:
    {analysis}
    
    {type_str}
    
    For each platform recommendation, provide:
    - A unique ID (alphanumeric string like 'plat-1')
    - A projectId (you can just use 'proj-1' or any string, it will be overridden by the backend)
    - The platform name (e.g., LinkedIn, YouTube, Twitter)
    - A suitability score from 0 to 100
    - Reasoning for why it's a good fit
    - The recommended format (e.g. Long-form video, Carousel)
    - The recommended length
    - The target audience on this specific platform
    - The tone
    - The priority ('Recommended' or 'Optional')
    """
    
    try:
        result = await provider.generate_structured(prompt, PlatformStrategyOutput)
        return {
            "structured_output": result.model_dump(),
            "error": None
        }
    except Exception as e:
        retries = state.get("retries", 0)
        return {
            "error": f"Failed to generate platform recommendations: {str(e)}",
            "retries": retries + 1
        }

async def validate_result(state: AIState) -> Dict[str, Any]:
    """Validate the final output."""
    if state.get("error"):
        return state
        
    output = state.get("structured_output")
    if not output or "recommendations" not in output:
        return {"error": "Missing recommendations in generated output"}
        
    if not isinstance(output["recommendations"], list) or len(output["recommendations"]) == 0:
        return {"error": "Generated recommendations list is empty or invalid"}
        
    return state
