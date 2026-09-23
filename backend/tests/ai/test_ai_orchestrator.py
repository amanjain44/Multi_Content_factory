import pytest
from app.ai.schemas import AIState, ContentPlanOutput
from app.ai.nodes.demo_nodes import analyze_input, generate_result, validate_result
from app.ai.graphs.demo_graph import should_retry, build_demo_graph
from app.ai.services.ai_orchestrator import AIOrchestrator
from unittest.mock import patch, MagicMock, AsyncMock

@pytest.mark.asyncio
async def test_analyze_input():
    initial_state: AIState = {
        "input_text": "Test input",
        "intent": None,
        "keywords": None,
        "structured_output": None,
        "error": None,
        "retries": 0
    }
    
    with patch("app.ai.nodes.demo_nodes.get_provider") as mock_get_provider:
        mock_provider = AsyncMock()
        mock_provider.generate_text.return_value = "Mock text"
        mock_get_provider.return_value = mock_provider
        
        state = await analyze_input(initial_state)
        
        assert state["intent"] == "Content Planning"
        assert "AI" in state["keywords"]

@pytest.mark.asyncio
async def test_generate_result_success():
    state: AIState = {
        "input_text": "Test",
        "intent": "Content Planning",
        "keywords": ["AI"],
        "structured_output": None,
        "error": None,
        "retries": 0
    }
    
    with patch("app.ai.nodes.demo_nodes.get_provider") as mock_get_provider:
        mock_provider = AsyncMock()
        mock_provider.generate_structured.return_value = ContentPlanOutput(
            summary="Test",
            audience="Devs",
            key_points=["Point"],
            suggested_angles=["Angle"]
        )
        mock_get_provider.return_value = mock_provider
        
        new_state = await generate_result(state)
        
        assert new_state["structured_output"] is not None
        assert new_state["structured_output"]["summary"] == "Test"
        assert new_state["error"] is None

@pytest.mark.asyncio
async def test_generate_result_failure():
    state: AIState = {
        "input_text": "Test",
        "intent": "Content Planning",
        "keywords": ["AI"],
        "structured_output": None,
        "error": None,
        "retries": 1
    }
    
    with patch("app.ai.nodes.demo_nodes.get_provider") as mock_get_provider:
        mock_provider = AsyncMock()
        mock_provider.generate_structured.side_effect = Exception("API Failed")
        mock_get_provider.return_value = mock_provider
        
        new_state = await generate_result(state)
        
        assert new_state["error"] == "API Failed"
        assert new_state["retries"] == 2

def test_should_retry():
    # Test retry logic
    state_no_error: AIState = {"error": None, "retries": 0, "input_text": ""}
    assert should_retry(state_no_error) == "validate_result"
    
    state_with_error_can_retry: AIState = {"error": "Failed", "retries": 1, "input_text": ""}
    assert should_retry(state_with_error_can_retry) == "generate_result"
    
    state_with_error_max_retries: AIState = {"error": "Failed", "retries": 3, "input_text": ""}
    assert should_retry(state_with_error_max_retries) == "__end__"

@pytest.mark.asyncio
async def test_integration_demo_graph():
    # This integration test runs the full graph using the DemoProvider
    # We patch settings to ensure AI_PROVIDER is 'demo'
    with patch("app.core.config.settings.AI_PROVIDER", "demo"):
        orchestrator = AIOrchestrator()
        result = await orchestrator.run_content_plan("Create a plan for an AI coding assistant")
        
        assert "summary" in result
        assert "audience" in result
        assert isinstance(result["summary"], str)
        assert len(result["summary"]) > 0

