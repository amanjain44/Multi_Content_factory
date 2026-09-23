from typing import Any, Dict
from ..schemas import AIState, ContentSelectionOutput
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

async def analyze_source(state: AIState) -> Dict[str, Any]:
    """Analyze the input text to extract key themes and potential audiences."""
    input_text = state.get("input_text", "")
    
    if not input_text:
        return {"error": "Input text is empty"}

    # Use AI to analyze the source material briefly
    provider = get_provider()
    
    prompt = f"""
    Analyze the following source material or idea. Identify the main themes, 
    the potential target audiences, and the core value proposition.
    
    Source Material:
    {input_text}
    """
    
    try:
        # We can just use generate_text for the intermediate step to populate context if needed
        analysis = await provider.generate_text(prompt)
        return {"intent": analysis}
    except Exception as e:
        return {"error": f"Failed to analyze source: {str(e)}"}

async def generate_recommendations(state: AIState) -> Dict[str, Any]:
    """Generate content opportunities based on the input text and analysis."""
    input_text = state.get("input_text", "")
    analysis = state.get("intent", "")
    
    if state.get("error") and state.get("retries", 0) >= 3:
        return {} # Max retries reached
        
    provider = get_provider()
    
    grounding_context = state.get("grounding_context", {})
    grounding_text = grounding_context.get("text", "")
    
    context_str = f"Extra Grounding Context (use if relevant):\n{grounding_text}\n\n" if grounding_text else ""
    
    prompt = f"""
    Based on the following source material and its analysis, recommend 3-5 distinct content formats or angles (Content Opportunities) that would be highly valuable for the target audience.
    
    Source Material:
    {input_text}
    
    {context_str}
    Analysis Context:
    {analysis}
    
    For each opportunity, provide:
    - A unique ID (e.g. alphanumeric string like 'opt-1')
    - A catchy title
    - A brief summary
    - Why it is interesting/valuable
    - A list of 3-5 key points it will cover
    - The specific potential audience
    - The estimated value or impact
    """
    
    try:
        result = await provider.generate_structured(prompt, ContentSelectionOutput)
        return {
            "structured_output": result.model_dump(),
            "error": None
        }
    except Exception as e:
        retries = state.get("retries", 0)
        return {
            "error": f"Failed to generate recommendations: {str(e)}",
            "retries": retries + 1
        }

async def validate_result(state: AIState) -> Dict[str, Any]:
    """Validate the final output."""
    if state.get("error"):
        return state
        
    output = state.get("structured_output")
    if not output or "opportunities" not in output:
        return {"error": "Missing opportunities in generated output"}
        
    if not isinstance(output["opportunities"], list) or len(output["opportunities"]) == 0:
        return {"error": "Generated opportunities list is empty or invalid"}
        
    return state
