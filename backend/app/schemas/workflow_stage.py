from pydantic import BaseModel, ConfigDict
from typing import Optional, Any
from datetime import datetime
from uuid import UUID

class WorkflowStageBase(BaseModel):
    stage_type: str
    status: str

class WorkflowStageCreate(WorkflowStageBase):
    data: Optional[Any] = None

class WorkflowStageUpdate(BaseModel):
    status: Optional[str] = None
    data: Optional[Any] = None

class WorkflowStageResponse(WorkflowStageBase):
    id: UUID
    project_id: UUID
    data: Optional[Any] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
