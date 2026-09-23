import uuid
from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc

from app.db.session import get_db
from app.models.schedule import Schedule
from app.models.project import Project
from app.models.workflow_stage import WorkflowStage
from app.schemas.schedule import ScheduleCreate, ScheduleUpdate, ScheduleResponse, ScheduleWithProjectResponse
from app.api.deps import get_current_user
from app.models.user import User
from app.services.project_service import ProjectService

router = APIRouter()

@router.post("", response_model=ScheduleResponse)
async def create_schedule(schedule_in: ScheduleCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Verify project exists and belongs to user
    project_service = ProjectService(db, current_user.id)
    project = await project_service.get_project(schedule_in.project_id)

    # Verify project has approved content (at least Script stage)
    stmt = select(WorkflowStage).where(
        WorkflowStage.project_id == schedule_in.project_id,
        WorkflowStage.stage_type.in_(["script", "final-script"]),
        WorkflowStage.status.in_(["completed", "Completed"])
    )
    result = await db.execute(stmt)
    script_stage = result.scalar_one_or_none()

    if not script_stage:
        raise HTTPException(
            status_code=400, 
            detail="Cannot schedule project: No completed script found. Human approval of script is required."
        )

    db_schedule = Schedule(
        project_id=schedule_in.project_id,
        platform=schedule_in.platform,
        scheduled_at=schedule_in.scheduled_at,
        status=schedule_in.status or "Scheduled"
    )
    db.add(db_schedule)
    await db.commit()
    await db.refresh(db_schedule)
    return db_schedule

@router.get("", response_model=List[ScheduleWithProjectResponse])
async def list_schedules(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    stmt = select(Schedule, Project.title.label("project_title")).join(Project, Schedule.project_id == Project.id).where(Project.user_id == current_user.id).order_by(Schedule.scheduled_at.asc())
    result = await db.execute(stmt)
    
    schedules = []
    for sched, proj_title in result.all():
        sched_dict = sched.__dict__.copy()
        sched_dict["project_title"] = proj_title
        schedules.append(sched_dict)
        
    return schedules

async def get_schedule_with_ownership_check(schedule_id: uuid.UUID, db: AsyncSession, current_user: User) -> Schedule:
    stmt = select(Schedule).join(Project).where(Schedule.id == schedule_id, Project.user_id == current_user.id)
    result = await db.execute(stmt)
    schedule = result.scalar_one_or_none()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return schedule

@router.get("/{schedule_id}", response_model=ScheduleResponse)
async def get_schedule(schedule_id: uuid.UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await get_schedule_with_ownership_check(schedule_id, db, current_user)

@router.put("/{schedule_id}", response_model=ScheduleResponse)
async def update_schedule(schedule_id: uuid.UUID, schedule_in: ScheduleUpdate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_schedule = await get_schedule_with_ownership_check(schedule_id, db, current_user)

    update_data = schedule_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_schedule, field, value)

    await db.commit()
    await db.refresh(db_schedule)
    return db_schedule

@router.delete("/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_schedule(schedule_id: uuid.UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_schedule = await get_schedule_with_ownership_check(schedule_id, db, current_user)

    await db.delete(db_schedule)
    await db.commit()
