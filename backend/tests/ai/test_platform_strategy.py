import pytest
from app.ai.schemas import AIState, PlatformStrategyOutput, PlatformRecommendation
from app.ai.nodes.platform_strategy_nodes import analyze_content, generate_platforms, validate_result
from app.ai.graphs.platform_strategy_graph import should_retry
from app.ai.services.ai_orchestrator import AIOrchestrator
from unittest.mock import patch, AsyncMock

@pytest.mark.asyncio
async def test_analyze_content():
    initial_state: AIState = {
        "input_text": "The future of AI coding assistants",
        "selected_opportunity": {
            "title": "Title",
            "summary": "Summary",
            "potentialAudience": "Devs",
            "keyPoints": ["Point"]
        },
        "intent": None,
        "keywords": None,
        "structured_output": None,
        "error": None,
        "retries": 0
    }
    
    with patch("app.ai.nodes.platform_strategy_nodes.get_provider") as mock_get_provider:
        mock_provider = AsyncMock()
        mock_provider.generate_text.return_value = "Mock analysis"
        mock_get_provider.return_value = mock_provider
        
        state = await analyze_content(initial_state)
        
        assert state["intent"] == "Mock analysis"

@pytest.mark.asyncio
async def test_generate_platforms_success():
    state: AIState = {
        "input_text": "Test",
        "selected_opportunity": {"title": "Title"},
        "intent": "Mock analysis",
        "keywords": None,
        "structured_output": None,
        "error": None,
        "retries": 0
    }
    
    with patch("app.ai.nodes.platform_strategy_nodes.get_provider") as mock_get_provider:
        mock_provider = AsyncMock()
        mock_provider.generate_structured.return_value = PlatformStrategyOutput(
            recommendations=[
                PlatformRecommendation(
                    id="plat-1",
                    projectId="proj-1",
                    platform="LinkedIn",
                    suitability=90,
                    reasoning="Good",
                    recommendedFormat="Post",
                    recommendedLength="Short",
                    audience="Devs",
                    tone="Pro",
                    priority="Recommended"
                )
            ]
        )
        mock_get_provider.return_value = mock_provider
        
        new_state = await generate_platforms(state)
        
        assert new_state["structured_output"] is not None
        assert "recommendations" in new_state["structured_output"]
        assert new_state["error"] is None

def test_should_retry():
    state_no_error: AIState = {"error": None, "retries": 0, "input_text": ""}
    assert should_retry(state_no_error) == "validate_result"
    
    state_with_error_can_retry: AIState = {"error": "Failed", "retries": 1, "input_text": ""}
    assert should_retry(state_with_error_can_retry) == "generate_platforms"
    
    state_with_error_max_retries: AIState = {"error": "Failed", "retries": 3, "input_text": ""}
    assert should_retry(state_with_error_max_retries) == "__end__"

@pytest.mark.asyncio
async def test_integration_platform_strategy_graph():
    with patch("app.core.config.settings.AI_PROVIDER", "demo"):
        orchestrator = AIOrchestrator()
        selected_opp = {"title": "Title", "summary": "Summary"}
        result = await orchestrator.run_platform_strategy("Source text", selected_opp)
        
        assert "recommendations" in result
        assert len(result["recommendations"]) > 0
        assert result["recommendations"][0]["platform"] == "LinkedIn"
