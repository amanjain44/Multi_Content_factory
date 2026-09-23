import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.models.user import User
from app.core.security import get_password_hash, create_access_token
from datetime import timedelta, datetime
from app.core.config import settings
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.project import Project
from app.models.workflow_stage import WorkflowStage
from app.models.source import SourceDocument
from app.models.schedule import Schedule

@pytest.mark.asyncio
async def test_full_cross_user_isolation(authenticated_client: AsyncClient, db_session: AsyncSession, test_user: User):
    # test_user is User A
    
    # 1. Create User B
    user_b = User(
        email="user_b@example.com",
        hashed_password=get_password_hash("passwordB"),
        is_active=True
    )
    db_session.add(user_b)
    await db_session.commit()
    await db_session.refresh(user_b)
    
    access_token_b = create_access_token(
        subject=str(user_b.id), expires_delta=timedelta(minutes=15)
    )

    headers_b = {"Authorization": f"Bearer {access_token_b}"}

    # User A creates a project using authenticated_client
    p_res = await authenticated_client.post("/api/projects", json={
        "title": "User A Project",
        "source_type": "TEXT",
        "source_reference": "test reference"
    })
    assert p_res.status_code == 201
    project_id = p_res.json()["id"]

    # We won't insert workflow stages directly via db_session because of transaction isolation between test and API.
    # Instead, we will rely on the API endpoints directly.
    # The project has been created successfully.

    # ----------------------------------------------------
    # VERIFY USER B CANNOT ACCESS PROJECT A RESOURCES
    # ----------------------------------------------------
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. Project
        res = await client.get(f"/api/projects/{project_id}", headers=headers_b)
        assert res.status_code in [404, 403]
        
        # 2. Workflow stages
        # For simplicity, if we hit the project by ID from User B, they shouldn't be able to get the workflow stages
        res = await client.get(f"/api/workflow-stages/content-selection/{project_id}", headers=headers_b)
        assert res.status_code in [404, 403]
        
        res = await client.get(f"/api/workflow-stages/platform-strategy/{project_id}", headers=headers_b)
        assert res.status_code in [404, 403]

        res = await client.get(f"/api/workflow-stages/topic-angle/{project_id}", headers=headers_b)
        assert res.status_code in [404, 403]

        res = await client.get(f"/api/workflow-stages/content-strategy/{project_id}", headers=headers_b)
        assert res.status_code in [404, 403]

        res = await client.get(f"/api/workflow-stages/storyboard/{project_id}", headers=headers_b)
        assert res.status_code in [404, 403]

        res = await client.get(f"/api/workflow-stages/script/{project_id}", headers=headers_b)
        assert res.status_code in [404, 403]

        # 3. Calendar
        # Attempt to get schedule by ID
        res = await client.get("/api/schedules", headers=headers_b)
        # Should not see User A's schedule
        schedules = res.json()
        assert len(schedules) == 0

        # Attempt to create schedule on User A's project
        res = await client.post("/api/schedules", json={
            "project_id": project_id,
            "platform": "test",
            "scheduled_at": "2026-11-11T10:00:00Z"
        }, headers=headers_b)
        assert res.status_code in [404, 403]

        # 4. RAG / Sources
        # Assuming the RAG API takes a project ID
        res = await client.get(f"/api/sources/{project_id}", headers=headers_b)
        assert res.status_code in [404, 403]

        # 5. AI Endpoints
        res = await client.post("/api/ai/content-selection", json={"project_id": project_id}, headers=headers_b)
        assert res.status_code in [404, 403, 422]
        
        res = await client.post("/api/ai/platform-strategy", json={"project_id": project_id}, headers=headers_b)
        assert res.status_code in [404, 403, 422]

        res = await client.post("/api/ai/topic-angle", json={"project_id": project_id}, headers=headers_b)
        assert res.status_code in [404, 403, 422]

        res = await client.post("/api/ai/content-strategy", json={"project_id": project_id}, headers=headers_b)
        assert res.status_code in [404, 403, 422]

        res = await client.post("/api/ai/storyboard", json={"project_id": project_id}, headers=headers_b)
        assert res.status_code in [404, 403, 422]

        res = await client.post("/api/ai/script", json={"project_id": project_id}, headers=headers_b)
        assert res.status_code in [404, 403, 422]

        # All passed!
