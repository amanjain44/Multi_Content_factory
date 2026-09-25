from ..schemas import AIState, ContentTypeOutput
from ..providers.factory import AIProviderFactory
from ..config import AIConfig
from ..prompts import GLOBAL_RELEVANCE_REQUIREMENT

def get_provider():
    from ...core.config import settings
    config = AIConfig(
        provider=settings.AI_PROVIDER,
        api_key=settings.OPENAI_API_KEY,
        model_name=settings.AI_MODEL_NAME,
        temperature=settings.AI_TEMPERATURE
    )
    return AIProviderFactory.get_provider(config)

async def recommend_type(state: AIState) -> AIState:
    provider = get_provider()
    
    prompt = f"""
    {GLOBAL_RELEVANCE_REQUIREMENT}
    Analyze the following source text and recommend the most suitable primary content type, along with alternatives.
    
    Source Text:
    {state['input_text']}
    
    CRITICAL INSTRUCTION: You MUST recommend exactly ONE primary type and a few alternatives. 
    You MUST choose ONLY from the following exact six options:
    - Video
    - Image
    - Carousel
    - Article
    - Newsletter
    - Social Post
    
    Do NOT use any other names or variations. Provide your recommendation with detailed reasoning and signals found in the source text.
    """
    
    try:
        result: ContentTypeOutput = await provider.generate_structured(prompt, ContentTypeOutput)
        return {
            **state,
            "structured_output": result.model_dump(),
            "error": None
        }
    except Exception as e:
        return {
            **state,
            "error": str(e),
            "retries": state.get("retries", 0) + 1
        }

async def validate_result(state: AIState) -> AIState:
    if state.get("error"):
        return state
        
    output = state.get("structured_output")
    if not output:
        return {**state, "error": "No output generated"}
        
    try:
        ContentTypeOutput(**output)
        return state
    except Exception as e:
        return {**state, "error": f"Validation failed: {str(e)}"}
