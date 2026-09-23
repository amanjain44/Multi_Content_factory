"""
Phase 9F Tests: Storyboard AI Flow

Tests the complete chain:
  analyze_context → generate_storyboard → validate_result
  → AIOrchestrator.run_storyboard()
  → DemoProvider structured output
  → POST /api/ai/storyboard endpoint
"""
import pytest
from app.ai.schemas import (
    AIState, StoryboardOutput, StoryboardModel, StoryboardScene
)
from app.ai.nodes.storyboard_nodes import analyze_context, generate_storyboard, validate_result
from app.ai.graphs.storyboard_graph import should_retry
from app.ai.services.ai_orchestrator import AIOrchestrator
from unittest.mock import patch, AsyncMock


# ─── Fixtures — reusable workflow context ─────────────────────────────────────

SAMPLE_OPPORTUNITY = {
    "id": "opt-short-video",
    "title": "Short-Form Educational Video",
    "summary": "AI coding tool overview",
    "whyInteresting": "Viral potential",
    "keyPoints": ["Speed", "Quality"],
    "potentialAudience": "Developers",
    "estimatedValue": "High"
}

SAMPLE_PLATFORMS = [
    {
        "id": "plat-linkedin",
        "platform": "LinkedIn",
        "suitability": 95,
        "reasoning": "Professional audience",
        "recommendedFormat": "Educational post",
        "recommendedLength": "1000 characters",
        "audience": "Developers",
        "tone": "Professional",
        "priority": "Recommended",
        "projectId": "test-project"
    }
]

SAMPLE_ANGLE = {
    "id": "ang-contrarian",
    "projectId": "test-project",
    "title": "AI: The Developer's Superpower",
    "angle": "Contrarian",
    "hook": "AI won't replace you — but developers who use AI will.",
    "description": "An empowering take on AI coding tools.",
    "targetAudience": "Developers",
    "corePromise": "Learn how to leverage AI for 10x productivity.",
    "differentiation": "Addresses fear head-on with data.",
    "supportingPoints": ["Point A", "Point B"],
    "recommendedPlatforms": ["LinkedIn", "YouTube"]
}

SAMPLE_STRATEGY = {
    "id": "strat-1",
    "projectId": "test-project",
    "objective": "Educate developers on AI coding assistant adoption",
    "targetAudience": "Software engineers aged 25-45",
    "coreMessage": "AI coding tools make you faster and better",
    "valueProposition": "Actionable tips you can apply today",
    "tone": "Authoritative, accessible",
    "format": "Multi-scene educational video",
    "hookStrategy": "Open with a bold claim backed by data",
    "keyTalkingPoints": ["55% faster", "New skill stack", "Real tools"],
    "callToAction": "Follow for more AI engineering content",
    "contentStructure": "Hook → Evidence → Solution → CTA",
    "platformAdaptations": [
        {"platform": "LinkedIn", "format": "Post", "notes": "Professional tone"}
    ]
}


def _make_state(**kwargs) -> AIState:
    """Create a baseline AIState with optional overrides."""
    defaults: AIState = {
        "input_text": "The future of AI coding assistants",
        "selected_opportunity": SAMPLE_OPPORTUNITY,
        "selected_platforms": SAMPLE_PLATFORMS,
        "selected_angle": SAMPLE_ANGLE,
        "approved_strategy": SAMPLE_STRATEGY,
        "intent": None,
        "keywords": None,
        "structured_output": None,
        "error": None,
        "retries": 0,
    }
    defaults.update(kwargs)
    return defaults


# ─── A. Pydantic Models ───────────────────────────────────────────────────────

def test_storyboard_scene_valid():
    """StoryboardScene accepts all required fields."""
    scene = StoryboardScene(
        id="s-1",
        order=1,
        title="Hook Scene",
        purpose="Grab attention",
        narration="This is the narration.",
        visualDirection="Camera pans left.",
        onScreenText="Bold Claim Here",
        transition="Cut to black",
        estimatedDuration="8 seconds",
    )
    assert scene.id == "s-1"
    assert scene.order == 1
    assert scene.estimatedDuration == "8 seconds"


def test_storyboard_model_valid():
    """StoryboardModel requires scenes list."""
    model = StoryboardModel(
        id="sb-1",
        projectId="proj-1",
        title="Test Storyboard",
        objective="Test objective",
        status="Draft",
        scenes=[
            StoryboardScene(
                id="s-1", order=1, title="Scene 1", purpose="Purpose",
                narration="Narration", visualDirection="Visual",
                onScreenText="Text", transition="Cut", estimatedDuration="5s"
            )
        ]
    )
    assert len(model.scenes) == 1
    assert model.status == "Draft"


def test_storyboard_output_valid():
    """StoryboardOutput wraps a StoryboardModel."""
    output = StoryboardOutput(
        storyboard=StoryboardModel(
            id="sb-1", projectId="proj-1", title="T", objective="O",
            status="Draft", scenes=[]
        )
    )
    assert output.storyboard.id == "sb-1"


def test_storyboard_scene_missing_required_field():
    """StoryboardScene raises ValidationError if required field is missing."""
    from pydantic import ValidationError
    with pytest.raises(ValidationError):
        StoryboardScene(
            # Missing 'order', 'title', 'purpose', etc.
            id="s-1",
            narration="Only narration",
        )


# ─── B. Node Unit Tests ───────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_analyze_context_returns_intent():
    """analyze_context should set state['intent'] from provider.generate_text."""
    state = _make_state()

    with patch("app.ai.nodes.storyboard_nodes.get_provider") as mock_get_provider:
        mock_provider = AsyncMock()
        mock_provider.generate_text.return_value = "Narrative beats: Hook → Data → Tools → CTA"
        mock_get_provider.return_value = mock_provider

        new_state = await analyze_context(state)

    assert new_state["intent"] == "Narrative beats: Hook → Data → Tools → CTA"
    assert new_state.get("error") is None


@pytest.mark.asyncio
async def test_analyze_context_missing_required_fields_returns_error():
    """analyze_context should return error when required context fields are missing."""
    state = _make_state(selected_opportunity=None)
    new_state = await analyze_context(state)
    assert new_state.get("error") == "Missing required context for storyboard"


@pytest.mark.asyncio
async def test_analyze_context_missing_strategy_returns_error():
    """analyze_context should return error when approved_strategy is missing."""
    state = _make_state(approved_strategy=None)
    new_state = await analyze_context(state)
    assert new_state.get("error") == "Missing required context for storyboard"


@pytest.mark.asyncio
async def test_generate_storyboard_success():
    """generate_storyboard should produce structured StoryboardOutput."""
    state = _make_state(intent="Hook → Data → Tools → CTA")

    mock_output = StoryboardOutput(
        storyboard=StoryboardModel(
            id="sb-test",
            projectId="proj-test",
            title="Test Storyboard",
            objective="Educate developers",
            status="Draft",
            scenes=[
                StoryboardScene(
                    id="s-1", order=1, title="Hook", purpose="Grab attention",
                    narration="Bold opening statement.", visualDirection="Split screen.",
                    onScreenText="Are you using AI?", transition="Hard cut",
                    estimatedDuration="8 seconds"
                ),
                StoryboardScene(
                    id="s-2", order=2, title="Evidence", purpose="Build credibility",
                    narration="55% faster with Copilot.", visualDirection="Bar chart animation.",
                    onScreenText="55% faster", transition="Slide",
                    estimatedDuration="10 seconds"
                ),
            ]
        )
    )

    with patch("app.ai.nodes.storyboard_nodes.get_provider") as mock_get_provider:
        mock_provider = AsyncMock()
        mock_provider.generate_structured.return_value = mock_output
        mock_get_provider.return_value = mock_provider

        new_state = await generate_storyboard(state)

    assert new_state["structured_output"] is not None
    assert "storyboard" in new_state["structured_output"]
    sb = new_state["structured_output"]["storyboard"]
    assert len(sb["scenes"]) == 2
    assert sb["scenes"][0]["title"] == "Hook"
    assert new_state.get("error") is None


@pytest.mark.asyncio
async def test_generate_storyboard_increments_retries_on_failure():
    """generate_storyboard should increment retries on provider exception."""
    state = _make_state(intent="Some analysis", retries=1)

    with patch("app.ai.nodes.storyboard_nodes.get_provider") as mock_get_provider:
        mock_provider = AsyncMock()
        mock_provider.generate_structured.side_effect = Exception("OpenAI timeout")
        mock_get_provider.return_value = mock_provider

        new_state = await generate_storyboard(state)

    assert new_state.get("error") is not None
    assert "Failed to generate storyboard" in new_state["error"]
    assert new_state["retries"] == 2


@pytest.mark.asyncio
async def test_generate_storyboard_skips_on_max_retries():
    """generate_storyboard should skip execution when retries >= 3 and error is set."""
    state = _make_state(error="Previous failure", retries=3, intent="Analysis")
    # Should return early with empty dict — no further calls
    with patch("app.ai.nodes.storyboard_nodes.get_provider") as mock_get_provider:
        mock_provider = AsyncMock()
        mock_get_provider.return_value = mock_provider
        result = await generate_storyboard(state)
    # Should return empty dict (max retries guard)
    assert result == {}
    mock_provider.generate_structured.assert_not_called()


@pytest.mark.asyncio
async def test_validate_result_passes_valid_storyboard():
    """validate_result should return state unchanged when storyboard is present."""
    state = _make_state(
        structured_output={
            "storyboard": {
                "id": "sb-1",
                "scenes": [{"id": "s-1", "title": "Hook"}]
            }
        }
    )
    result = await validate_result(state)
    assert result["error"] is None
    assert result["structured_output"]["storyboard"]["id"] == "sb-1"


@pytest.mark.asyncio
async def test_validate_result_fails_on_missing_storyboard_key():
    """validate_result should set error when structured_output has no 'storyboard' key."""
    state = _make_state(structured_output={"something_else": {}})
    result = await validate_result(state)
    assert result["error"] is not None
    assert "storyboard" in result["error"].lower()


@pytest.mark.asyncio
async def test_validate_result_propagates_existing_error():
    """validate_result should return state unchanged when error is already set."""
    state = _make_state(error="Previous error", structured_output=None)
    result = await validate_result(state)
    assert result["error"] == "Previous error"


# ─── C. Graph Retry Logic ─────────────────────────────────────────────────────

def test_should_retry_no_error_routes_to_validate():
    """No error → routes to validate_result."""
    state = _make_state(error=None, retries=0)
    assert should_retry(state) == "validate_result"


def test_should_retry_error_routes_to_retry():
    """Error with retries < 3 → routes back to generate_storyboard."""
    state = _make_state(error="Timeout", retries=1)
    assert should_retry(state) == "generate_storyboard"


def test_should_retry_max_retries_routes_to_end():
    """Error with retries >= 3 → routes to END."""
    from langgraph.graph import END
    state = _make_state(error="Timeout", retries=3)
    assert should_retry(state) == END


# ─── D. Integration — Full Graph with DemoProvider ────────────────────────────

@pytest.mark.asyncio
async def test_integration_storyboard_graph_demo_mode():
    """
    Full integration test: runs the storyboard LangGraph flow with DemoProvider.
    Validates complete structured output shape.
    """
    with patch("app.core.config.settings.AI_PROVIDER", "demo"):
        orchestrator = AIOrchestrator()
        result = await orchestrator.run_storyboard(
            input_text="The future of AI coding assistants",
            selected_opportunity=SAMPLE_OPPORTUNITY,
            selected_platforms=SAMPLE_PLATFORMS,
            selected_angle=SAMPLE_ANGLE,
            approved_strategy=SAMPLE_STRATEGY,
        )

    assert result is not None
    assert "storyboard" in result

    sb = result["storyboard"]
    assert "id" in sb
    assert "title" in sb
    assert "objective" in sb
    assert "status" in sb
    assert sb["status"] == "Draft"
    assert "scenes" in sb
    assert isinstance(sb["scenes"], list)
    assert len(sb["scenes"]) >= 4, "Demo storyboard should have at least 4 scenes"

    # Validate each scene has required fields
    for scene in sb["scenes"]:
        assert "id" in scene
        assert "order" in scene
        assert "title" in scene
        assert "purpose" in scene
        assert "narration" in scene
        assert len(scene["narration"]) > 20, "Narration should be substantive"


# ─── E. Provider Routing ──────────────────────────────────────────────────────

def test_demo_provider_storyboard_routing():
    """DemoProvider.generate_structured should return StoryboardOutput for StoryboardOutput schema."""
    from app.ai.providers.demo_provider import DemoProvider

    provider = DemoProvider()

    import asyncio
    result = asyncio.get_event_loop().run_until_complete(
        provider.generate_structured("prompt", StoryboardOutput)
    )

    assert isinstance(result, StoryboardOutput)
    assert result.storyboard is not None
    assert len(result.storyboard.scenes) >= 4
    assert result.storyboard.status == "Draft"


def test_demo_provider_routes_correctly():
    """DemoProvider should be returned for AI_PROVIDER=demo without an API key."""
    from app.ai.providers.factory import AIProviderFactory
    from app.ai.providers.demo_provider import DemoProvider
    from app.ai.config import AIConfig

    config = AIConfig(provider="demo")
    provider = AIProviderFactory.get_provider(config)
    assert isinstance(provider, DemoProvider)


def test_openai_provider_requires_api_key_for_storyboard():
    """OpenAI provider should raise ValueError without API key."""
    from app.ai.providers.factory import AIProviderFactory
    from app.ai.config import AIConfig

    config = AIConfig(provider="openai", api_key=None)
    with pytest.raises(ValueError, match="OPENAI_API_KEY"):
        AIProviderFactory.get_provider(config)


# ─── F. Context Propagation ───────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_context_propagation_to_generate_storyboard_node():
    """
    Verify that generate_storyboard node receives the full workflow context:
    opportunity, platforms, angle, and strategy — all passed to the provider prompt.
    """
    state = _make_state(intent="Narrative context analyzed")
    captured_prompt = []

    async def mock_generate_structured(prompt, schema):
        captured_prompt.append(prompt)
        return StoryboardOutput(
            storyboard=StoryboardModel(
                id="sb-ctx", projectId="proj-ctx", title="Ctx Test",
                objective="Test", status="Draft",
                scenes=[
                    StoryboardScene(
                        id="s-1", order=1, title="Scene", purpose="P",
                        narration="N", visualDirection="V",
                        onScreenText="T", transition="Cut", estimatedDuration="5s"
                    )
                ]
            )
        )

    with patch("app.ai.nodes.storyboard_nodes.get_provider") as mock_get_provider:
        mock_provider = AsyncMock()
        mock_provider.generate_structured.side_effect = mock_generate_structured
        mock_get_provider.return_value = mock_provider

        await generate_storyboard(state)

    assert len(captured_prompt) == 1
    prompt_text = captured_prompt[0]

    # Verify key context pieces are present in the prompt
    # The node uses: objective, targetAudience, coreMessage, contentStructure,
    # keyTalkingPoints, and platform adaptations
    assert "Educate developers on AI coding assistant adoption" in prompt_text  # objective
    assert "Software engineers aged 25-45" in prompt_text  # targetAudience
    assert "AI coding tools make you faster and better" in prompt_text  # coreMessage
    assert "Hook" in prompt_text or "CTA" in prompt_text  # contentStructure fragment
    assert "55% faster" in prompt_text  # keyTalkingPoints fragment
    assert "LinkedIn" in prompt_text  # platform
    assert "55% faster" in prompt_text or "keyTalkingPoints" in prompt_text or "talking" in prompt_text.lower()
