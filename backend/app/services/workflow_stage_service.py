from typing import List
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.workflow_stage_repo import WorkflowStageRepository
from app.services.project_service import ProjectService
from app.schemas.workflow_stage import WorkflowStageCreate, WorkflowStageUpdate
from app.schemas.project import ProjectUpdate
from app.models.workflow_stage import WorkflowStage

class WorkflowStageService:
    def __init__(self, session: AsyncSession, user_id: int):
        self.repo = WorkflowStageRepository(session)
        self.project_service = ProjectService(session, user_id)
        self.session = session

    async def create_or_update_stage(self, project_id: UUID, stage_type: str, stage_in: WorkflowStageUpdate) -> WorkflowStage:
        # Verify project exists
        project = await self.project_service.get_project(project_id)

        existing_stage = await self.repo.get_by_project_and_type(project_id, stage_type)

        if existing_stage:
            updated_stage = await self.repo.update(existing_stage, stage_in)
        else:
            create_schema = WorkflowStageCreate(
                stage_type=stage_type,
                status=stage_in.status or "Locked",
                data=stage_in.data
            )
            updated_stage = await self.repo.create(project_id, create_schema)

        # Sync project current_stage if status is in progress
        if stage_in.status == 'In Progress' and project.current_stage != stage_type:
            await self.project_service.update_project(project_id, ProjectUpdate(current_stage=stage_type))

        return updated_stage

    async def get_stages(self, project_id: UUID) -> List[WorkflowStage]:
        # Verify project exists
        await self.project_service.get_project(project_id)
        return await self.repo.get_all_by_project(project_id)

    async def get_stage(self, project_id: UUID, stage_type: str) -> WorkflowStage:
        await self.project_service.get_project(project_id)
        stage = await self.repo.get_by_project_and_type(project_id, stage_type)
        if not stage:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow stage not found")
        return stage
