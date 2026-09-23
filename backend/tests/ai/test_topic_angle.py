import pytest
from app.ai.schemas import AIState, TopicAngleOutput, TopicAngle
from app.ai.nodes.topic_angle_nodes import analyze_context, generate_angles, validate_result
from app.ai.graphs.topic_angle_graph import should_retry
from app.ai.services.ai_orchestrator import AIOrchestrator
from unittest.mock import patch, AsyncMock

@pytest.mark.asyncio
async def test_analyze_context():
    initial_state: AIState = {
        "input_text": "Source",
        "selected_opportunity": {"title": "Title"},
        "selected_platforms": [{"platform": "LinkedIn"}],
        "intent": None,
        "keywords": None,
        "structured_output": None,
        "error": None,
        "retries": 0
    }
    
    with patch("app.ai.nodes.topic_angle_nodes.get_provider") as mock_get_provider:
        mock_provider = AsyncMock()
        mock_provider.generate_text.return_value = "Mock intent"
        mock_get_provider.return_value = mock_provider
        
        state = await analyze_context(initial_state)
        assert state["intent"] == "Mock intent"

@pytest.mark.asyncio
async def test_generate_angles_success():
    state: AIState = {
        "input_text": "Source",
        "selected_opportunity": {"title": "Title"},
        "selected_platforms": [{"platform": "LinkedIn"}],
        "intent": "Mock intent",
        "keywords": None,
        "structured_output": None,
        "error": None,
        "retries": 0
    }
    
    with patch("app.ai.nodes.topic_angle_nodes.get_provider") as mock_get_provider:
        mock_provider = AsyncMock()
        mock_provider.generate_structured.return_value = TopicAngleOutput(
            angles=[
                TopicAngle(
                    id="ang-1",
                    projectId="proj-1",
                    title="Title",
                    angle="Angle",
                    hook="Hook",
                    description="Desc",
                    targetAudience="Audience",
                    corePromise="Promise",
                    differentiation="Diff",
                    supportingPoints=["P1"],
                    recommendedPlatforms=["LinkedIn"]
                )
            ]
        )
        mock_get_provider.return_value = mock_provider
        
        new_state = await generate_angles(state)
        
        assert new_state["structured_output"] is not None
        assert "angles" in new_state["structured_output"]
        assert new_state["error"] is None

def test_should_retry():
    state_no_error: AIState = {"error": None, "retries": 0, "input_text": ""}
    assert should_retry(state_no_error) == "validate_result"
    
    state_with_error_can_retry: AIState = {"error": "Failed", "retries": 1, "input_text": ""}
    assert should_retry(state_with_error_can_retry) == "generate_angles"
    
    state_with_error_max_retries: AIState = {"error": "Failed", "retries": 3, "input_text": ""}
    assert should_retry(state_with_error_max_retries) == "__end__"

@pytest.mark.asyncio
async def test_integration_topic_angle_graph():
    with patch("app.core.config.settings.AI_PROVIDER", "demo"):
        orchestrator = AIOrchestrator()
        selected_opp = {"title": "Title"}
        selected_plats = [{"platform": "LinkedIn"}]
        result = await orchestrator.run_topic_angle("Source", selected_opp, selected_plats)
        
        assert "angles" in result
        assert len(result["angles"]) > 0
        assert isinstance(result["angles"][0]["angle"], str)
        assert len(result["angles"][0]["angle"]) > 0
