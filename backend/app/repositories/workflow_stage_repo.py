from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.workflow_stage import WorkflowStage
from app.schemas.workflow_stage import WorkflowStageCreate, WorkflowStageUpdate

class WorkflowStageRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, project_id: UUID, stage_in: WorkflowStageCreate) -> WorkflowStage:
        kwargs = stage_in.model_dump()
        kwargs["project_id"] = project_id
        db_obj = WorkflowStage(**kwargs)
        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj

    async def get_by_project_and_type(self, project_id: UUID, stage_type: str) -> Optional[WorkflowStage]:
        result = await self.session.execute(
            select(WorkflowStage)
            .where(WorkflowStage.project_id == project_id)
            .where(WorkflowStage.stage_type == stage_type)
        )
        return result.scalars().first()

    async def get_all_by_project(self, project_id: UUID) -> List[WorkflowStage]:
        result = await self.session.execute(
            select(WorkflowStage)
            .where(WorkflowStage.project_id == project_id)
            .order_by(WorkflowStage.created_at.asc())
        )
        return list(result.scalars().all())

    async def update(self, db_obj: WorkflowStage, obj_in: WorkflowStageUpdate) -> WorkflowStage:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
            
        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj
