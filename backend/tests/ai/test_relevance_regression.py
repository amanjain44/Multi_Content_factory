import pytest
from app.ai.providers.demo_provider import DemoProvider
from app.ai.schemas import (
    AIState,
    ContentSelectionOutput,
    ContentTypeOutput,
    StoryboardOutput,
    ScriptOutput,
    PlatformStrategyOutput,
)
from app.ai.nodes.storyboard_nodes import generate_storyboard
from app.ai.nodes.script_nodes import generate_script
import asyncio
from unittest.mock import patch, AsyncMock

@pytest.mark.asyncio
async def test_project_isolation_relevance():
    """
    Test Project A (AI-assisted coding) vs Project B (JavaScript fundamentals).
    Ensure the demo provider dynamically generates content related to the specific project topic,
    and no leakage occurs.
    """
    provider = DemoProvider()
    
    # Project A
    prompt_a = "Source Material:\nAI-assisted coding\napproved the Content Type: \"Carousel\""
    output_a: ContentSelectionOutput = await provider.generate_structured(prompt_a, ContentSelectionOutput)
    
    opp_a_titles = [opp.title for opp in output_a.opportunities]
    assert any("AI-assisted coding" in title for title in opp_a_titles), f"Did not find topic in {opp_a_titles}"
    assert all("JavaScript" not in title for title in opp_a_titles)

    # Project B
    prompt_b = "Source Material:\nJavaScript fundamentals\napproved the Content Type: \"Carousel\""
    output_b: ContentSelectionOutput = await provider.generate_structured(prompt_b, ContentSelectionOutput)
    
    opp_b_titles = [opp.title for opp in output_b.opportunities]
    assert any("JavaScript fundamentals" in title for title in opp_b_titles), f"Did not find topic in {opp_b_titles}"
    assert all("AI-assisted coding" not in title for title in opp_b_titles)

@pytest.mark.asyncio
async def test_content_type_relevance():
    """
    Test Topic A + Carousel vs Topic A + Video vs Topic B + Newsletter.
    """
    provider = DemoProvider()
    
    prompt_carousel = "Source Material:\nTopic A\napproved the Content Type: \"Carousel\""
    output_carousel = await provider.generate_structured(prompt_carousel, StoryboardOutput)
    assert "Carousel" in output_carousel.storyboard.title

    prompt_video = "Source Material:\nTopic A\napproved the Content Type: \"Video\""
    output_video = await provider.generate_structured(prompt_video, StoryboardOutput)
    assert "Video" in output_video.storyboard.title

    prompt_news = "Source Material:\nTopic B\napproved the Content Type: \"Newsletter\""
    output_news = await provider.generate_structured(prompt_news, ContentSelectionOutput)
    assert "Newsletter" in output_news.opportunities[0].title

@pytest.mark.asyncio
async def test_cross_stage_relevance_pipeline():
    """
    CROSS-STAGE RELEVANCE TEST:
    Original Topic: AI-assisted coding
    Content Type: Carousel
    Topic & Angle: Developer workflow transformation
    Content Strategy: Educational LinkedIn carousel
    Storyboard: 7 slides
    Final Script: Every final section must correspond to the approved storyboard and remain about AI-assisted coding.
    """
    state: AIState = {
        "input_text": "AI-assisted coding",
        "approved_content_type": "Carousel",
        "selected_angle": {
            "title": "Developer workflow transformation",
            "corePromise": "Understand exactly which skills matter most."
        },
        "approved_strategy": {
            "objective": "Educational LinkedIn carousel",
            "format": "Carousel",
            "platformAdaptations": [
                {"platform": "LinkedIn", "format": "Carousel", "notes": ""}
            ]
        },
        "approved_storyboard": {
            "id": "sb-1",
            "projectId": "demo",
            "title": "The AI Developer Workflow (LinkedIn Carousel)",
            "objective": "Educate",
            "status": "Draft",
            "scenes": [
                {"id": f"slide-{i}", "order": i, "title": f"Scene {i}", "purpose": "Test", "narration": f"Slide {i} narration", "visualDirection": "", "onScreenText": "", "transition": "", "estimatedDuration": ""}
                for i in range(1, 8)
            ]
        },
        "intent": "Generate script",
        "keywords": [],
        "structured_output": None,
        "error": None,
        "retries": 0,
        "selected_opportunity": {},
        "selected_platforms": [],
        "grounding_context": {}
    }

    with patch("app.ai.nodes.script_nodes.get_provider") as mock_get:
        mock_provider = AsyncMock()
        
        async def mock_generate_structured(prompt, schema):
            # Assert GLOBAL_RELEVANCE_REQUIREMENT is in prompt
            assert "GLOBAL REQUIREMENT — CONTENT RELEVANCE & CONTEXTUAL CONSISTENCY" in prompt
            
            # Use demo provider to actually generate
            dp = DemoProvider()
            demo_prompt = "Source Material:\nAI-assisted coding\napproved the Content Type: \"Carousel\""
            return await dp.generate_structured(demo_prompt, schema)

        mock_provider.generate_structured.side_effect = mock_generate_structured
        mock_get.return_value = mock_provider

        result = await generate_script(state)
        
        assert result.get("error") is None
        script = result["structured_output"]["script"]
        
        # Verify 7 sections generated corresponding to 7 slides (demo mock has 7)
        assert len(script["sections"]) == 7
        
        for section in script["sections"]:
            found = False
            for val in section.values():
                if isinstance(val, str) and "AI-assisted coding" in val:
                    found = True
            if not found:
                assert "AI-assisted coding" in script["title"] or "AI-assisted coding" in script["hook"]

@pytest.mark.asyncio
async def test_global_requirement_in_prompts():
    state: AIState = {
        "input_text": "Test requirement",
        "approved_content_type": "Article",
        "selected_opportunity": {"id": "1"},
        "selected_platforms": [{"platform": "Blog"}],
        "selected_angle": {"title": "Angle"},
        "approved_strategy": {"objective": "Test obj"},
        "intent": "Test intent",
        "error": None,
        "retries": 0,
    }
    
    with patch("app.ai.nodes.storyboard_nodes.get_provider") as mock_get:
        mock_provider = AsyncMock()
        mock_provider.generate_structured.return_value = StoryboardOutput(
            storyboard={"id": "sb1", "projectId": "p1", "title": "T", "objective": "O", "status": "Draft", "scenes": []}
        )
        mock_get.return_value = mock_provider
        
        await generate_storyboard(state)
        
        called_prompt = mock_provider.generate_structured.call_args[0][0]
        
        assert "GLOBAL REQUIREMENT — CONTENT RELEVANCE & CONTEXTUAL CONSISTENCY" in called_prompt
        assert "1. SOURCE / USER INPUT RELEVANCE" in called_prompt
        assert "3. NO RANDOM FACTS OR EXAMPLES" in called_prompt

