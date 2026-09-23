from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from app.schemas.workflow_stage import WorkflowStageResponse

class ProjectBase(BaseModel):
    title: str
    description: Optional[str] = None
    source_type: str
    source_reference: str

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    source_type: Optional[str] = None
    source_reference: Optional[str] = None
    current_stage: Optional[str] = None

class ProjectResponse(ProjectBase):
    id: UUID
    status: str
    current_stage: str
    created_at: datetime
    updated_at: datetime
    stages: List[WorkflowStageResponse] = []

    model_config = ConfigDict(from_attributes=True)
