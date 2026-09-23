from fastapi import APIRouter, Depends, status
from typing import List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.workflow_stage import WorkflowStageUpdate, WorkflowStageResponse
from app.services.workflow_stage_service import WorkflowStageService
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter()

@router.get("/{project_id}/stages", response_model=List[WorkflowStageResponse])
async def read_project_stages(project_id: UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    service = WorkflowStageService(db, current_user.id)
    return await service.get_stages(project_id)

@router.get("/{project_id}/stages/{stage_type}", response_model=WorkflowStageResponse)
async def read_project_stage(project_id: UUID, stage_type: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    service = WorkflowStageService(db, current_user.id)
    return await service.get_stage(project_id, stage_type)

@router.put("/{project_id}/stages/{stage_type}", response_model=WorkflowStageResponse)
@router.patch("/{project_id}/stages/{stage_type}", response_model=WorkflowStageResponse)
async def update_project_stage(project_id: UUID, stage_type: str, stage_in: WorkflowStageUpdate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    service = WorkflowStageService(db, current_user.id)
    return await service.create_or_update_stage(project_id, stage_type, stage_in)
