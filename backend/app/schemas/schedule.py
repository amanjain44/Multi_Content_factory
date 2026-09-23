from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field

class ScheduleBase(BaseModel):
    platform: str
    scheduled_at: datetime
    status: Optional[str] = Field("Scheduled", description="Status of the schedule")

class ScheduleCreate(ScheduleBase):
    project_id: UUID

class ScheduleUpdate(BaseModel):
    platform: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    status: Optional[str] = None

class ScheduleResponse(ScheduleBase):
    id: UUID
    project_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ScheduleWithProjectResponse(ScheduleResponse):
    project_title: str
    
    class Config:
        from_attributes = True
