"""
Phase 9G — Comprehensive test suite for the Final Script AI stage.

Tests:
A. Pydantic models (ScriptSection, ScriptModel, ScriptOutput)
B. LangGraph node unit tests (analyze_storyboard_context, generate_script, validate_script_result)
C. LangGraph graph integration (script_graph)
D. Provider routing (Demo & OpenAI)
E. Context propagation (storyboard scenes → script sections)
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from app.ai.schemas import (
    AIState,
    ScriptSection,
    ScriptModel,
    ScriptOutput,
)
from app.ai.nodes.script_nodes import (
    analyze_storyboard_context,
    generate_script,
    validate_script_result,
)
from app.ai.graphs.script_graph import build_script_graph


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

def _make_scene(order: int = 1) -> dict:
    return {
        "id": f"scene-{order}",
        "order": order,
        "title": f"Scene {order}: Hook",
        "purpose": "Grab attention",
        "narration": "Two developers. Same task.",
        "visualDirection": "Split screen",
        "onScreenText": "Same task. Different tools.",
        "transition": "Hard cut",
        "estimatedDuration": "8 seconds",
    }


def _make_storyboard(n_scenes: int = 2) -> dict:
    return {
        "id": "sb-1",
        "projectId": "proj-1",
        "title": "AI Coding Assistants",
        "objective": "Educate developers",
        "status": "Approved",
        "scenes": [_make_scene(i + 1) for i in range(n_scenes)],
    }


def _make_state(**overrides) -> AIState:
    defaults: AIState = {
        "input_text": "AI coding assistant adoption for developers",
        "selected_opportunity": {
            "id": "opp-1",
            "title": "Educational Deep Dive",
            "summary": "A comprehensive look at AI coding tools",
        },
        "selected_platforms": [
            {"id": "plat-1", "platform": "LinkedIn", "recommendedFormat": "Short-form video"}
        ],
        "selected_angle": {
            "id": "angle-1",
            "title": "From Author to Architect",
            "hook": "Two developers. Same task.",
            "corePromise": "AI makes you faster",
        },
        "approved_strategy": {
            "id": "strat-1",
            "objective": "Educate developers on AI coding assistant adoption",
            "targetAudience": "Software engineers aged 25–45",
            "coreMessage": "AI coding tools make you faster and better",
            "tone": "Authoritative, accessible",
            "hookStrategy": "Open with relatable contrast",
            "callToAction": "Follow for weekly deep dives",
            "contentStructure": "Hook → Evidence → Solution → CTA",
            "keyTalkingPoints": ["Faster delivery", "New skill stack", "Real tools"],
            "platformAdaptations": [
                {"platform": "LinkedIn", "format": "Short-form video", "notes": "Professional tone"}
            ],
        },
        "approved_storyboard": _make_storyboard(2),
        "intent": None,
        "keywords": None,
        "structured_output": None,
        "error": None,
        "retries": 0,
    }
    defaults.update(overrides)
    return defaults


def _make_demo_script_output() -> ScriptOutput:
    return ScriptOutput(
        script=ScriptModel(
            id="demo-script-1",
            projectId="demo-proj",
            title="LinkedIn: AI Coding Assistants",
            platform="LinkedIn",
            format="Short-form video",
            hook="Two developers. Same task.",
            conclusion="The developers who thrive won't be those who avoided AI.",
            callToAction="Follow for weekly deep dives.",
            estimatedDuration="68 seconds",
            status="Draft",
            sections=[
                ScriptSection(
                    id="sec-1",
                    order=1,
                    title="Hook",
                    narration="Two developers. Same task. Same deadline.",
                    visualNotes="Split screen",
                    onScreenText="Same task. Different tools.",
                    estimatedDuration="8 seconds",
                ),
                ScriptSection(
                    id="sec-2",
                    order=2,
                    title="The Shift",
                    narration="AI coding assistants aren't replacing developers.",
                    visualNotes="Role pyramid animation",
                    onScreenText="From author → to architect",
                    estimatedDuration="10 seconds",
                ),
            ],
        )
    )


# ===========================================================================
# A. PYDANTIC MODEL TESTS
# ===========================================================================

class TestScriptSectionModel:
    def test_valid_section(self):
        section = ScriptSection(
            id="s-1",
            order=1,
            title="Hook",
            narration="Opening narration text.",
            visualNotes="Split screen setup",
            onScreenText="Same task. Different tools.",
            estimatedDuration="8 seconds",
        )
        assert section.id == "s-1"
        assert section.order == 1
        assert section.title == "Hook"
        assert section.narration == "Opening narration text."
        assert section.visualNotes == "Split screen setup"
        assert section.onScreenText == "Same task. Different tools."
        assert section.estimatedDuration == "8 seconds"

    def test_missing_required_field_raises(self):
        import pydantic
        with pytest.raises(pydantic.ValidationError):
            ScriptSection(
                id="s-1",
                order=1,
                # title is missing
                narration="N",
                visualNotes="V",
                onScreenText="T",
                estimatedDuration="5s",
            )


class TestScriptModelValid:
    def test_valid_script_model(self):
        section = ScriptSection(
            id="s-1", order=1, title="Hook", narration="N",
            visualNotes="V", onScreenText="T", estimatedDuration="8s"
        )
        script = ScriptModel(
            id="script-1",
            projectId="proj-1",
            title="LinkedIn Script",
            platform="LinkedIn",
            format="Short-form video",
            hook="Opening hook",
            conclusion="Conclusion text",
            callToAction="Follow for more",
            estimatedDuration="68 seconds",
            status="Draft",
            sections=[section],
        )
        assert script.id == "script-1"
        assert script.status == "Draft"
        assert len(script.sections) == 1

    def test_empty_sections_is_valid(self):
        """Model itself allows empty sections; validation happens in nodes/API."""
        script = ScriptModel(
            id="s", projectId="p", title="T", platform="LP",
            format="Video", hook="H", conclusion="C",
            callToAction="CTA", estimatedDuration="60s",
            status="Draft", sections=[]
        )
        assert script.sections == []


class TestScriptOutputModel:
    def test_valid_output(self):
        out = _make_demo_script_output()
        assert out.script.id == "demo-script-1"
        assert out.script.platform == "LinkedIn"
        assert len(out.script.sections) == 2

    def test_section_fields_preserved(self):
        out = _make_demo_script_output()
        sec = out.script.sections[0]
        assert sec.narration == "Two developers. Same task. Same deadline."
        assert sec.visualNotes == "Split screen"


# ===========================================================================
# B. LANGGRAPH NODE UNIT TESTS
# ===========================================================================

class TestAnalyzeStoryboardContextNode:
    @pytest.mark.asyncio
    async def test_returns_intent_on_success(self):
        state = _make_state()

        with patch("app.ai.nodes.script_nodes.get_provider") as mock_get:
            mock_provider = AsyncMock()
            mock_provider.generate_text.return_value = "Expand each scene into full narration"
            mock_get.return_value = mock_provider

            result = await analyze_storyboard_context(state)

        assert "intent" in result
        assert "Expand each scene" in result["intent"]
        assert "error" not in result

    @pytest.mark.asyncio
    async def test_missing_input_text_returns_error(self):
        state = _make_state(input_text="")
        result = await analyze_storyboard_context(state)
        assert result.get("error") is not None
        assert "Missing required context" in result["error"]

    @pytest.mark.asyncio
    async def test_missing_storyboard_returns_error(self):
        state = _make_state(approved_storyboard=None)
        result = await analyze_storyboard_context(state)
        assert result.get("error") is not None

    @pytest.mark.asyncio
    async def test_empty_scenes_returns_error(self):
        state = _make_state(approved_storyboard={"scenes": [], "id": "sb-1"})
        result = await analyze_storyboard_context(state)
        assert result.get("error") is not None
        assert "no scenes" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_provider_exception_returns_error(self):
        state = _make_state()

        with patch("app.ai.nodes.script_nodes.get_provider") as mock_get:
            mock_provider = AsyncMock()
            mock_provider.generate_text.side_effect = RuntimeError("LLM timeout")
            mock_get.return_value = mock_provider

            result = await analyze_storyboard_context(state)

        assert result.get("error") is not None
        assert "Failed to analyze" in result["error"]


class TestGenerateScriptNode:
    @pytest.mark.asyncio
    async def test_success_returns_structured_output(self):
        state = _make_state(intent="Expand each scene with platform adaptation")

        expected = _make_demo_script_output()

        with patch("app.ai.nodes.script_nodes.get_provider") as mock_get:
            mock_provider = AsyncMock()
            mock_provider.generate_structured.return_value = expected
            mock_get.return_value = mock_provider

            result = await generate_script(state)

        assert "structured_output" in result
        assert result.get("error") is None
        assert "script" in result["structured_output"]

    @pytest.mark.asyncio
    async def test_increments_retries_on_failure(self):
        state = _make_state(retries=0, intent="Context")

        with patch("app.ai.nodes.script_nodes.get_provider") as mock_get:
            mock_provider = AsyncMock()
            mock_provider.generate_structured.side_effect = RuntimeError("Provider error")
            mock_get.return_value = mock_provider

            result = await generate_script(state)

        assert result.get("error") is not None
        assert result.get("retries") == 1

    @pytest.mark.asyncio
    async def test_skips_on_max_retries(self):
        state = _make_state(error="Previous error", retries=3, intent="Context")
        result = await generate_script(state)
        # Should return empty dict (abort)
        assert result == {}


class TestValidateScriptResultNode:
    @pytest.mark.asyncio
    async def test_passes_valid_output(self):
        out = _make_demo_script_output()
        state = _make_state(structured_output=out.model_dump(), error=None)
        result = await validate_script_result(state)
        assert result.get("error") is None

    @pytest.mark.asyncio
    async def test_fails_missing_script_key(self):
        state = _make_state(structured_output={"wrong_key": {}}, error=None)
        result = await validate_script_result(state)
        assert result.get("error") is not None
        assert "script" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_fails_empty_sections(self):
        state = _make_state(
            structured_output={"script": {"sections": []}},
            error=None
        )
        result = await validate_script_result(state)
        assert result.get("error") is not None
        assert "no sections" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_propagates_existing_error(self):
        state = _make_state(error="Previous error", structured_output=None)
        result = await validate_script_result(state)
        assert result.get("error") == "Previous error"


# ===========================================================================
# C. LANGGRAPH GRAPH INTEGRATION
# ===========================================================================

class TestScriptGraph:
    def test_graph_builds_without_error(self):
        graph = build_script_graph()
        assert graph is not None

    @pytest.mark.asyncio
    async def test_should_retry_routes_to_generate_on_error(self):
        from app.ai.graphs.script_graph import should_retry
        from langgraph.graph import END

        state_with_error = _make_state(error="Some error", retries=1)
        assert should_retry(state_with_error) == "generate_script"

    @pytest.mark.asyncio
    async def test_should_retry_routes_to_end_on_max_retries(self):
        from app.ai.graphs.script_graph import should_retry
        from langgraph.graph import END

        state_max = _make_state(error="Max retries", retries=3)
        assert should_retry(state_max) == END

    @pytest.mark.asyncio
    async def test_should_retry_routes_to_validate_on_success(self):
        from app.ai.graphs.script_graph import should_retry

        state_ok = _make_state(error=None)
        assert should_retry(state_ok) == "validate_script_result"

    @pytest.mark.asyncio
    async def test_integration_script_graph_demo_mode(self):
        """Full graph integration test using mocked DemoProvider."""
        graph = build_script_graph()
        expected = _make_demo_script_output()

        initial_state = _make_state()

        with patch("app.ai.nodes.script_nodes.get_provider") as mock_get:
            mock_provider = AsyncMock()
            mock_provider.generate_text.return_value = "Narrative context analyzed"
            mock_provider.generate_structured.return_value = expected
            mock_get.return_value = mock_provider

            final_state = await graph.ainvoke(initial_state)

        assert final_state.get("error") is None
        assert "script" in final_state.get("structured_output", {})
        assert final_state["structured_output"]["script"]["id"] == "demo-script-1"


# ===========================================================================
# D. PROVIDER ROUTING TESTS
# ===========================================================================

class TestDemoProviderScriptRouting:
    def test_demo_provider_routes_correctly(self):
        """DemoProvider returns ScriptOutput when asked for ScriptOutput schema."""
        import asyncio
        from app.ai.providers.demo_provider import DemoProvider
        from app.ai.schemas import ScriptOutput
        from app.ai.config import AIConfig

        provider = DemoProvider()

        result = asyncio.get_event_loop().run_until_complete(
            provider.generate_structured("Generate a script", ScriptOutput)
        )

        assert isinstance(result, ScriptOutput)
        assert result.script.id is not None
        assert result.script.platform is not None
        assert len(result.script.sections) > 0

    def test_demo_provider_script_has_required_fields(self):
        """Verify demo ScriptOutput has all required fields."""
        import asyncio
        from app.ai.providers.demo_provider import DemoProvider
        from app.ai.schemas import ScriptOutput
        from app.ai.config import AIConfig

    def test_demo_provider_script_has_required_fields(self):
        """Verify demo ScriptOutput has all required fields."""
        import asyncio
        from app.ai.providers.demo_provider import DemoProvider
        from app.ai.schemas import ScriptOutput

        provider = DemoProvider()

        result = asyncio.get_event_loop().run_until_complete(
            provider.generate_structured("prompt", ScriptOutput)
        )

        script = result.script
        assert script.hook != ""
        assert script.conclusion != ""
        assert script.callToAction != ""
        assert script.estimatedDuration != ""
        assert script.status == "Draft"

    def test_demo_script_sections_have_all_fields(self):
        """Each section in the demo script must have all required fields."""
        import asyncio
        from app.ai.providers.demo_provider import DemoProvider
        from app.ai.schemas import ScriptOutput

        provider = DemoProvider()

        result = asyncio.get_event_loop().run_until_complete(
            provider.generate_structured("prompt", ScriptOutput)
        )

        for section in result.script.sections:
            assert section.id != ""
            assert section.order > 0
            assert section.title != ""
            assert section.narration != ""
            assert section.visualNotes != ""
            assert section.onScreenText != ""
            assert section.estimatedDuration != ""


class TestOpenAIProviderScriptRouting:
    def test_openai_provider_requires_api_key_for_script(self):
        """OpenAIProvider raises ValueError when no API key provided."""
        from app.ai.providers.factory import AIProviderFactory
        from app.ai.config import AIConfig

        config = AIConfig(provider="openai", api_key=None, model_name="gpt-4o-mini", temperature=0.7)
        with pytest.raises(ValueError, match="OPENAI_API_KEY"):
            AIProviderFactory.get_provider(config)


# ===========================================================================
# E. CONTEXT PROPAGATION TESTS
# ===========================================================================

class TestContextPropagationToGenerateScriptNode:
    @pytest.mark.asyncio
    async def test_storyboard_scenes_appear_in_prompt(self):
        """Verify that scene details from the approved storyboard appear in the generation prompt."""
        storyboard = _make_storyboard(2)
        state = _make_state(
            intent="Narrative context analyzed",
            approved_storyboard=storyboard,
        )
        captured_prompt = []

        async def mock_generate_structured(prompt, schema):
            captured_prompt.append(prompt)
            return _make_demo_script_output()

        with patch("app.ai.nodes.script_nodes.get_provider") as mock_get:
            mock_provider = AsyncMock()
            mock_provider.generate_structured.side_effect = mock_generate_structured
            mock_get.return_value = mock_provider

            await generate_script(state)

        assert len(captured_prompt) == 1
        prompt_text = captured_prompt[0]

        # Verify storyboard scene content appears in the prompt
        assert "Scene 1" in prompt_text or "scene-1" in prompt_text
        assert "Two developers. Same task." in prompt_text  # scene narration
        assert "Split screen" in prompt_text  # visual direction
        # Verify platform info appears
        assert "LinkedIn" in prompt_text
        # Verify strategy context appears
        assert "Authoritative" in prompt_text or "accessible" in prompt_text  # tone

    @pytest.mark.asyncio
    async def test_strategy_cta_appears_in_prompt(self):
        """Verify that the strategy's call-to-action appears in the generation prompt."""
        state = _make_state(intent="Analyzed")
        captured = []

        async def capture_prompt(prompt, schema):
            captured.append(prompt)
            return _make_demo_script_output()

        with patch("app.ai.nodes.script_nodes.get_provider") as mock_get:
            mock_provider = AsyncMock()
            mock_provider.generate_structured.side_effect = capture_prompt
            mock_get.return_value = mock_provider

            await generate_script(state)

        assert "Follow for weekly deep dives" in captured[0]  # CTA from approved_strategy

    @pytest.mark.asyncio
    async def test_angle_hook_appears_in_prompt(self):
        """Verify the selected angle's hook is included in the generation prompt."""
        state = _make_state(intent="Analyzed")
        captured = []

        async def capture_prompt(prompt, schema):
            captured.append(prompt)
            return _make_demo_script_output()

        with patch("app.ai.nodes.script_nodes.get_provider") as mock_get:
            mock_provider = AsyncMock()
            mock_provider.generate_structured.side_effect = capture_prompt
            mock_get.return_value = mock_provider

            await generate_script(state)

        assert "Two developers. Same task." in captured[0]  # angle hook
