import pytest
from app.ai.schemas import AIState, ContentStrategyOutput, ContentStrategy
from app.ai.nodes.content_strategy_nodes import analyze_context, generate_strategy, validate_result
from app.ai.graphs.content_strategy_graph import should_retry
from app.ai.services.ai_orchestrator import AIOrchestrator
from unittest.mock import patch, AsyncMock

@pytest.mark.asyncio
async def test_analyze_context():
    initial_state: AIState = {
        "input_text": "Source",
        "selected_opportunity": {"title": "Title"},
        "selected_platforms": [{"platform": "LinkedIn"}],
        "selected_angle": {"title": "Title", "angle": "Angle"},
        "intent": None,
        "keywords": None,
        "structured_output": None,
        "error": None,
        "retries": 0
    }
    
    with patch("app.ai.nodes.content_strategy_nodes.get_provider") as mock_get_provider:
        mock_provider = AsyncMock()
        mock_provider.generate_text.return_value = "Mock intent"
        mock_get_provider.return_value = mock_provider
        
        state = await analyze_context(initial_state)
        assert state["intent"] == "Mock intent"

@pytest.mark.asyncio
async def test_generate_strategy_success():
    state: AIState = {
        "input_text": "Source",
        "selected_opportunity": {"title": "Title"},
        "selected_platforms": [{"platform": "LinkedIn"}],
        "selected_angle": {"title": "Title", "angle": "Angle"},
        "intent": "Mock intent",
        "keywords": None,
        "structured_output": None,
        "error": None,
        "retries": 0
    }
    
    with patch("app.ai.nodes.content_strategy_nodes.get_provider") as mock_get_provider:
        mock_provider = AsyncMock()
        mock_provider.generate_structured.return_value = ContentStrategyOutput(
            strategy=ContentStrategy(
                id="strat-1",
                projectId="proj-1",
                objective="Obj",
                targetAudience="Aud",
                coreMessage="Msg",
                valueProposition="Prop",
                tone="Tone",
                format="Fmt",
                hookStrategy="Hook",
                keyTalkingPoints=["P1"],
                callToAction="CTA",
                contentStructure="Struct",
                platformAdaptations=[]
            )
        )
        mock_get_provider.return_value = mock_provider
        
        new_state = await generate_strategy(state)
        
        assert new_state["structured_output"] is not None
        assert "strategy" in new_state["structured_output"]
        assert new_state["error"] is None

def test_should_retry():
    state_no_error: AIState = {"error": None, "retries": 0, "input_text": ""}
    assert should_retry(state_no_error) == "validate_result"
    
    state_with_error_can_retry: AIState = {"error": "Failed", "retries": 1, "input_text": ""}
    assert should_retry(state_with_error_can_retry) == "generate_strategy"
    
    state_with_error_max_retries: AIState = {"error": "Failed", "retries": 3, "input_text": ""}
    assert should_retry(state_with_error_max_retries) == "__end__"

@pytest.mark.asyncio
async def test_integration_content_strategy_graph():
    with patch("app.core.config.settings.AI_PROVIDER", "demo"):
        orchestrator = AIOrchestrator()
        selected_opp = {"title": "Title"}
        selected_plats = [{"platform": "LinkedIn"}]
        selected_angle = {"title": "Title"}
        result = await orchestrator.run_content_strategy("Source", selected_opp, selected_plats, selected_angle)
        
        assert "strategy" in result
        assert isinstance(result["strategy"]["objective"], str)
        assert len(result["strategy"]["objective"]) > 0
