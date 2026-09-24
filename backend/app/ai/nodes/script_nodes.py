from typing import Any, Dict
from ..schemas import AIState, ScriptOutput
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


async def analyze_storyboard_context(state: AIState) -> Dict[str, Any]:
    """
    Analyze the approved storyboard and full workflow context to prepare
    for script generation. Identifies per-scene narrative expansion strategy.
    """
    input_text = state.get("input_text", "")
    selected_opportunity = state.get("selected_opportunity", {})
    selected_platforms = state.get("selected_platforms", [])
    selected_angle = state.get("selected_angle", {})
    approved_strategy = state.get("approved_strategy", {})
    approved_storyboard = state.get("approved_storyboard", {})

    if (
        not input_text
        or not selected_opportunity
        or not selected_platforms
        or not selected_angle
        or not approved_strategy
        or not approved_storyboard
    ):
        return {"error": "Missing required context for script generation"}

    scenes = approved_storyboard.get("scenes", [])
    if not scenes:
        return {"error": "Approved storyboard has no scenes — cannot generate script"}

    provider = get_provider()

    scene_titles = ", ".join(s.get("title", "") for s in scenes)
    platform_name = selected_platforms[0].get("platform", "Unknown") if selected_platforms else "Unknown"
    platform_format = selected_platforms[0].get("recommendedFormat", "") if selected_platforms else ""

    prompt = f"""
    Analyze the following approved storyboard and workflow context to prepare for Final Script generation.

    Source Topic: {input_text}

    Platform: {platform_name} ({platform_format})
    Tone: {approved_strategy.get('tone', '')}
    Hook Strategy: {approved_strategy.get('hookStrategy', '')}
    CTA: {approved_strategy.get('callToAction', '')}

    Approved Storyboard — {len(scenes)} scenes:
    {scene_titles}

    For each scene, identify what narration expansion and platform adaptation is needed
    to turn the storyboard into a final, publish-ready script.
    """

    try:
        analysis = await provider.generate_text(prompt)
        return {"intent": analysis}
    except Exception as e:
        return {"error": f"Failed to analyze storyboard context: {str(e)}"}


async def generate_script(state: AIState) -> Dict[str, Any]:
    """
    Generate the final script by expanding each storyboard scene into a
    complete, platform-adapted script section.
    """
    input_text = state.get("input_text", "")
    selected_opportunity = state.get("selected_opportunity", {})
    selected_platforms = state.get("selected_platforms", [])
    selected_angle = state.get("selected_angle", {})
    approved_strategy = state.get("approved_strategy", {})
    approved_storyboard = state.get("approved_storyboard", {})
    analysis = state.get("intent", "")

    if state.get("error") and state.get("retries", 0) >= 3:
        return {}  # Max retries reached — abort

    provider = get_provider()

    platform_name = selected_platforms[0].get("platform", "Unknown") if selected_platforms else "Unknown"
    platform_format = selected_platforms[0].get("recommendedFormat", "Short-form video") if selected_platforms else "Short-form video"

    scenes = approved_storyboard.get("scenes", [])
    scenes_detail = "\n".join([
        f"Scene {s.get('order')}: {s.get('title')} | Purpose: {s.get('purpose')} | "
        f"Narration: {s.get('narration')} | Visual: {s.get('visualDirection')} | "
        f"On-Screen: {s.get('onScreenText')} | Duration: {s.get('estimatedDuration')}"
        for s in scenes
    ])

    grounding_context = state.get("grounding_context", {})
    grounding_text = grounding_context.get("text", "")
    context_str = f"Extra Grounding Context (use if relevant):\n{grounding_text}\n\n" if grounding_text else ""

    approved_type = state.get("approved_content_type")
    type_str = f"""
CRITICAL INSTRUCTION:
The user has explicitly approved the Content Type: {approved_type}.
You MUST generate a final script that is 100% {approved_type}-oriented.
Do NOT recommend or output any other content type.
""" if approved_type else ""

    prompt = f"""
    Based on the following approved storyboard and complete workflow context, generate a final,
    publish-ready script. The script MUST follow the storyboard exactly — preserving scene order,
    narrative beats, and visual direction.
    
    {context_str}
    {type_str}
    Platform: {platform_name}
    Format: {platform_format}
    Tone: {approved_strategy.get('tone', 'Professional, accessible')}
    Hook Strategy: {approved_strategy.get('hookStrategy', '')}
    Core Message: {approved_strategy.get('coreMessage', '')}
    Call to Action: {approved_strategy.get('callToAction', '')}
    Target Audience: {approved_strategy.get('targetAudience', '')}

    Selected Topic Angle:
    Hook: {selected_angle.get('hook', '')}
    Core Promise: {selected_angle.get('corePromise', '')}

    Approved Storyboard Scenes (MUST be followed in order):
    {scenes_detail}

    Analysis Context:
    {analysis}

    Generate one ScriptSection per storyboard scene. The narration for each section
    should be the fully polished, platform-adapted version of the scene's narration.
    Adapt tone for {platform_name} — {platform_format}.
    """

    try:
        result = await provider.generate_structured(prompt, ScriptOutput)
        return {
            "structured_output": result.model_dump(),
            "error": None
        }
    except Exception as e:
        retries = state.get("retries", 0)
        return {
            "error": f"Failed to generate script: {str(e)}",
            "retries": retries + 1
        }


async def validate_script_result(state: AIState) -> Dict[str, Any]:
    """Validate that the generated script has the required structure."""
    if state.get("error"):
        return state

    output = state.get("structured_output")
    if not output or "script" not in output:
        return {"error": "Missing 'script' key in generated output"}

    script = output["script"]
    if not isinstance(script.get("sections"), list) or len(script["sections"]) == 0:
        return {"error": "Generated script has no sections"}

    return state
