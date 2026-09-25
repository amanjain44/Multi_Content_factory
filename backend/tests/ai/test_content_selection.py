"""
Phase 9B Tests: Content Selection AI Flow

Tests the full chain:
  analyze_source node → generate_recommendations node → validate_result node
  → AIOrchestrator.run_content_selection()
  → DemoProvider structured output
  → POST /api/ai/content-selection endpoint
"""
import pytest
from app.ai.schemas import AIState, ContentSelectionOutput, ContentOpportunity
from app.ai.nodes.content_selection_nodes import analyze_source, generate_recommendations, validate_result
from app.ai.graphs.content_selection_graph import should_retry
from app.ai.services.ai_orchestrator import AIOrchestrator
from unittest.mock import patch, AsyncMock


# ─── Node Unit Tests ──────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_analyze_source_returns_intent():
    """analyze_source should set state['intent'] from provider.generate_text."""
    initial_state: AIState = {
        "input_text": "The future of AI coding assistants",
        "selected_opportunity": None,
        "selected_platforms": None,
        "selected_angle": None,
        "approved_strategy": None,
        "intent": None,
        "keywords": None,
        "structured_output": None,
        "error": None,
        "retries": 0,
    }

    with patch("app.ai.nodes.content_selection_nodes.get_provider") as mock_get_provider:
        mock_provider = AsyncMock()
        mock_provider.generate_text.return_value = "AI coding assistants are reshaping developer workflows"
        mock_get_provider.return_value = mock_provider

        state = await analyze_source(initial_state)

        assert state["intent"] == "AI coding assistants are reshaping developer workflows"


@pytest.mark.asyncio
async def test_analyze_source_empty_input_returns_error():
    """analyze_source should return an error when input_text is empty."""
    initial_state: AIState = {
        "input_text": "",
        "selected_opportunity": None,
        "selected_platforms": None,
        "selected_angle": None,
        "approved_strategy": None,
        "intent": None,
        "keywords": None,
        "structured_output": None,
        "error": None,
        "retries": 0,
    }
    state = await analyze_source(initial_state)
    assert "error" in state
    assert state["error"] == "Input text is empty"


@pytest.mark.asyncio
async def test_generate_recommendations_success():
    """generate_recommendations should produce structured output on success."""
    state: AIState = {
        "input_text": "The future of AI coding assistants",
        "selected_opportunity": None,
        "selected_platforms": None,
        "selected_angle": None,
        "approved_strategy": None,
        "intent": "AI coding reshaping software development",
        "keywords": None,
        "structured_output": None,
        "error": None,
        "retries": 0,
    }

    with patch("app.ai.nodes.content_selection_nodes.get_provider") as mock_get_provider:
        mock_provider = AsyncMock()
        mock_provider.generate_structured.return_value = ContentSelectionOutput(
            opportunities=[
                ContentOpportunity(
                    id="opt-1",
                    content_type="Video",
                    platform="YouTube",
                    title="Short-Form Educational Video",
                    summary="A punchy video about AI coding.",
                    whyInteresting="Developers love short-form content.",
                    keyPoints=["Doubles velocity", "Changes nature of coding", "Practical demo"],
                    potentialAudience="Software engineers and tech leads",
                    estimatedValue="High reach on LinkedIn and YouTube Shorts",
                )
            ]
        )
        mock_get_provider.return_value = mock_provider

        new_state = await generate_recommendations(state)

        assert new_state["structured_output"] is not None
        assert "opportunities" in new_state["structured_output"]
        assert len(new_state["structured_output"]["opportunities"]) == 1
        assert new_state["structured_output"]["opportunities"][0]["title"] == "Short-Form Educational Video"
        assert new_state["error"] is None


@pytest.mark.asyncio
async def test_generate_recommendations_increments_retries_on_failure():
    """generate_recommendations should increment retries on provider exception."""
    state: AIState = {
        "input_text": "Test input",
        "selected_opportunity": None,
        "selected_platforms": None,
        "selected_angle": None,
        "approved_strategy": None,
        "intent": "Some analysis",
        "keywords": None,
        "structured_output": None,
        "error": None,
        "retries": 1,
    }

    with patch("app.ai.nodes.content_selection_nodes.get_provider") as mock_get_provider:
        mock_provider = AsyncMock()
        mock_provider.generate_structured.side_effect = Exception("OpenAI timeout")
        mock_get_provider.return_value = mock_provider

        new_state = await generate_recommendations(state)

        assert new_state["error"] is not None
        assert "Failed to generate recommendations" in new_state["error"]
        assert new_state["retries"] == 2


@pytest.mark.asyncio
async def test_validate_result_passes_valid_output():
    """validate_result should return state unchanged when opportunities are present."""
    state: AIState = {
        "input_text": "test",
        "selected_opportunity": None,
        "selected_platforms": None,
        "selected_angle": None,
        "approved_strategy": None,
        "approved_content_type": "Video",
        "intent": None,
        "keywords": None,
        "structured_output": {
            "opportunities": [
                {
                    "id": "opt-1",
                    "content_type": "Video",
                    "platform": "YouTube",
                    "title": "Test",
                    "summary": "Summary",
                    "whyInteresting": "Why",
                    "keyPoints": ["Point"],
                    "potentialAudience": "Devs",
                    "estimatedValue": "High",
                }
            ]
        },
        "error": None,
        "retries": 0,
    }
    result = await validate_result(state)
    assert result.get("error") is None
    assert result["structured_output"]["opportunities"][0]["id"] == "opt-1"


@pytest.mark.asyncio
async def test_validate_result_fails_on_empty_opportunities():
    """validate_result should set error when opportunities list is empty."""
    state: AIState = {
        "input_text": "test",
        "selected_opportunity": None,
        "selected_platforms": None,
        "selected_angle": None,
        "approved_strategy": None,
        "intent": None,
        "keywords": None,
        "structured_output": {"opportunities": []},
        "error": None,
        "retries": 0,
    }
    result = await validate_result(state)
    assert result["error"] is not None


# ─── Graph Retry Logic ────────────────────────────────────────────────────────

def test_should_retry_routing():
    """Verify conditional edge logic: no error → validate, error+retries<3 → retry, max → END."""
    state_ok: AIState = {"error": None, "retries": 0, "input_text": ""}
    assert should_retry(state_ok) == "validate_result"

    state_retry: AIState = {"error": "Failed", "retries": 1, "input_text": ""}
    assert should_retry(state_retry) == "generate_recommendations"

    state_max: AIState = {"error": "Failed", "retries": 3, "input_text": ""}
    assert should_retry(state_max) == "__end__"


# ─── Integration: Full Graph with DemoProvider ────────────────────────────────

@pytest.mark.asyncio
async def test_integration_content_selection_graph_demo_mode():
    """
    Full integration test: runs the LangGraph content selection flow using
    the DemoProvider (AI_PROVIDER=demo). Validates structured output shape.
    """
    with patch("app.core.config.settings.AI_PROVIDER", "demo"):
        orchestrator = AIOrchestrator()
        result = await orchestrator.run_content_selection(
            "The future of AI coding assistants"
        )

    assert result is not None, "Orchestrator should return a result dict"
    assert "opportunities" in result, "Result must contain 'opportunities' key"
    assert isinstance(result["opportunities"], list), "Opportunities must be a list"
    assert len(result["opportunities"]) >= 1, "Demo mode should return at least 1 opportunity"

    # Validate each opportunity has required fields
    for opp in result["opportunities"]:
        assert "id" in opp, "Each opportunity must have an 'id'"
        assert "title" in opp, "Each opportunity must have a 'title'"
        assert "summary" in opp, "Each opportunity must have a 'summary'"
        assert "keyPoints" in opp or "key_points" in opp, "Each opportunity must have key points"
        assert "potentialAudience" in opp or "potential_audience" in opp, (
            "Each opportunity must have a potentialAudience"
        )


# ─── Provider Routing ─────────────────────────────────────────────────────────

def test_openai_provider_routing_requires_api_key():
    """
    OpenAI provider should be selected when AI_PROVIDER=openai.
    Without an API key, the factory should raise ValueError (not crash silently).
    """
    from app.ai.providers.factory import AIProviderFactory
    from app.ai.config import AIConfig

    config_no_key = AIConfig(provider="openai", api_key=None)
    with pytest.raises(ValueError, match="OPENAI_API_KEY"):
        AIProviderFactory.get_provider(config_no_key)


def test_demo_provider_routing_no_key_required():
    """DemoProvider should be returned for provider='demo' without any API key."""
    from app.ai.providers.factory import AIProviderFactory
    from app.ai.providers.demo_provider import DemoProvider
    from app.ai.config import AIConfig

    config = AIConfig(provider="demo")
    provider = AIProviderFactory.get_provider(config)
    assert isinstance(provider, DemoProvider)
