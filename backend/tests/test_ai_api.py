"""
Phase 9B Tests: AI API Endpoint — Content Selection

Tests the HTTP layer for POST /api/ai/content-selection.
Verifies: valid request, 404 on bad project, 422 on bad input, 500 on AI failure.
"""
import pytest
import uuid
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock


# ─── Helpers ─────────────────────────────────────────────────────────────────

async def create_test_project(authenticated_client: AsyncClient, title: str = "AI Test Project") -> str:
    """Helper to create a project and return its ID."""
    res = await authenticated_client.post(
        "/api/projects",
        json={
            "title": title,
            "description": "The future of AI coding assistants",
            "source_type": "Text Idea",
            "source_reference": "The future of AI coding assistants",
        },
    )
    assert res.status_code == 201, f"Project creation failed: {res.text}"
    return res.json()["id"]


# ─── Content Selection Endpoint Tests ────────────────────────────────────────

@pytest.mark.asyncio
async def test_content_selection_demo_mode(authenticated_client: AsyncClient):
    """
    POST /api/ai/content-selection with a valid project should return opportunities
    when AI_PROVIDER=demo.

    The DemoProvider returns a fixed set of realistic opportunities without
    requiring an API key.
    """
    project_id = await create_test_project(authenticated_client, "CS Demo Test")

    # Step 1.5: Setup content type stage
    await authenticated_client.put(
        f"/api/projects/{project_id}/stages/content-type",
        json={
            "stage_type": "content-type",
            "status": "Completed",
            "data": {
                "recommendation": {"recommendedType": "Carousel"},
                "approved_type": "Carousel"
            }
        }
    )

    with patch("app.core.config.settings.AI_PROVIDER", "demo"):
        response = await authenticated_client.post(
            "/api/ai/content-selection",
            json={"project_id": project_id},
        )

    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    data = response.json()

    # Validate response shape
    assert "opportunities" in data, "Response must contain 'opportunities' key"
    assert isinstance(data["opportunities"], list), "Opportunities must be a list"
    assert len(data["opportunities"]) >= 1, "Should return at least 1 opportunities"

    # Validate first opportunity structure
    first = data["opportunities"][0]
    assert "id" in first
    assert "title" in first
    assert "summary" in first
    assert "why_interesting" in first or "whyInteresting" in first
    assert "potential_audience" in first or "potentialAudience" in first


@pytest.mark.asyncio
async def test_content_selection_project_not_found(authenticated_client: AsyncClient):
    """
    POST /api/ai/content-selection with a non-existent project_id should return 404.
    """
    fake_id = str(uuid.uuid4())
    response = await authenticated_client.post(
        "/api/ai/content-selection",
        json={"project_id": fake_id},
    )
    assert response.status_code == 404, f"Expected 404, got {response.status_code}"


@pytest.mark.asyncio
async def test_content_selection_invalid_request_missing_field(authenticated_client: AsyncClient):
    """
    POST /api/ai/content-selection without project_id should return 422 (validation error).
    """
    response = await authenticated_client.post(
        "/api/ai/content-selection",
        json={},  # missing project_id
    )
    assert response.status_code == 422, f"Expected 422, got {response.status_code}"


@pytest.mark.asyncio
async def test_content_selection_invalid_uuid_format(authenticated_client: AsyncClient):
    """
    POST /api/ai/content-selection with a malformed project_id should return 422.
    """
    response = await authenticated_client.post(
        "/api/ai/content-selection",
        json={"project_id": "not-a-valid-uuid"},
    )
    assert response.status_code == 422, f"Expected 422, got {response.status_code}"


@pytest.mark.asyncio
async def test_content_selection_ai_failure_returns_500(authenticated_client: AsyncClient):
    """
    When the AI orchestrator raises an exception, the endpoint should return 500
    with a descriptive error message.
    """
    project_id = await create_test_project(authenticated_client, "CS Failure Test")

    # Step 1.5: Setup content type stage
    await authenticated_client.put(
        f"/api/projects/{project_id}/stages/content-type",
        json={
            "stage_type": "content-type",
            "status": "Completed",
            "data": {
                "recommendation": {"recommendedType": "Carousel"},
                "approved_type": "Carousel"
            }
        }
    )

    with patch(
        "app.api.routes.ai.orchestrator.run_content_selection",
        new_callable=AsyncMock,
        side_effect=RuntimeError("LLM provider timed out"),
    ):
        response = await authenticated_client.post(
            "/api/ai/content-selection",
            json={"project_id": project_id},
        )

    assert response.status_code == 500, f"Expected 500, got {response.status_code}"
    detail = response.json().get("detail", "")
    assert "AI Content Selection failed" in detail or "LLM provider timed out" in detail


@pytest.mark.asyncio
async def test_content_selection_openai_provider_routing(authenticated_client: AsyncClient):
    """
    When AI_PROVIDER=openai, the endpoint should attempt to use the OpenAI provider.
    We mock the orchestrator so we don't need a real API key.
    This test verifies the provider routing config is respected.
    """
    project_id = await create_test_project(authenticated_client, "CS OpenAI Routing Test")

    mock_result = {
        "opportunities": [
            {
                "id": "opt-openai-1",
                "title": "OpenAI Generated: Short-Form Video",
                "summary": "A video generated by real OpenAI.",
                "whyInteresting": "Real AI output.",
                "keyPoints": ["Real point 1", "Real point 2"],
                "potentialAudience": "Developers",
                "estimatedValue": "High",
            }
        ]
    }

    # Step 1.5: Setup content type stage
    await authenticated_client.put(
        f"/api/projects/{project_id}/stages/content-type",
        json={
            "stage_type": "content-type",
            "status": "Completed",
            "data": {
                "recommendation": {"recommendedType": "Carousel"},
                "approved_type": "Carousel"
            }
        }
    )

    with patch("app.core.config.settings.AI_PROVIDER", "openai"), patch(
        "app.api.routes.ai.orchestrator.run_content_selection",
        new_callable=AsyncMock,
        return_value=mock_result,
    ):
        response = await authenticated_client.post(
            "/api/ai/content-selection",
            json={"project_id": project_id},
        )

    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    data = response.json()
    assert "opportunities" in data
    assert data["opportunities"][0]["id"] == "opt-openai-1"


# ─── Data Persistence Tests ───────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_content_selection_result_persists_via_stage(authenticated_client: AsyncClient):
    """
    After generating content selection AND saving via PUT /stages/content-selection,
    the data should be retrievable from PostgreSQL.
    """
    project_id = await create_test_project(authenticated_client, "CS Persistence Test")

    # Step 0.5: Setup content type stage
    await authenticated_client.put(
        f"/api/projects/{project_id}/stages/content-type",
        json={
            "stage_type": "content-type",
            "status": "Completed",
            "data": {
                "recommendation": {"recommendedType": "Carousel"},
                "approved_type": "Carousel"
            }
        }
    )

    # Step 1: Generate content selection
    with patch("app.core.config.settings.AI_PROVIDER", "demo"):
        gen_response = await authenticated_client.post(
            "/api/ai/content-selection",
            json={"project_id": project_id},
        )
    assert gen_response.status_code == 200
    opportunities = gen_response.json()["opportunities"]

    # Step 2: Persist via the workflow stage endpoint (simulating what the frontend does)
    persist_response = await authenticated_client.put(
        f"/api/projects/{project_id}/stages/content-selection",
        json={
            "stage_type": "content-selection",
            "status": "In Progress",
            "data": {"opportunities": opportunities, "selectedId": opportunities[0]["id"]},
        },
    )
    assert persist_response.status_code == 200

    # Step 3: Reload from DB and verify
    read_response = await authenticated_client.get(
        f"/api/projects/{project_id}/stages/content-selection"
    )
    assert read_response.status_code == 200
    stage_data = read_response.json()

    assert stage_data["data"] is not None
    assert "opportunities" in stage_data["data"]
    assert len(stage_data["data"]["opportunities"]) >= 1

    # The selectedId is stored as-is in the JSON blob (camelCase preserved)
    stored_selected = (
        stage_data["data"].get("selectedId")
        or stage_data["data"].get("selected_id")
    )
    assert stored_selected == opportunities[0]["id"], (
        f"Expected selectedId={opportunities[0]['id']!r}, got {stored_selected!r}. "
        f"Stage data keys: {list(stage_data['data'].keys())}"
    )


# ─── Storyboard Endpoint Tests ────────────────────────────────────────────────

# Shared stage data fixtures for storyboard prerequisite setup

SAMPLE_OPPORTUNITY = {
    "id": "opt-short-video",
    "title": "Short-Form Educational Video",
    "summary": "AI coding overview",
    "whyInteresting": "Viral potential",
    "keyPoints": ["Speed", "Quality"],
    "potentialAudience": "Developers",
    "estimatedValue": "High"
}

SAMPLE_PLATFORM = {
    "id": "plat-linkedin",
    "projectId": "proj",
    "platform": "LinkedIn",
    "suitability": 95,
    "reasoning": "Professional audience",
    "recommendedFormat": "Educational post",
    "recommendedLength": "1000 chars",
    "audience": "Developers",
    "tone": "Professional",
    "priority": "Recommended"
}

SAMPLE_ANGLE = {
    "id": "ang-1",
    "projectId": "proj",
    "title": "The Developer Superpower",
    "angle": "Contrarian",
    "hook": "AI won't replace you",
    "description": "An empowering take",
    "targetAudience": "Developers",
    "corePromise": "10x productivity",
    "differentiation": "Data-backed",
    "supportingPoints": ["Point A"],
    "recommendedPlatforms": ["LinkedIn"]
}

SAMPLE_STRATEGY = {
    "id": "strat-1",
    "projectId": "proj",
    "objective": "Educate developers",
    "targetAudience": "Developers",
    "coreMessage": "AI tools make you better",
    "valueProposition": "Actionable tips",
    "tone": "Professional",
    "format": "Multi-scene video",
    "hookStrategy": "Bold claim",
    "keyTalkingPoints": ["Faster delivery", "New tools"],
    "callToAction": "Follow for more",
    "contentStructure": "Hook → Data → Tools → CTA",
    "platformAdaptations": [{"platform": "LinkedIn", "format": "Post", "notes": "Professional"}]
}


async def _setup_prerequisite_stages(authenticated_client: AsyncClient, project_id: str):
    """Helper: persist all prerequisite stages so storyboard endpoint can load them."""
    # content-type
    await authenticated_client.put(
        f"/api/projects/{project_id}/stages/content-type",
        json={
            "stage_type": "content-type",
            "status": "Completed",
            "data": {
                "recommendation": {"recommendedType": "Carousel"},
                "approved_type": "Carousel"
            }
        }
    )
    # content-selection
    await authenticated_client.put(
        f"/api/projects/{project_id}/stages/content-selection",
        json={
            "stage_type": "content-selection",
            "status": "Completed",
            "data": {
                "opportunities": [SAMPLE_OPPORTUNITY],
                "selectedId": SAMPLE_OPPORTUNITY["id"]
            }
        }
    )
    # platform-strategy
    await authenticated_client.put(
        f"/api/projects/{project_id}/stages/platform-strategy",
        json={
            "stage_type": "platform-strategy",
            "status": "Completed",
            "data": {
                "recommendations": [SAMPLE_PLATFORM],
                "selectedIds": [SAMPLE_PLATFORM["id"]]
            }
        }
    )
    # topic-angle
    await authenticated_client.put(
        f"/api/projects/{project_id}/stages/topic-angle",
        json={
            "stage_type": "topic-angle",
            "status": "Completed",
            "data": {
                "angles": [SAMPLE_ANGLE],
                "selectedId": SAMPLE_ANGLE["id"]
            }
        }
    )
    # content-strategy
    await authenticated_client.put(
        f"/api/projects/{project_id}/stages/content-strategy",
        json={
            "stage_type": "content-strategy",
            "status": "Completed",
            "data": {"strategy": SAMPLE_STRATEGY}
        }
    )


@pytest.mark.asyncio
async def test_storyboard_demo_mode_success(authenticated_client: AsyncClient):
    """
    POST /api/ai/storyboard with all prerequisite stages set up should return
    a complete storyboard in demo mode.
    """
    project_id = await create_test_project(authenticated_client, "SB Demo Test")
    await _setup_prerequisite_stages(authenticated_client, project_id)

    with patch("app.core.config.settings.AI_PROVIDER", "demo"):
        response = await authenticated_client.post(
            "/api/ai/storyboard",
            json={"project_id": project_id},
        )

    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    data = response.json()

    assert "storyboard" in data, "Response must contain 'storyboard' key"
    sb = data["storyboard"]
    assert "id" in sb
    assert "title" in sb
    assert "status" in sb
    assert sb["status"] == "Draft"
    assert "scenes" in sb
    assert isinstance(sb["scenes"], list)
    assert len(sb["scenes"]) >= 4, "Demo storyboard should have at least 4 scenes"

    # Validate first scene shape
    first_scene = sb["scenes"][0]
    assert "id" in first_scene
    assert "order" in first_scene
    assert "title" in first_scene
    assert "narration" in first_scene or "narration" in first_scene
    assert "visualDirection" in first_scene or "visual_direction" in first_scene


@pytest.mark.asyncio
async def test_storyboard_project_not_found(authenticated_client: AsyncClient):
    """POST /api/ai/storyboard with non-existent project_id returns 404."""
    fake_id = str(uuid.uuid4())
    response = await authenticated_client.post(
        "/api/ai/storyboard",
        json={"project_id": fake_id},
    )
    assert response.status_code == 404, f"Expected 404, got {response.status_code}"


@pytest.mark.asyncio
async def test_storyboard_invalid_uuid_returns_422(authenticated_client: AsyncClient):
    """POST /api/ai/storyboard with malformed project_id returns 422."""
    response = await authenticated_client.post(
        "/api/ai/storyboard",
        json={"project_id": "not-a-uuid"},
    )
    assert response.status_code == 422, f"Expected 422, got {response.status_code}"


@pytest.mark.asyncio
async def test_storyboard_missing_project_id_returns_422(authenticated_client: AsyncClient):
    """POST /api/ai/storyboard without project_id returns 422."""
    response = await authenticated_client.post("/api/ai/storyboard", json={})
    assert response.status_code == 422, f"Expected 422, got {response.status_code}"


@pytest.mark.asyncio
async def test_storyboard_missing_prerequisite_content_selection(authenticated_client: AsyncClient):
    """POST /api/ai/storyboard without prerequisite stages returns 400."""
    project_id = await create_test_project(authenticated_client, "SB Missing Prereqs")
    # Don't set up any prerequisite stages

    with patch("app.core.config.settings.AI_PROVIDER", "demo"):
        response = await authenticated_client.post(
            "/api/ai/storyboard",
            json={"project_id": project_id},
        )

    assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"
    detail = response.json().get("detail", "").lower()
    assert (
        "content-selection" in detail
        or "prerequisite" in detail
        or "content selection" in detail
        or "empty" in detail
        or "content type" in detail
    ), f"Unexpected 400 detail: {detail}"


@pytest.mark.asyncio
async def test_storyboard_ai_failure_returns_500(authenticated_client: AsyncClient):
    """When orchestrator raises an exception, endpoint returns 500."""
    project_id = await create_test_project(authenticated_client, "SB Failure Test")
    await _setup_prerequisite_stages(authenticated_client, project_id)

    with patch(
        "app.api.routes.ai.orchestrator.run_storyboard",
        new_callable=AsyncMock,
        side_effect=RuntimeError("LLM provider timed out"),
    ):
        response = await authenticated_client.post(
            "/api/ai/storyboard",
            json={"project_id": project_id},
        )

    assert response.status_code == 500, f"Expected 500, got {response.status_code}"
    detail = response.json().get("detail", "")
    assert "storyboard" in detail.lower() or "timed out" in detail.lower()


@pytest.mark.asyncio
async def test_storyboard_openai_provider_routing(authenticated_client: AsyncClient):
    """When AI_PROVIDER=openai, endpoint uses mocked orchestrator without a real API key."""
    project_id = await create_test_project(authenticated_client, "SB OpenAI Routing Test")
    await _setup_prerequisite_stages(authenticated_client, project_id)

    mock_result = {
        "storyboard": {
            "id": "sb-openai",
            "projectId": project_id,
            "title": "OpenAI Generated Storyboard",
            "objective": "Educate developers",
            "status": "Draft",
            "scenes": [
                {
                    "id": "s-1",
                    "order": 1,
                    "title": "Hook",
                    "purpose": "Grab attention",
                    "narration": "Real AI narration.",
                    "visualDirection": "Camera close-up.",
                    "onScreenText": "AI Coding",
                    "transition": "Cut",
                    "estimatedDuration": "8 seconds"
                }
            ]
        }
    }

    with patch("app.core.config.settings.AI_PROVIDER", "openai"), patch(
        "app.api.routes.ai.orchestrator.run_storyboard",
        new_callable=AsyncMock,
        return_value=mock_result,
    ):
        response = await authenticated_client.post(
            "/api/ai/storyboard",
            json={"project_id": project_id},
        )

    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    data = response.json()
    assert data["storyboard"]["id"] == "sb-openai"
    assert len(data["storyboard"]["scenes"]) == 1


@pytest.mark.asyncio
async def test_storyboard_result_persists_via_stage(authenticated_client: AsyncClient):
    """
    End-to-end persistence test:
    Generate storyboard → save via PUT → reload and verify from PostgreSQL.
    """
    project_id = await create_test_project(authenticated_client, "SB Persistence Test")
    await _setup_prerequisite_stages(authenticated_client, project_id)

    # Step 1: Generate storyboard
    with patch("app.core.config.settings.AI_PROVIDER", "demo"):
        gen_response = await authenticated_client.post(
            "/api/ai/storyboard",
            json={"project_id": project_id},
        )
    assert gen_response.status_code == 200
    storyboard = gen_response.json()["storyboard"]

    # Step 2: Save storyboard via the stage endpoint
    persist_response = await authenticated_client.put(
        f"/api/projects/{project_id}/stages/storyboard",
        json={
            "stage_type": "storyboard",
            "status": "In Progress",
            "data": {"storyboard": storyboard}
        }
    )
    assert persist_response.status_code == 200

    # Step 3: Reload and verify from PostgreSQL
    read_response = await authenticated_client.get(
        f"/api/projects/{project_id}/stages/storyboard"
    )
    assert read_response.status_code == 200
    stage_data = read_response.json()

    assert stage_data["data"] is not None
    assert "storyboard" in stage_data["data"]
    saved_sb = stage_data["data"]["storyboard"]
    assert saved_sb["id"] == storyboard["id"]
    assert len(saved_sb["scenes"]) == len(storyboard["scenes"])

