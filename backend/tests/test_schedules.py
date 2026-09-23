import uuid
import pytest
from datetime import datetime, timezone, timedelta
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.project import Project
from app.models.workflow_stage import WorkflowStage
from app.models.schedule import Schedule

pytestmark = pytest.mark.asyncio

async def test_schedule_crud_flow(authenticated_client: AsyncClient, db_session: AsyncSession, test_user):
    # 1. Create a project
    proj_id = uuid.uuid4()
    proj = Project(id=proj_id, title="Schedule Test Project", source_type="text", source_reference="N/A", user_id=test_user.id)
    db_session.add(proj)
    await db_session.flush()

    # Create content (Script Stage) to allow scheduling
    script_stage = WorkflowStage(
        id=uuid.uuid4(),
        project_id=proj_id,
        stage_type="script",
        status="completed",
        data={"script": "Test script"}
    )
    db_session.add(script_stage)
    await db_session.commit()

    # 2. Create schedule
    future_date = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()
    create_data = {
        "project_id": str(proj_id),
        "platform": "LinkedIn",
        "scheduled_at": future_date,
        "status": "Scheduled"
    }
    
    res = await authenticated_client.post("/api/schedules", json=create_data)
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["platform"] == "LinkedIn"
    assert data["status"] == "Scheduled"
    schedule_id = data["id"]

    # 3. Retrieve schedule list
    res = await authenticated_client.get("/api/schedules")
    assert res.status_code == 200
    schedules = res.json()
    assert len(schedules) >= 1
    assert any(s['id'] == schedule_id and s['project_title'] == "Schedule Test Project" for s in schedules)

    # 4. Update schedule
    new_future_date = (datetime.now(timezone.utc) + timedelta(days=3)).isoformat()
    update_data = {
        "platform": "Twitter",
        "scheduled_at": new_future_date
    }
    res = await authenticated_client.put(f"/api/schedules/{schedule_id}", json=update_data)
    assert res.status_code == 200
    updated_data = res.json()
    assert updated_data["platform"] == "Twitter"
    assert updated_data["scheduled_at"] != data["scheduled_at"]

    # 5. Delete schedule
    res = await authenticated_client.delete(f"/api/schedules/{schedule_id}")
    assert res.status_code == 204

    # Confirm deletion
    res = await authenticated_client.get(f"/api/schedules/{schedule_id}")
    assert res.status_code == 404

async def test_cannot_schedule_project_without_script(authenticated_client: AsyncClient, db_session: AsyncSession, test_user):
    # 1. Create a project without a completed script stage
    proj_id = uuid.uuid4()
    proj = Project(id=proj_id, title="Empty Project", source_type="text", source_reference="N/A", user_id=test_user.id)
    db_session.add(proj)
    await db_session.commit()

    # 2. Try to create schedule
    future_date = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()
    create_data = {
        "project_id": str(proj_id),
        "platform": "Blog",
        "scheduled_at": future_date
    }
    
    res = await authenticated_client.post("/api/schedules", json=create_data)
    assert res.status_code == 400
    assert "No completed script found" in res.json()["detail"]
